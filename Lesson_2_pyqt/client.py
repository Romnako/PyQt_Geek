import sys
import json
import time
import re
import logging
import threading
from Lesson_2_pyqt.lib.variables import *
from Lesson_2_pyqt.lib.utils import server_settings, get_message, send_message
from Lesson_2_pyqt.lib.errors import ReqFieldMissingError, ServerError, IncorrectDataReceivedError
from Lesson_2_pyqt.lib.metaclasses import ClientMaker
import socket

CLIENT_LOGGER = logging.getLogger('client')


class ClientSender(threading.Thread, metaclass=ClientMaker):
    '''
    The class for generating and sending messages to the server and interacting with the user.
    '''
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock =sock
        super.__init__()

    def create_exit_message(self):
        '''
        The function creates a dictionary with an exit message
        :return:
        '''
        out = {ACTION: EXIT, TIME: time.time(), ACCOUNT_NAME: self.account_name}
        CLIENT_LOGGER.info(f'exit{out}')
        return out

    def create_message(self):
        '''
        The function requests the text of the message
        :return: the text of the message
        '''
        to_user = input('Who is the recipient of the message?')
        message = input('Input message for send: ')
        message_dict = {ACTION: MSG, TIME: time.time(), SENDER: self.account_name, DESTINATION: to_user,
                        MSG_TEXT: message}
        CLIENT_LOGGER.debug(f'Message dictionary generated: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            CLIENT_LOGGER.info(f'Message sent to user {to_user}')
        except:
            CLIENT_LOGGER.error('Lost connection to server.')
            sys.exit(1)

    def create_who_message(self):
        '''
        Generates a list of clients
        :return:
        '''
        message_dict = {ACTION: WHO, TIME: time.time(), SENDER: self.account_name, DESTINATION: self.account_name,
                        MSG_TEXT: None}
        CLIENT_LOGGER.debug(f'The message dictionary is generated: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            CLIENT_LOGGER.error('Lost connection to server.')
            sys.exit(1)

    def run(self):
            '''
            User interaction function, request commands, send messages
            :return:
            '''
        while True:
            self.print_help()
            command = input('Input command: ').lower()
            if command == 'message' or command == 'm':
                self.create_message()
            elif command == 'help' or command == 'h':
                self.print_help()
            elif command == 'who' or command == 'w':
                CLIENT_LOGGER.debug(f"Server users query:")
                self.create_who_message()
            elif command == 'exit' or command == 'e' or command == 'q':
                send_message(self.sock, self.create_exit_message())
                print('Terminating the connection...')
                CLIENT_LOGGER.info("Completion of work on the user's command.")
                time.sleep(0.5)
                break
            else:
                print('Command not recognized, please try again. help - display supported commands.')

    def print_help(self):
        """Function for displaying help on usage"""
        print('Supported commands:')
        print('message (m) - send a message. To and text will be requested separately.')
        print('who (w) - name users')
        print('help (h) - display command prompts')
        print('exit (q или e)- exit')

class ClientReader(threading.Thread, metaclass=ClientMaker):
    '''
    The class that receives messages from the server. Receives messages, outputs to the console.
    '''
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        '''
        Function - handler of other users' messages coming from the server
        :return:
        '''
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MSG and SENDER in message and DESTINATION in message
                    and MSG_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'Message received from user {message[SENDER]}:{message[MSG_TEXT]}')
                    CLIENT_LOGGER.info(f'Message received from user {message[SENDER]}:{message[MSG_TEXT]}')
                else:
                    CLIENT_LOGGER.error(f'Invalid message received from server: {message}')
            except IncorrectDataReceivedError:
                CLIENT_LOGGER.error(f'Failed to decode received message.')
            except(OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                CLIENT_LOGGER.critical(f'Lost connection to server.')
                break


def create_presence(account_name='Guest'):
    '''

    :param account_name:The function generates a client presence request
    :return:
    '''
    out = {ACTION:PRESENCE, TIME: time.time(), USER: {ACCOUNT_NAME: account_name}}
    CLIENT_LOGGER.debug(f'{PRESENCE} message generated for user {account_name}')
    return out

def process_handler(message):
    '''

    :param message:The function parses the server response
    :return:
    '''
    CLIENT_LOGGER.debug(f'Parsing the welcome message from the server: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            CLIENT_LOGGER.debug(f"{message[RESPONSE]} contains {ERR200}")
            return message[MSG]
        elif message[RESPONSE] == ERR400:
            CLIENT_LOGGER.debug(f"{message[RESPONSE]} contains {ERR400}")
            raise ServerError(f"{ERR400}: {message[ERROR]}")
    raise ReqFieldMissingError(RESPONSE)


def get_user():
    '''

    :return: the function returns the username
    '''
    while True:
        account = input('Enter username: ')
        if not re.match(r'[A-Za-z]', account) or len(account) > 25 or len(account) < 3:
            CLIENT_LOGGER.error(f'Invalid username: {account}')
            print('Username must be between 3 and 25 Latin characters')
        elif account.lower().strip() == 'guest':
            CLIENT_LOGGER.error(f'Invalid username: {account}')
            print('Invalid username')
        else:
            break
    return account


def create_action(account_name, action, msg=None):
    '''

    :param account_name: The function returns a dictionary with the message text
    :param action:
    :param msg:
    :return:
    '''
    out = {ACTION: action, TIME: time.time(), USER: {ACCOUNT_NAME: account_name}, MSG: msg}
    CLIENT_LOGGER.debug(f'{action} message generated for user {account_name}')
    CLIENT_LOGGER.debug(f"{out}")
    return out


def start_client():
    srv_settings = server_settings()
    server_address = srv_settings[0]
    server_port = srv_settings[1]
    client_listen = srv_settings[2]
    print(f'Start client on: {server_address}:{server_port}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence())
        answer = process_handler(get_message(transport))
        CLIENT_LOGGER.info(f'Connection to the server {server_address}:{server_port}. Answer: {answer}')
        print(f'Server connection {server_address}:{server_port} \n {answer}')

        account_name = get_user()
        CLIENT_LOGGER.info(f'Guest logged in as {account_name}')
        CLIENT_LOGGER.debug(
            f'sending {AUTH} message to server {server_address}:{server_port} from user={account_name}')
        message_to_server = create_action(account_name, action=AUTH, msg=None)
        send_message(transport, message_to_server)
        try:
            answer = process_handler(get_message(transport))
            print(answer)
        except(ValueError, json.JSONDecodeError):
            print(answer)
            CLIENT_LOGGER.error(f'{ERR 400}. Failed to decode message from server')
            print(f'{ERR 400}. Failed to decode message from server')

    except json.JSONDecodeError:
        CLIENT_LOGGER.error(f'Failed to decode JSON string')
        print(f'Failed to decode JSON string')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'Connection error: {error.text}')
        print(f'Connection error: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'The server response does not contain the required field {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Failed to connect to server {server_address}:{server_port}')
        sys.exit(1)
    else:
        '''start the client process of receiving messages '''
        receiver = ClientReader(account_name, transport)
        receiver.daemon = True
        receiver.start()

        ''' Start sending messages and interacting with the user.'''
        user_interface = ClientSender(account_name, transport)
        user_interface.daemon = True
        user_interface.start()
        CLIENT_LOGGER.debug('Process running')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    start_client()

















