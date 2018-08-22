# vasttrafik stuff
import base64
import requests
import json

# other
import platform
import logging
from datetime import datetime
from pytz import timezone


# defines
TOKEN_URL = 'https://api.vasttrafik.se/token'
API_BASE_URL = 'https://api.vasttrafik.se/bin/rest.exe/v2'


def getTime():
    print("datetime:")
    swe_time = datetime.now(timezone('Europe/Stockholm'))
    dr2 = swe_time.strftime('%Y-%m-%d'), swe_time.strftime('%H:%M')
    print(dr2)
    return dr2


def fetchtoken(key, secret):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode((key + ':' + secret).encode()).decode()
    }
    data = {'grant_type': 'client_credentials'}

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    obj = json.loads(response.content.decode('UTF-8'))
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


print("XLEISAN - helpers outside scope")
