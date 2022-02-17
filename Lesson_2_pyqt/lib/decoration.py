import sys
import socket
import logging
import Lesson_2_pyqt.logs.config_server_log
import Lesson_2_pyqt.logs.config_client_log
import inspect

if sys.argv[0].rfind('server') > 0:
    # имя скрипта содержит server, значит это сервер
    DEC_LOGGER = logging.getLogger('server')
else:
    # =-1, не найдено, значит клент
    DEC_LOGGER = logging.getLogger('client')


def log(func):
    def log_saver(*args, **kwargs):
        ret_log_saver = func(*args, **kwargs)
        DEC_LOGGER.debug(f'Вызов функции:{func.__module__}.{func.__name__}:({args}, {kwargs})'
                         f' из {inspect.stack()[1][3]}')
        return ret_log_saver
    return log_saver