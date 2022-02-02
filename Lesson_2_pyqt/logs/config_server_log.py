import sys
import os
from datetime import datetime
import logging.handlers

sys.path.append('../')
from lib.variables import LOG_LEVEL, ENCODING, LOG_FORMATTER

SERVER_FORMATTER = logging.Formatter(LOG_FORMATTER)

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.log')

LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encoding=ENCODING, interval=1, when='midnight')
LOG_FILE.setFormatter(SERVER_FORMATTER)

LOGGER = logging.getLogger('server')
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOG_LEVEL)


if __name__ == '__main__':
    LOGGER.critical('Critical error')
    LOGGER.error('Error')
    LOGGER.debug('Debug information')
    LOGGER.info('Info message')