#!/usr/bin/python3
# -*- coding:utf8 -*-

# TODO: create a config.py file (not included in repo since a secret...)
# with
# CONSUMER_KEY = '<KEY>'
# CONSUMER_SECRET = '<SECRET>'

from config import CONSUMER_KEY, CONSUMER_SECRET

# NTP stuff
import socket
from socket import AF_INET, SOCK_DGRAM
import time
import struct

import requests
import base64
import json
from operator import itemgetter

from flask import Flask, request, make_response, jsonify

buf = ''

TOKEN_URL = 'https://api.vasttrafik.se/token'
API_BASE_URL = 'https://api.vasttrafik.se/bin/rest.exe/v2'


BERGSPRANGAREGATAN = '9022014001390001'
ENGDAHLSGATAN = '9022014002230002'

timeoutNTP = 1.0  # How much to wait for the NTP server's response in seconds

app = Flask("My-Local-Traffic-Planner")



# Fetches the time from NTP server.
# Source: http://blog.mattcrampton.com/post/88291892461/query-an-ntp-server-from-python
def getNTPTime(host="pool.ntp.org"):
    port = 123
    buf = 1024
    address = (host, port)
    msg = '\x1b' + 47 * '\0'

    # Reference time (in seconds since 1900-01-01 00:00:00)
    TIME1970 = 2208988800  # 1970-01-01 00:00:00

    # connect to server
    client = socket.socket(AF_INET, SOCK_DGRAM)
    client.settimeout(timeoutNTP)  # Do not wait too much to receive a response from the NTP server
    try:
        client.sendto(bytes(msg, "UTF-8"), address)
        msg, address = client.recvfrom(buf)
        t = struct.unpack("!12I", msg)[10]
        t -= TIME1970
    except:
        print("WARNING: Could not fetch time from NTP server! Using system time instead.")
        t = time.time()  # Fall back to the system time when no response from ntp server

    d = time.strptime(time.ctime(t), "%a %b %d %H:%M:%S %Y")
    return time.strftime("%Y-%m-%d", d), time.strftime("%H:%M", d)


def fetchtoken(key, secret):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode((key + ':' + secret).encode()).decode()
    }
    data = {'grant_type': 'client_credentials'}

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    obj = json.loads(response.content.decode('UTF-8'))
    return obj['access_token']


def get_departure_list(id_str, currentDate, currentTime):
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


def dothework(a):
    # Get the current time and date from an NTP server as the host might not have an RTC
    (currentDate, currentTime) = getNTPTime()
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
    for avgang in kandidatlista:
        str = avgang['rtTime'] + ' (' + avgang['time'] + ') ' + avgang['rtDate'] + ' ' + \
              avgang['name'] + ' ' + avgang['track'] + ' ' + avgang['direction']
        print(str)
        buf = buf + str + '</BR>'
    # app.run(debug=True)
    # app.run()



def respond(fullfilment):
    return make_response(jsonify({'fulfillmentText': fullfilment}))


@app.route('/departures', methods=['POST'])
def departures_handler():
    try:
        req = request.get_json(silent=True, force=True)
        print(json.dumps(req))

        location = req.get('queryResult').get('parameters').get('current-location')

        if location == 'home':
            return respond("This seems to work. Congrats Layf")
        elif location == 'work':
            return respond("At work? Well, are you sure it's time to leave already?")
        else:
            return respond("I am not sure where " + location + " is.")

    except Exception as e:
        print(e)
        return respond("Sorry, an error occurred. Please check the server logs.")


@app.route("/")
def hello():
    # return "simple test 3"
    dothework("hej")
    return buf


def main():
#    app.run()
    print("now I'm in console mode")
    dothework("hej")

token = fetchtoken(CONSUMER_KEY, CONSUMER_SECRET)

if __name__ == '__main__':
    main()
