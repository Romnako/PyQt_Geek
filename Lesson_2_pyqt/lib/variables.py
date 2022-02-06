import logging

DEFAULT_PORT = 7777
DEFAULT_IP = '127.0.0.1'
MAX_CONNECTIONS = 5
PACKAGE_LENGHT = 1024
ENCODING = 'utf-8'
SERVER_TIMEOUT = 1/2

SERVER_DATABASE = 'sqlite:///server_db.db3'

# Protocol JIM
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# Keys in protocol
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
AUTH = 'authenticate'
ALERT ='alert'
MSG = 'msg'
MSG_TEXT = 'msg_text'
LISTEN = 'listen'
EXIT = 'exit'
WHO = 'who'

CLIENT_LISTEN = False

ERR_200 = '200:OK'
ERR400 = '400:Bad request'
ERR_USER_ALREADY_EXIST = 'Username already taken'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {RESPONSE: 400, ERROR: None}

# setting logging
LOG_LEVEL = logging.DEBUG
# LOG_LEVEL = logging.INFO
LOG_FORMATTER = '%(asctime)s %(levelname)s %(filename)s %(message)s'
