# vasttrafik stuff
import base64
import requests
import json

# other
import platform
import logging
from datetime import datetime
from datetime import time
from pytz import timezone

from pprint import pprint

# defines
TOKEN_URL = 'https://api.vasttrafik.se/token'
API_BASE_URL = 'https://api.vasttrafik.se/bin/rest.exe/v2'

logger = logging.getLogger(__name__)


mypagetemplate = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="10">
    <title>WIP</title>
    <style>
        body {{background-color: {0};}}
    </style>
</head>
<body>
<h1 style="color:{1};font-size:400%;">{2}</h1>
<h1 style="color:{3};font-size:1200%;">[{4}] {5} min</h1>
<h1 style="color:{3};font-size:1200%;">[{6}] {7} min</h1>
<h1 style="color:{3};font-size:1200%;">[{8}] {9} min</h1>
<!--
<p>12:03+2</p>
<div style="font-size:72">Score</div>
-->
</body>
</html>
"""


def getcolor(t):
    d1 = datetime(*t)
    # print(d1.time())
    d2 = time(07, 30, 0)
    d3 = time(22, 00, 0)
    if d2 < d1.time() < d3:
        return 'white', 'black', 'blue'
    else:
        return 'black', 'DimGrey', 'DimGrey'


def mypage(bgcolor, col1, a, col2,  l):
    print(l)
    if l:
        # list is not empty - assume ok... TODO: refactor
        return mypagetemplate.format(bgcolor, col1, a, col2,
                                     l[0][0], l[0][1],
                                     l[1][0], l[1][1],
                                     l[2][0], l[2][1])
    else:
        logger.warning("empty list to mypage()")
        return mypagetemplate.format(bgcolor, col1, a, col2, '??', '??', '??', '??', '??', '??')


'''
- need date/time with seconds for webpage header (timezone/daylight compensated)
- need to calculate timediff in minutes between date/time in yymmdd-HH:MM format
'''


def getTimeNow_TZD_compensated():
    # rename: TZ = TimeZone, D = daylight...
    swe_time = datetime.now(timezone('Europe/Stockholm'))
    # old code: dr2 = swe_time.strftime('%Y-%m-%d'), swe_time.strftime('%H:%M:%S')
    return swe_time.year, swe_time.month, swe_time.day, swe_time.hour, swe_time.minute, swe_time.second


def tuple2string(t):
    # return "{}-{}-{} {}:{}:{}".format(*tuple)
    return "{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5])


def string2tuple(s):
    a = str(s).split(' ')
    return (a[0], a[1][:-3])


def getminutesdiff(tuple, date, time):
    d1 = datetime(*tuple)
    # print("d1 = '{}'".format(d1))
    d1 = datetime(d1.year, d1.month, d1.day, d1.hour, d1.minute)
    # print("seconds set to zero. d1 = '{}'".format(d1))
    stringtoparse = date + '|' + time
    # print(stringtoparse)
    d2 = datetime.strptime(stringtoparse, "%Y-%m-%d|%H:%M")
    # print("d2 = '{}'".format(d2))
    diff = d2-d1
    # print(diff)
    # print(diff.seconds//60)
    return diff.seconds//60


def fetchtoken(key, secret):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode((key + ':' + secret).encode()).decode()
    }
    data = {'grant_type': 'client_credentials'}

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    obj = json.loads(response.content.decode('UTF-8'))
    pprint(obj)
    return obj['access_token']


def getHWplatform():
    logger = logging.getLogger()
    env = platform.platform()
    logger.info("platform.platform() = '{}'".format(env))
    if 'Windows' in env:
        return 'pc'
    elif 'armv7l' in env:
        return 'rpi'
    elif 'aws' in env:
        return 'cloud'
    else:
        logger.critical("Running on unknown platform. Aborting")
        exit(1)


def handle_exception(exc_type, exc_value, exc_traceback):
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    print("Uncaught exception - check log")


print("XLEISAN - helpers outside scope")
