# create a config.py file (not included in repo since a secret...) with
# CONSUMER_KEY = '<KEY>'
# CONSUMER_SECRET = '<SECRET>'


from flask import Flask
import logging.handlers
import sys
import os

from operator import itemgetter
from config import CONSUMER_KEY, CONSUMER_SECRET

from vasttrafik import *
import helpers

BERGSPRANGAREGATAN = '9022014001390001'
ENGDAHLSGATAN = '9022014002230002'

LOGFILE = 'mybus.log'

'''
TODO:
- SQUASH COMMITS!!
- try what happens with datetime object on pythonanywhere, different result??
- split "python_google_assistant.txt" into notes for "mybus" and (new) "googleAssistant". "myvasttrafik" should be reviewed and removed  
- review and delete test1.py (has code about ctrl-c, useful?)
- add unit tests
- support Ipad3 (safari) fullscreen. http://disq.us/p/1gdzfhm       
- dokument: use "private mode" to get black bar (this is how it was done before)
- update README.md
- add error handling if server fails to respond or "timeout"
    - this.readyState == 1 && this.status == 0 seems to be normal
    - 1/502, 2/502, 3/502, 4/502 has been seen... 
    - running to collect more data. Ignore all other states than 4? Only check if <>200 then. 
- add printout about URL to open when debugging on PC
- add "fail counter" (to visualise how well this fix works)
- "Missing rt-data 05:14 Buss 19" investigate if this should be highlighted (different color)
- update requirement.txt (check that no warnings from github)
- show busses in both directions
- verify or remove RPI support
- run pyCharm inspect code 
- check timediff calculation (has been "-1" midnight?)
- # PA file would be found "/home/qleisan/mysite/mybus/index.html"

- add links to good resources
https://flask.palletsprojects.com/en/1.0.x/
http://127.0.0.1:5000/index.html
http://127.0.0.1:5000/longlist
'''


app = Flask(__name__)

@app.route("/")
@app.route("/index.html")
def index():
    # "index.html" should be stored in the same directory as this file
    dir_name, filename = os.path.split(os.path.abspath(__file__))
    pathname = os.path.join(dir_name,'index.html')
    return open(pathname).read()


@app.route("/index.js")
def js():
    # "index.js" should be stored in the same directory as this file
    dir_name, filename = os.path.split(os.path.abspath(__file__))
    pathname = os.path.join(dir_name,'index.js')
    return open(pathname).read()


# TODO: this is not really part of the main application...more for debugging? Make new version with the new "API"
'''
@app.route("/longlist")
def longlist():
    global buf
    print("----------------------------------")
    t = helpers.getTimeNow_TZD_compensated()
    tstr = helpers.tuple2string(t)
    print(tstr)
    (cD, cT) = helpers.string2tuple(tstr)
    kandidatlista = helpers.getmybus(cD, cT)

    buf = '<h1>{}</h1>\n'.format(tstr)
    buf = buf + '<meta http-equiv="refresh" content="10">'
    for avgang in kandidatlista:
        str = avgang['rtTime'] + ' (' + avgang['time'] + ') ' + avgang['rtDate'] + ' ' + \
              avgang['name'] + ' ' + avgang['track'] + ' ' + avgang['direction']
        logger.info(str)
        buf = buf + str + '</BR>'
    return buf
'''

@app.route("/ajax")
def ajax():
    print("ajax------------------------")
    #TODO: why is this formatted XXXX-XX-XX YY:YY ?? (this is what I want but how safe?)
    now = datetime.now(timezone('Europe/Stockholm'))
    print(now)
    b = a.getDepartures(BERGSPRANGAREGATAN, now)
    c = a.getDepartures(ENGDAHLSGATAN, now)
    mylist = b.search("18", "A")
    mylist.extend(b.search("52", "A"))
    mylist.extend(c.search("19", "A"))
    # TODO: dag/tid can be removed and only use datetime object in dict and here
    mylist.sort(key=itemgetter('dag', 'tid'))
    pprint(mylist)

    l = []
    for idx, avgang in enumerate(mylist):
        #gives -1 as soon as negative.
        result=int((avgang['y_aware']-now).total_seconds()/60)
        l.append((avgang['linje'], result))
        if idx == 2:
            break

    outDict = {
        'timetext': str(datetime(now.year,
                                 now.month,
                                 now.day,
                                 now.hour,
                                 now.minute,
                                 now.second)),
        'table': l,
        'colors': helpers.getcolor(now)
    }
    pprint(outDict)
    json_data = json.dumps(outDict, sort_keys=True)
    return json_data


# debugging info
print("__name__ = {}".format(__name__))
#if __name__ == '__main__':
if True:
    logging.basicConfig(filename=LOGFILE,
                        level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(module)s %(lineno)d - %(message)s",
                        filemode='w')

    logger = logging.getLogger()
    print("Logging to file '{}'".format(LOGFILE))
    # make sure unhandled exceptions are logged
    sys.excepthook = helpers.handle_exception

    logger.setLevel(logging.INFO)
    logger.info("Application staring")

    hwplatform = helpers.getHWplatform()
    a = Server(CONSUMER_KEY, CONSUMER_SECRET)

    if hwplatform == 'pc':
        logger.info("Running on pc")
        # app.run() i a blocking call!
        ##app.run(host='0.0.0.0')  # publicly available
        app.run(debug=True)

        # will only get here if app.run() is commented out
        print("Flask server not run now during development")

    elif hwplatform == 'rpi':
        logger.info("Running on rpi")
        app.run()
    else:
        logger.info("Running on cloud")
        # cloud starts flask automatically
