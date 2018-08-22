#!/usr/bin/python3
# -*- coding:utf8 -*-

# TODO: automate this - if no file exist create one and inform user to fill in the blanks
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

buf = ''


BERGSPRANGAREGATAN = '9022014001390001'
ENGDAHLSGATAN = '9022014002230002'

LOGFILE = 'mybus.log'

app = Flask("My-Local-Traffic-Planner")


def get_departure_list(id_str, currentDate, currentTime):
    global token
    headers = {
        'Authorization': 'Bearer ' + token
    }

    datetimestr = '&date=' + currentDate.replace('-','') + '&time={}%3A{}'.format(*currentTime.split(':'))

    res = requests.get('https://api.vasttrafik.se/bin/rest.exe/v2/departureBoard?id=' + id_str +
                       datetimestr + '&format=json', headers=headers)

    if res.status_code == 200:
        return json.loads(res.text)['DepartureBoard']['Departure']
    else:
        raise Exception('Error: ' + str(res.status_code) + str(res.content))


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


@app.route("/")
def hello():
    # return "simple test"
    print("XLEISAN ----------------------------------")
    getmybus()
    return buf


def getmybus():
    # Get the current time and date from an NTP server as the host might not have an RTC
    (currentDate, currentTime) = helpers.getTime()
    print(currentDate, currentTime)

    kandidatlista = []
    debug = False

    if debug  == True:
        kandidatlista = json.load(open('kandidatlista.json'))
        #pprint.pprint(kandidatlista)
        #quit(0)
    else:
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
    global buf
    buf = ''
    for avgang in kandidatlista:
        str = avgang['rtTime'] + ' (' + avgang['time'] + ') ' + avgang['rtDate'] + ' ' + \
              avgang['name'] + ' ' + avgang['track'] + ' ' + avgang['direction']
        logger.info(str)
        logger.info("is this written to error log also?")
        buf = buf + str + '</BR>'


def handle_exception(exc_type, exc_value, exc_traceback):
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    print("Uncaught exception - check log")


def main():
    logging.basicConfig(filename=LOGFILE,
                        level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(module)s %(lineno)d - %(message)s",
                        filemode='w')
    global logger   # todo: consider removing global and using getlogger() in evecy function
    logger = logging.getLogger()
    print("Logging to file '{}'".format(LOGFILE))
    # make sure unhandled exceptions are logged
    sys.excepthook = handle_exception

    logger.setLevel(logging.INFO)
    logger.info("Application staring")
    (currentDate, currentTime) = helpers.getTime()
    logger.info("Timezone and Daylightsavings adjusted date/time: {} {}".format(currentDate, currentTime))

    hwplatform = helpers.getHWplatform()

    global token # todo: consider refactoring
    token = helpers.fetchtoken(CONSUMER_KEY, CONSUMER_SECRET)
    logger.info("Getting token: {}".format(token))

    if hwplatform == 'pc':
        logger.info("Running on pc")
        # app.run()
        # app.run(debug=True)
        print("Flask server not run now now during development")
        getmybus()
    elif hwplatform == 'rpi':
        # my RPI doesn't support HTTPS now
        logger.info("Running on rpi")
        app.run()
    else:
        logger.info("Running on cloud")
        # cloud starts flask automatically


print("XLEISAN - outer scope")
print("__name__ = {}".format(__name__))

# if __name__ == '__main__':
if True:
    print("XLEISAN - Calling main")
    main()
