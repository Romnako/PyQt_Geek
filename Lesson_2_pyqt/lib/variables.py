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
DATA = 'bin'
PUBLIC_KEY = 'pubkey'

# маска разрешенных символов валидаторов полей
# https://habr.com/ru/post/123845/
RE_LOGIN_MASK='[a-zA-Z][a-zA-Z0-9]{1,25}'
RE_PASWD_MASK='[a-zA-Z][a-zA-Z0-9]{1,12}'
RE_IPV4_VALIDATOR='((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)'
RE_IPV6_VALIDATOR='((^|:)([0-9a-fA-F]{0,4})){1,8}$'
RE_PORT_VALIDATOR='[0-9]{0,5}'


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
PUBLIC_KEY_REQUEST = 'pubkey_need'

ERR_200 = '200:OK'
ERR400 = '400:Bad request'
ERR_USER_ALREADY_EXIST = 'Username already taken'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {RESPONSE: 400, ERROR: None}
RESPONSE_202 = {RESPONSE: 202, LIST_INFO: None}
RESPONSE_205 = {RESPONSE: 205}
RESPONSE_511 = {RESPONSE: 511, DATA: None}


# setting logging
LOG_LEVEL = logging.DEBUG
# LOG_LEVEL = logging.INFO
LOG_FORMATTER = '%(asctime)s %(levelname)s %(filename)s %(message)s'
