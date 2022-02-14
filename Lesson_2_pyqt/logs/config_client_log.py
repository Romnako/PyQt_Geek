import sys
import os
import logging

sys.path.append('../')
from Lesson_2_pyqt.lib.variables import ENCODING, LOGGING_LEVEL

# CLIENT_FORMATTER = logging.Formatter(LOG_FORMATTER)
client_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

#Filename for logging
path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'client.log')

#Create log output streams
steam = logging.StreamHandler(sys.stderr)
steam.setFormatter(client_formatter)
steam.setLevel(logging.ERROR)
log_file = logging.FileHandler(path, encoding=ENCODING)
log_file.setFormatter(client_formatter)

#Create registration
logger  = logging.getLogger('client')
logger.addHandler(steam)
logger.addHandler(log_file)
logger.setLevel(LOGGING_LEVEL)

#debugging
if __name__ == '__main__':
    logger.critical('Critical error')
    logger.error('Error')
    logger.debug('Debug information')
    logger.info('Info message')




