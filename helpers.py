# other
import platform
import logging

from datetime import time

logger = logging.getLogger(__name__)


def getcolor(t):
    d2 = time(7, 30, 0)
    d3 = time(22, 00, 0)
    if d2 < t.time() < d3:
        return 'white', 'black', 'blue'
    else:
        return 'black', 'DimGrey', 'DimGrey'

'''
- need date/time with seconds for webpage header (timezone/daylight compensated)
- need to calculate timediff in minutes between date/time in yymmdd-HH:MM format
'''

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
