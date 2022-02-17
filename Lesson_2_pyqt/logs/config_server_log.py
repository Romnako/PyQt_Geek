import sys
import os

import logging.handlers
import logging
# sys.path.append('../')
from Lesson_2_pyqt.lib.variables import LOGGING_LEVEL, ENCODING

server_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'server_log')
steam = logging.StreamHandler(sys.stderr)
steam.setFormatter(server_formatter)
steam.setLevel(logging.INFO)
log_file = logging.handlers.TimedRotatingFileHandler(path, encoding=ENCODING, interval=1, when='D')
log_file.setFormatter(server_formatter)
logger = logging.getLogger('server')
logger.addHandler(log_file)
logger.addHandler(steam)
logger.setLevel(LOGGING_LEVEL)


if __name__ == '__main__':
    logger.critical('Critical error')
    logger.error('Error')
    logger.debug('Debug information')
    logger.info('Info message')