import argparse
import sys
import json
import time
import re
import logging
import threading
import socket
import Lesson_2_pyqt.logs.config_client_log
from Lesson_2_pyqt.logs.decoration_log import log
from Lesson_2_pyqt.lib.variables import *
from Lesson_2_pyqt.lib.utils import server_settings, get_message, send_message
from Lesson_2_pyqt.lib.errors import ReqFieldMissingError, ServerError, IncorrectDataReceivedError
from Lesson_2_pyqt.lib.metaclasses import ClientMaker
from client_db import ClientDatabase

client_logger = logging.getLogger('client')

sock_lock = threading.Lock()
database_lock = threading.Lock()


class ClientSender(threading.Thread, metaclass=ClientMaker):
    '''
    The class for generating and sending messages to the server and interacting with the user.
    '''
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock =sock
        self.database = database
        super.__init__()

    def create_exit_message(self,):
        '''
        The function creates a dictionary with an exit message
        :return:
        '''
        out = {ACTION: EXIT, TIME: time.time(), ACCOUNT_NAME: self.account_name}
        client_logger.info(f'exit{out}')
        return out

    def create_message(self):
        '''
        The function requests the text of the message
        :return: the text of the message
        '''
        to_user = input('Who is the recipient of the message?')
        message = input('Input message for send: ')
        message_dict = {ACTION: MESSAGE, TIME: time.time(), SENDER: self.account_name, DESTINATION: to_user,
                        MESSAGE_TEXT: message}
        client_logger.debug(f'Message dictionary generated: {message_dict}')
        with database_lock:
            self.database.save_message(self.account_name, recipient, message)
        with sock_lock:
            try:
                client_logger.info(f'Message send to user: {recipient} | {message_dict}')
                send_message(self.sock, message_dict)
                # client_logger.info(f'Message sent to user {to_user}')
            except OSError as err:
                if err.errno:
                    client_logger.critical('Disconnect server')
                    exit(1)
                else:
                    client_logger.error('Failed to send message. Connection timeout.')


    def create_who_message(self):
        '''
        Generates a list of clients
        :return:
        '''
        message_dict = {ACTION: WHO, TIME: time.time(), SENDER: self.account_name, DESTINATION: self.account_name,
                        MESSAGE_TEXT: None}
        client_logger.debug(f'The message dictionary is generated: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            client_logger.error('Lost connection to server.')
            sys.exit(1)

    def run(self):
            '''
            User interaction function, request commands, send messages
            :return:
            '''
        while True:
            # self.print_help()
            # command = input('Input command: ').lower()
            # if command == 'message' or command == 'm':
            #     self.create_message()
            # elif command == 'help' or command == 'h':
            #     self.print_help()
            # elif command == 'who' or command == 'w':
            #     client_logger.debug(f"Server users query:")
            #     self.create_who_message()
            # elif command == 'exit' or command == 'e' or command == 'q':
            #     send_message(self.sock, self.create_exit_message())
            #     print('Terminating the connection...')
            #     client_logger.info("Completion of work on the user's command.")
            #     time.sleep(0.5)
            #     break
            # else:
            #     print('Command not recognized, please try again. help - display supported commands.')
            self.print_help()
            command = input('Input command: ')
            if command in ('message', 'm'):
                self.create_message()
            elif command in ('help', 'h'):
                self.print_help()
            elif command in ('exit', 'q'):
                with sock_lock:
                    try:
                        send_message(self.sock, self.create_exit_message())
                    except:
                        pass
                    print('Terminating the connection.')
                    client_logger.info("Completion of work on the user's command.")

                time.sleep(0.5)
                break
            elif command in ('contacts', 'c'):
                with database_lock:
                    contacts_list = self.database.get_contacts()
                for contact in contacts_list:
                    print(contact)
            elif command in ('edit', 'e'):
                self.edit_contacts()
            elif command in ('history', 'mh'):
                self.print_history()
            else:
                print('Command not recognized, please try again. help - display supported commands.')

    def print_help(self):
        """Function for displaying help on usage"""
        print('Supported commands:')
        print('message (m) - send a message. To and text will be requested separately.')
        print('who (w) - name users')
        print('help (h) - display command prompts')
        print('exit (q или e)- exit')


    def print_history(self):
        client_logger.debug(f'message history requested')
        what_msg = input('Show incoming messages - in, outgoing - out, all - just Enter:')
        with database_lock:
            if what_msg == 'in':
                history_list = self.database.get_history(to_who=self.account_name)
                for message in history_list:
                    print(f'{message[3]} | {message[0]} | {message[2]}')
            elif what_msg == 'out':
                history_list = self.database.get_history(from_who=self.account_name)
                for message in history_list:
                    print(f'{message[3]} | {message[1]} | {message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(f'{message[3]} | {message[0]} -> {message[1]} | {message[2]}')


    def edit_contacts(self):
        ans = input('Enter - to remove, + to add:')
        if ans == '-':
            edit = input('Name delete contact')
            with database_lock:
                if self.database.check_contact(edit):
                    self.database.del_contact(edit)
                else:
                    client_logger.error('An attempt was made to delete a non-existent contact.')
        elif ans == '+':
            edit = input('Name of created contact')
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                with sock_lock:
                    try:
                        add_contact(self.sock, self.account_name, edit)
                    except ServerError:
                        client_logger.error('Failed to send information to the server.')



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
            time.sleep(1)
            with sock_lock:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message
                    and MESSAGE in message and message[DESTINATION] == self.account_name:
                    print(f'Message received from user {message[SENDER]}:{message[MESSAGE_TEXT]}')
                    client_logger.info(f'Message received from user {message[SENDER]}:{message[MESSAGE_TEXT]}')
                elif ACTION in message and message[ACTION] == WHO and SENDER in message \
                        and DESTINATION in message and MESSAGE_TEXT in message and message[
                    DESTINATION] == self.account_name:
                    print(f'Message from user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    client_logger.info(f'Message from user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    client_logger.error(f'Invalid message received from server: {message}')
            except IncorrectDataReceivedError:
                client_logger.error(f'Failed to decode received message.')
            except(OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                client_logger.critical(f'Lost connection to server.')
                break
            else:
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message \
                        and DESTINATION in message and MESSAGE_TEXT in message \
                        and message[DESTINATION] == self.account_name:
                    print(f'Send user message {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    with database_lock:
                        try:
                            self.database.save_message(message[SENDER], self.account_name, message[MESSAGE_TEXT])
                        except:
                            client_logger.error('Database interaction error')
                    client_logger.info(f'Send message from {message[SENDER]} | {message[MESSAGE_TEXT]}')
                else:
                    client_logger.error(f'Incorrect message received from server: {message}')


@log
def create_presence(account_name='Guest'):
    '''

    :param account_name:The function generates a client presence request
    :return:
    '''
    out = {ACTION:PRESENCE, TIME: time.time(), USER: {ACCOUNT_NAME: account_name}}
    client_logger.debug(f'{PRESENCE} message generated for user {account_name}')
    return out


@log
def process_response_ans(message):
    client_logger.debug(f'Parsing the welcome message from the server: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


# def process_handler(message):
#     '''
#
#     :param message:The function parses the server response
#     :return:
#     '''
#     client_logger.debug(f'Parsing the welcome message from the server: {message}')
#     if RESPONSE in message:
#         if message[RESPONSE] == 200:
#             client_logger.debug(f"{message[RESPONSE]} contains {ERR_200}")
#             return message[MESSAGE]
#         elif message[RESPONSE] == ERR400:
#             client_logger.debug(f"{message[RESPONSE]} contains {ERR400}")
#             raise ServerError(f"{ERR400}: {message[ERROR]}")
#     raise ReqFieldMissingError(RESPONSE)


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    check_port = validate_port(server_port)
    if not check_server_ip:
        client_logger.critical(f'Incorrect connection port: {server_port}')
        print(f'Incorrect connection port: {server_port}')
        exit(1)
    return server_address, server_port, client_name


def contact_list_request(sock, name):
    client_logger.debug(f'Request contact list for user {name}')
    req = {ACTION: GET_CONTACTS, TIME: time.time(), USER: name}
    client_logger.debug(f'Request {req} generated')
    send_message(sock, req)
    answer = get_message(sock)
    client_logger.debug(f'Answer received {answer}')
    if RESPONSE in answer and answer[RESPONSE] == 202:
        return answer[LIST_INFO]
    else:
        raise ServerError


def user_list_request(sock,username):
    client_logger.debug(f'Request a list of known users {username}')
    req = {ACTION: USERS_REQUEST, TIME: time.time(), ACCOUNT_NAME: username}
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


def add_contact(sock, username, contact):
    client_logger.debug(f'Create contact{contact}')
    req = {ACTION: ADD_CONTACT, TIME: time.time(), USER: username, ACCOUNT_NAME: contact}
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Error create contact')
    print(f'{contact} input to contact')


def remove_contact(sock, username, contact):
    client_logger.debug(f'Create contact {contact}')
    req = {ACTION: REMOVE_CONTACT, TIME: time.time(), USER: username, ACCOUNT_NAME: contact}
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Error user delete')
    print(f'{contact} delete from contacts')



def get_user():
    '''

    :return: the function returns the username
    '''
    while True:
        account = input('Enter username: ')
        if not re.match(r'[A-Za-z]', account) or len(account) > 25 or len(account) < 3:
            client_logger.error(f'Invalid username: {account}')
            print('Username must be between 3 and 25 Latin characters')
        elif account.lower().strip() == 'guest':
            client_logger.error(f'Invalid username: {account}')
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
    out = {ACTION: action, TIME: time.time(), USER: {ACCOUNT_NAME: account_name}, MESSAGE: msg}
    client_logger.debug(f'{action} message generated for user {account_name}')
    client_logger.debug(f"{out}")
    return out



# def start_client():
#     srv_settings = server_settings()
#     server_address = srv_settings[0]
#     server_port = srv_settings[1]
#     client_listen = srv_settings[2]
#     print(f'Start client on: {server_address}:{server_port}')
#     client_logger.info(f'Start client on: {server_address}:{server_port}')
#
#     try:
#         transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         transport.connect((server_address, server_port))
#         send_message(transport, create_presence())
#         answer = process_handler(get_message(transport))
#         client_logger.info(f'Connection to the server {server_address}:{server_port}. Answer: {answer}')
#         print(f'Server connection {server_address}:{server_port} \n {answer}')
#
#         account_name = get_user()
#         client_logger.info(f'Guest logged in as {account_name}')
#         client_logger.debug(
#             f'sending {AUTH} message to server {server_address}:{server_port} from user={account_name}')
#         message_to_server = create_action(account_name, action=AUTH, msg=None)
#         send_message(transport, message_to_server)
#         try:
#             answer = process_handler(get_message(transport))
#             print(answer)
#         except(ValueError, json.JSONDecodeError):
#             print(answer)
#             client_logger.error(f'{ERR400}. Failed to decode message from server')
#             print(f'{ERR400}. Failed to decode message from server')
#
#     except json.JSONDecodeError:
#         client_logger.error(f'Failed to decode JSON string')
#         print(f'Failed to decode JSON string')
#         sys.exit(1)
#     except ServerError as error:
#         client_logger.error(f'Connection error: {error.text}')
#         print(f'Connection error: {error.text}')
#         sys.exit(1)
#     except ReqFieldMissingError as missing_error:
#         client_logger.error(f'The server response does not contain the required field {missing_error.missing_field}')
#         sys.exit(1)
#     except ConnectionRefusedError:
#         client_logger.critical(f'Failed to connect to server {server_address}:{server_port}')
#         sys.exit(1)
#     else:
#         '''start the client process of receiving messages '''
#         receiver = ClientReader(account_name, transport)
#         receiver.daemon = True
#         receiver.start()
#
#         ''' Start sending messages and interacting with the user.'''
#         user_interface = ClientSender(account_name, transport)
#         user_interface.daemon = True
#         user_interface.start()
#         client_logger.debug('Process running')
#
#         while True:
#             time.sleep(1)
#             if receiver.is_alive() and user_interface.is_alive():
#                 continue
#             break


def database_load(sock, database, username):
    try:
        users_list = user_list_request(sock, username)
    except ServerError:
        client_logger.error('Failed to query list of known users.')
    else:
        database.add_users(users_list)

    try:
        contacts_list = contacts_list_request(sock, username)
    except ServerError:
        client_logger.error('Contact list request failed.')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


def main():
    server_address, server_port, client_name = arg_parser()
    print(f'start client on: {server_address}: {server_port}')

    if not client_name:
        client_name = get_user()
    else:
        print(f'Client module started with name: {client_name}')

    client_logger.info(f'start client on: {server_address}: {server_port} | User name: {client_name} ')

    try:
        transport = create_socket()
        transport.settimeout(1)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_response_ans(get_message(transport))
        client_logger.info(f'A connection to the server has been established. Server response: {answer}')
        print(f' Connection to the server has been established.')

    except json.JSONDecodeError:
        client_logger.error('Failed to decode received Json string.')
        exit(1)
    except ServerError as error:
        client_logger.error(f'When establishing a connection, the server returned an error: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        client_logger.error(f'A required field is missing in the server response {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        client_logger.critical(f'Failed to connect to server {server_address}:{server_port}:'
                               f'the destination computer denied the connection request.')
        exit(1)
    else:
        # create Database
        database = ClientDatabase(client_name)
        database_load(transport, database, client_name)

        # If the connection to the server is established correctly, we start the flow of interaction with the user
        module_sender = ClientSender(client_name, transport, database)
        module_sender.daemon = True
        module_sender.start()
        client_logger.debug(f'Message thread started')

        # then we start the thread - the message receiver.
        module_receiver = ClientReader(client_name, transport, database)
        module_receiver.daemon = True
        module_receiver.start()
        client_logger.debug(f'Message receiving thread started')


        while True:
            time.sleep(1)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()

















