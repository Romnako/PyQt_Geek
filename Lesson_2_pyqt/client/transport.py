import sys
import json
import socket
import time
import threading
import sys
import logging
from PyQt5.QtCore import pyqtSignal, QObject
sys.path.append('../')
from Lesson_2_pyqt.lib.metaclasses import ClientMaker
from Lesson_2_pyqt.lib.utils import *
from Lesson_2_pyqt.lib.variables import *
from Lesson_2_pyqt.lib.errors import ServerError


client_logger = logging.getLogger('client')

socket_lock = threading.Lock()



class ClientTransport(threading.Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.username = username
        self.transport = None
        self.connection_init(port, ip_address)

        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                client_logger.critical(f'Lost connection to server.')
                raise ServerError('Lost connection to server')
            client_logger.error('Connection timeout when updating user lists.')
        except json.JSONDecodeError:
            client_logger.critical(f'Lost connection to server.')
            raise ServerError('Lost connection to server.')

        self.running = True

    def connection_init(self, port, ip):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.settimeout(5)


        connected = False
        for cnt in range(5):
            print(f'Connection attempt {cnt + 1}')
            client_logger.info(f'Connection attempt {cnt + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        if not connected:
            client_logger.critical('Failed to connect to server')
            raise ServerError('Failed to connect to server')

        client_logger.debug('Connect to server')

        try:
            with socket_lock:
                send_message(self.transport, self.create_presence())
                self.process_server_ans(get_message(self.transport))
        except (OSError, json.JSONDecodeError):
            client_logger.critical('Failed to connect to server')
            raise ServerError('Failed to connect to server')

        client_logger.info('Connect to server')

    def create_presence(self):
        out = {ACTION: PRESENCE, TIME: time.time(), USER: {ACCOUNT_NAME: self.username}}
        client_logger.debug(f'Generated {PRESENCE} message for user {self.username}')
        return out


    def process_server_ans(self, message):
        client_logger.debug(f'Message from server: {message}')

        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            else:
                client_logger.debug(f'Unknown code received: {message[RESPONSE]}')


        elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                and MESSAGE_TEXT in message and message[DESTINATION] == self.username:
            client_logger.debug(f'Message from user {message[SENDER]}:{message[MESSAGE_TEXT]}')
            self.database.save_message(message[SENDER], 'in', message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])


    def contacts_list_update(self):
        req = {ACTION: GET_CONTACTS, TIME: time.time(), USER: self.username}
        client_logger.debug(f'Request contact list for {self.name}: {req}')
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        client_logger.debug(f'Answer received {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            client_logger.error('Failed to update contact list')

    def user_list_update(self):
        client_logger.debug(f'Query a List of Known Users {self.username}')
        req = {ACTION: USERS_REQUEST, TIME: time.time(), ACCOUNT_NAME: self.username}
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            client_logger.error('Failed to update contact list.')


    def add_contact(self, contact):
        client_logger.debug(f'Update contact {contact}')
        req = {ACTION: ADD_CONTACT, TIME: time.time(), USER: self.username, ACCOUNT_NAME: contact}
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))


    def remove_contact(self, contact):
        client_logger.debug(f'Delete contact {contact}')
        req = {ACTION: REMOVE_CONTACT, TIME: time.time(), USER: self.username, ACCOUNT_NAME: contact}
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))


    def transport_shutdown(self):
        self.running = False
        message = {ACTION: EXIT, TIME: time.time(), ACCOUNT_NAME: self.username}
        with socket_lock:
            try:
                send_message(self.transport, message)
            except OSError:
                pass
        client_logger.debug('Transport shuts down.')
        time.sleep(0.5)


    def send_message(self, to, message):
        message_dict = {ACTION: MESSAGE, SENDER: self.username, DESTINATION: to, TIME: time.time(),
                        MESSAGE_TEXT: message}
        client_logger.debug(f'Update dictionary message: {message_dict}')


        with socket_lock:
            send_message(self.transport, message_dict)
            self.process_server_ans(get_message(self.transport))
            client_logger.info(f'Send message for user {to}')

    def run(self):
        client_logger.debug('The process is running - the receiver of messages from the server.')
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        client_logger.critical(f'Lost connection to server')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    client_logger.debug(f'Lost connection to server.')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    client_logger.debug(f'Message received from the server: {message}')
                    self.process_server_ans(message)
                finally:
                    self.transport.settimeout(5)
            if message:
                client_logger.debug(f'Принято сообщение с сервера: {message}')
                self.process_server_ans(message)