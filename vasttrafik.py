import base64
import requests
import json
from datetime import datetime
from pytz import timezone
import logging
from pprint import pprint

# defines
TOKEN_URL = 'https://api.vasttrafik.se/token'
API_BASE_URL = 'https://api.vasttrafik.se/bin/rest.exe/v2'

'''
intended use (from main application with the "business logic")
- instatiate Server class (should only have one, token handling is done in the background)
- "getDepartures" (others Server class methods are "private") to query
  what busses arrive at a stop. An object is returned that contain the info
- query this object "Departures" using search one or multiple time (different busses)
  get a list of "info dictionaries in good format". Append to a list
- possibly repeat for another busstop
- sort the list and return the json info requested by AJAX call

'''

logger = logging.getLogger(__name__)


class Departures:
    # TODO: shouldn't be able to instantiate this yourself
    def __init__(self, data):
        self.data=data

    #TODO: search by bus number and track, return "custom" list of tuples
    #this way any changes in vasttrafik data format will not propagate (as much)
    #as otherwise...
    def search(self, busNo, track):
        kandidatlista = []
        for avgang in self.data:
            if (avgang['sname'] == busNo) and avgang['track'] == track:
                missing = object()
                tid = avgang.get('rtTime', missing)
                # TODO: refactor names etc.
                if tid is missing:
                    print('Missing rt-data ' + avgang['time'], avgang['name'])
                    mytime = avgang['time']
                    mydate = avgang['date']
                    realtime = False
                else:
                    mytime = avgang['rtTime']
                    mydate = avgang['rtDate']
                    realtime = True
                y = datetime(*tuple(map(int, mydate.split('-') + mytime.split(':'))))
                tz = timezone("Europe/Stockholm")
                y_aware = tz.localize(y)
                mydict = {"linje": avgang['sname'],
                          "dag": mydate,                # TODO remove
                          "tid": mytime,                # TODO remove
                          "realtid": realtime,
                          "y_aware": y_aware
                          }
                kandidatlista.append(mydict)
        return kandidatlista


class Server:
    def __init__(self, CONSUMER_KEY, CONSUMER_SECRET):
        self.consumer_key = CONSUMER_KEY
        self.consumer_secret = CONSUMER_SECRET
        self.fetchtoken()

    # "private"
    def fetchtoken(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' +
            base64.b64encode((self.consumer_key + ':'
                              + self.consumer_secret).encode()).decode()
        }
        data = {'grant_type': 'client_credentials'}

        response = requests.post(TOKEN_URL, data=data, headers=headers)
        obj = json.loads(response.content.decode('UTF-8'))
        #pprint(obj)
        self.token = obj['access_token']
        logger.info("Getting token: {}".format(self.token))

    # "private"
    # TODO: this way busses that are on the "ongoing" minute are displayed (as "-1")
    def requestcall(self, id_str, t):
        res = requests.get('https://api.vasttrafik.se/bin/rest.exe/v2/departureBoard?id=' + id_str +
                           f"&date={t.year:04d}{t.month:02d}{t.day:02d}&time={t.hour:02d}%3A{t.minute:02d}" +
                           '&format=json', headers={'Authorization': 'Bearer ' + self.token})
        return res

    def getDepartures(self, busstop, t):
        res = self.requestcall(busstop, t)
        if res.status_code == 200:
            #pprint(res.text)
            # TODO: Improve! This is a workaround for observed communication error
            '''
            ('{"DepartureBoard":{  '
             '"noNamespaceSchemaLocation":"http://api.vasttrafik.se/v1/.xsd",  "error":"S1 '
             'instableCommunication",  "errorText":"The desired connection to the server '
             'could not be established or was not stable.",  "$":""  }}')	
            '''
            # TODO: fixme!
            if 'Departure' in json.loads(res.text)['DepartureBoard']:
                return Departures(json.loads(res.text)['DepartureBoard']['Departure'])

            else:
                pprint(json.loads(res.text)['DepartureBoard'])
                logger.critical("SERVER ERROR FOUND (DEBUG)")
                logger.critical(json.loads(res.text)['DepartureBoard'])
                return Departures([])
        else:
            # 2018-09-16 09:17:54,198 WARNING flask_app 131 - res.status_code = '401'
            logger.warning("res.status_code = '{}'".format(res.status_code))
            self.fetchtoken()
            res = self.getDepartures(busstop, t)
            if res.status_code == 200:
                logger.info("worked this time")
                # TODO: this call might cause the same problem as above (but less frequent)
                return Departures(json.loads(res.text)['DepartureBoard']['Departure'])
            else:
                raise Exception('Error: ' + str(res.status_code) + '|' + str(res.content))
