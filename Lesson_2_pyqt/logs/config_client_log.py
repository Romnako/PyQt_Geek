import sys
import os
from datetime import datetime
import logging

sys.path.append('../')
from lib.variables import LOG_LEVEL, ENCODING, LOG_FORMATTER

CLIENT_FORMATTER = logging.Formatter(LOG_FORMATTER)

#Filename for logging
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.log')

#Create log output streams
LOG_FILE = logging.FileHandler(PATH, encoding=ENCODING)
LOG_FILE.setFormatter(CLIENT_FORMATTER)

#Create registration
LOGGER = logging.getLogger('client')
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOG_LEVEL)

#debugging
if __name__ == '__main__':
    LOGGER.critical('Critical error')
    LOGGER.error('Error')
    LOGGER.debug('Debug information')
    LOGGER.info('Info message')




