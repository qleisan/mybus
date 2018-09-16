# create a config.py file (not included in repo since a secret...) with
# CONSUMER_KEY = '<KEY>'
# CONSUMER_SECRET = '<SECRET>'
from config import CONSUMER_KEY, CONSUMER_SECRET

import helpers
import requests
import json
from operator import itemgetter
from flask import Flask, request, make_response, jsonify
import logging.handlers
import sys

from pprint import pprint

buf = ''


BERGSPRANGAREGATAN = '9022014001390001'
ENGDAHLSGATAN = '9022014002230002'

LOGFILE = 'mybus.log'

app = Flask("My-Local-Traffic-Planner")


###################### code for google assistant #######################

def respond(fullfilment):
    return make_response(jsonify({'fulfillmentText': fullfilment}))


@app.route('/departures', methods=['POST'])
def departures_handler():
    try:
        req = request.get_json(silent=True, force=True)
        print(json.dumps(req))

        location = req.get('queryResult').get('parameters').get('current-location')

        if location == 'home':
            return respond("Hardcoded test - next bus is 19 in 5 minutes")
        elif location == 'work':
            return respond("At work? Well, are you sure it's time to leave already?")
        else:
            return respond("I am not sure where " + location + " is.")

    except Exception as e:
        print(e)
        return respond("Sorry, an error occurred. Please check the server logs.")

#########################################################################

###################### Flask #######################
@app.route("/")
def longlist():
    global buf
    print("----------------------------------")
    t = helpers.getTimeNow_TZD_compensated()
    tstr = helpers.tuple2string(t)
    print(tstr)
    (cD, cT) = helpers.string2tuple(tstr)
    kandidatlista = getmybus(cD, cT)

    buf = '<h1>{}</h1>\n'.format(tstr)
    buf = buf + '<meta http-equiv="refresh" content="10">'
    for avgang in kandidatlista:
        str = avgang['rtTime'] + ' (' + avgang['time'] + ') ' + avgang['rtDate'] + ' ' + \
              avgang['name'] + ' ' + avgang['track'] + ' ' + avgang['direction']
        logger.info(str)
        logger.info("is this written to error log also?")
        buf = buf + str + '</BR>'
    return buf

@app.route("/wip")
def wip():
    print("WIP----------------------------------")
    t = helpers.getTimeNow_TZD_compensated()
    tstr = helpers.tuple2string(t)
    print(tstr)
    (cD, cT) = helpers.string2tuple(tstr)
    kandidatlista = getmybus(cD, cT)

    # pprint(kandidatlista)
    l = list()
    for idx, avgang in enumerate(kandidatlista):
        print(idx, avgang['rtTime'])
        result = helpers.getminutesdiff(t, avgang['rtDate'], avgang['rtTime'])
        l.append((avgang['sname'], result))
        if idx == 2:
            break
    pprint(l)
    return helpers.mypage(tstr, l)
###################################################


def requestcall(id_str, currentDate, currentTime):
    global token
    headers = {
        'Authorization': 'Bearer ' + token
    }

    datetimestr = '&date=' + currentDate.replace('-','') + '&time={}%3A{}'.format(*currentTime.split(':'))

    res = requests.get('https://api.vasttrafik.se/bin/rest.exe/v2/departureBoard?id=' + id_str +
                       datetimestr + '&format=json', headers=headers)
    return res


def get_departure_list(id_str, currentDate, currentTime):
    global token
    res = requestcall(id_str, currentDate, currentTime)
    if res.status_code == 200:
        # pprint(res.text)
        # TODO: Improve! This is a workaround for observed communication error
        '''
        ('{"DepartureBoard":{  '
         '"noNamespaceSchemaLocation":"http://api.vasttrafik.se/v1/.xsd",  "error":"S1 '
         'instableCommunication",  "errorText":"The desired connection to the server '
         'could not be established or was not stable.",  "$":""  }}')	
        '''
        # TODO: fixme!
        if 'Departure' in json.loads(res.text)['DepartureBoard']:
            return json.loads(res.text)['DepartureBoard']['Departure']
        else:
            pprint(json.loads(res.text)['DepartureBoard'])
            logger.critical("SERVER ERROR FOUND (DEBUG)")
            logger.critical(json.loads(res.text)['DepartureBoard'])
            return []
    else:
        logger.warning("res.status_code = '{}'".format(res.status_code))
        token = helpers.fetchtoken(CONSUMER_KEY, CONSUMER_SECRET)
        res = requestcall(id_str, currentDate, currentTime)
        if res.status_code == 200:
            logger.info("worked this time")
            # TODO: this call might cause the same problem as above (but less frequent)
            return json.loads(res.text)['DepartureBoard']['Departure']
        else:
            raise Exception('Error: ' + str(res.status_code) + '|' + str(res.content))


def getmybus(currentDate, currentTime):
    kandidatlista = []
    lista = get_departure_list(BERGSPRANGAREGATAN, currentDate, currentTime)
    for avgang in lista:
        if (avgang['sname'] == '18' or avgang['sname'] == '52') and avgang['track'] == 'A':
            kandidatlista.append(avgang)

    lista = get_departure_list(ENGDAHLSGATAN, currentDate, currentTime)
    for avgang in lista:
        if avgang['sname'] == '19' and avgang['track'] == 'A':
            kandidatlista.append(avgang)

    # with open('kandidatlista.json', 'w') as outfile:
    #     json.dump(kandidatlista, outfile)

    missing = object()
    for avgang in kandidatlista:
        tid = avgang.get('rtTime', missing)
        if tid is missing:
            print('Missing rt-data ' + avgang['time'], avgang['name'])
            avgang['rtTime'] = avgang['time']
            avgang['rtDate'] = avgang['date']

    kandidatlista.sort(key=itemgetter('rtDate', 'rtTime'))
    return kandidatlista




def main():
    logging.basicConfig(filename=LOGFILE,
                        level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(module)s %(lineno)d - %(message)s",
                        filemode='w')
    global logger   # todo: consider removing global and using getlogger() in every function
    logger = logging.getLogger()
    print("Logging to file '{}'".format(LOGFILE))
    # make sure unhandled exceptions are logged
    sys.excepthook = helpers.handle_exception

    logger.setLevel(logging.INFO)
    logger.info("Application staring")
    hwplatform = helpers.getHWplatform()

    global token # todo: consider refactoring
    token = helpers.fetchtoken(CONSUMER_KEY, CONSUMER_SECRET)
    logger.info("Getting token: {}".format(token))

    if hwplatform == 'pc':
        logger.info("Running on pc")
        # app.run() i a blocking call!
        app.run(host='0.0.0.0')  # publicly available
        ## app.run(debug=True)

        # will only get here if app.run() is commented out
        print("Flask server not run now during development")
        print(wip())    # print webpage

    elif hwplatform == 'rpi':
        # my RPI doesn't support HTTPS now
        logger.info("Running on rpi")
        app.run()
    else:
        logger.info("Running on cloud")
        # cloud starts flask automatically

# debugging info
print("XLEISAN - outer scope")
print("__name__ = {}".format(__name__))
# if __name__ == '__main__':
if True:
    main()
