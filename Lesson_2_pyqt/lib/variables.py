import logging

DEFAULT_PORT = 7777
DEFAULT_IP = '127.0.0.1'
MAX_CONNECTIONS = 5
PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'
LOGGING_LEVEL = logging.DEBUG
SERVER_CONFIG = 'server.ini'
SERVER_DATABASE = 'sqlite:///server_db.db3'
SERVER_TIMEOUT = 1/2
POOL_RECYCLE = 7200

CLIENT_LISTEN = False

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
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
LISTEN = 'listen'
EXIT = 'exit'
WHO = 'who'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'


ERR_200 = '200:OK'
ERR400 = '400:Bad request'
ERR_USER_ALREADY_EXIST = 'Username already taken'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {RESPONSE: 400, ERROR: None}
RESPONSE_202 = {RESPONSE: 202, LIST_INFO: None}

# setting logging
LOG_LEVEL = logging.DEBUG
# LOG_LEVEL = logging.INFO
LOG_FORMATTER = '%(asctime)s %(levelname)s %(filename)s %(message)s'
