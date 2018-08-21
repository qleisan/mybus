# NTP stuff
import socket
from socket import AF_INET, SOCK_DGRAM
import time
import struct

# vasttrafik stuff
import base64
import requests
import json

# other
import platform
import logging

# defines
timeoutNTP = 1.0  # How much to wait for the NTP server's response in seconds
TOKEN_URL = 'https://api.vasttrafik.se/token'
API_BASE_URL = 'https://api.vasttrafik.se/bin/rest.exe/v2'


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
    # TODO: fixme!
    # print("NTP disabled for now, code doesn't work on pythonanywhere")
    # '''
    try:
        client.sendto(bytes(msg, "UTF-8"), address)
        msg, address = client.recvfrom(buf)
        t = struct.unpack("!12I", msg)[10]
        t -= TIME1970
    except:
        print("WARNING: Could not fetch time from NTP server! Using system time instead.")
        t = time.time()  # Fall back to the system time when no response from ntp server
    #'''
    # TODO - temporary solution
    # t = time.time()
    d = time.strptime(time.ctime(t), "%a %b %d %H:%M:%S %Y")
    return time.strftime("%Y-%m-%d", d), time.strftime("%H:%M", d)


def getTime():
    if hwplatform == "cloud":
        pass
    else:
        pass


# --------------------------------------------------------------------------------------------------------


def fetchtoken(key, secret):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode((key + ':' + secret).encode()).decode()
    }
    data = {'grant_type': 'client_credentials'}

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    obj = json.loads(response.content.decode('UTF-8'))
    return obj['access_token']


# --------------------------------------------------------------------------------------------------------


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
