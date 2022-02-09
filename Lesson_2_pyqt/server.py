import socket
import sys
import os
import argparse
import json
import logging
import select
import time
import threading
import configparser
from asyncio.base_events import Server

import Lesson_2_pyqt.logs.config_server_log
from Lesson_2_pyqt.logs.decoration_log import log
from Lesson_2_pyqt.lib.errors import *
from Lesson_2_pyqt.lib.variables import *
from Lesson_2_pyqt.lib.utils import *
from Lesson_2_pyqt.lib.descriptors import PortValidate, IpValidate
from Lesson_2_pyqt.lib.metaclasses import ServerMaker
from Lesson_2_pyqt.server_db import ServerStorage
from server_gui import MainWindow, gui_create_model, HistoryWindow, create_stat_model, ConfigWindow,\
    LoginHistoryWindow, create_stat_login_history_model
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem


server_logger = logging.getLogger('server')
new_connection = False
conflag_lock = threading.Lock()


@log
def arg_parser(default_port, default_address):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_address, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port



class Server(threading.Thread, metaclass=ServerMaker):
    port = PortValidate()
    addr = IpValidate()

    def __init__(self, server_address, server_port, database, socket_transport):
        self.socket_transport = socket_transport
        self.addr = server_address
        self.port = server_port
        self.database = database
        self.clients = []
        self.message = []
        self.names = dict()
        # Ancestor constructor
        super().__init__()

    def init_socket(self):
        '''
        Server started
        :return:
        '''
        # transport = create_socket()
        # transport.bind(self.srv_adr, self.srv_port)
        # transport.settimeout(SERVER_TIMEOUT)
        # transport.listen(MAX_CONNECTIONS)
        # print(f'server start on: {self.srv_adr}:{self.srv_port}')
        # server_logger.info(f'server start on: {self.srv_adr}:{self.srv_port}')
        #
        # self.socket_transport = transport
        # self.socket_transport.listen()

        server_logger.info(f'Server is running. Port for connections: {self.port}.'
                            f'Address from which connections are accepted: {self.addr}.'
                            f'If no address is specified, connections from any address are accepted.')

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen()

    #def main_loop(self):
    def run(self):
        self.init_socket()

        while True:
            try:
                client, client_address = self.socket_transport.accept()
                server_logger.debug(f'client | {client_address}')
            except OSError:
                pass
            else:
                #print(f'Connection request received from {str(client_address)}')
                server_logger.info(f'Connection established with client {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                server_logger.error(f'Error socket: {err}')

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.client_message_handler(get_message(client_with_message), client_with_message)
                    except Exception:
                        server_logger.info(f'Client {client_with_message.getpeername()} disconnected')
                        #print(f'Client {client_with_message.getpeername()} disconnected')
                        self.clients.remove(client_with_message)
                        #print(self.clients)

            for message in self.message:
                try:
                    self.process_message(message, send_data_lst)
                except:
                    server_logger.info(f'Communication with client {message[DESTINATION]} lost')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
                self.message.clear()

    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            server_logger.info(f'Sent message to user {message[DESTINATION]} from user {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            server_logger.error(f'User {message[DESTINATION]} is not registered on the server, '
                                f'sending a message is not possible.')


    def client_message_handler(self, message, client):
        server_logger.debug(f'Function to parse message from client: {message}')
        if ACTION not in message:
            server_logger.error(f'сообщение от клиента не содержит обязательного поля ACTION: {message}')
            #print(f'сообщение от клиента не содержит обязательного поля ACTION: {message}')
            send_message(client, {RESPONSE: 400, ERROR: ERR400})
            return
        elif TIME not in message:
            server_logger.error(f'The message from the client does not contain the required field TIME: {message}')
            #print(f'the message from the client does not contain the required field TIME: {message}')
            send_message(client, {RESPONSE: 400, ERROR: ERR400})
            return
        elif message[ACTION] == PRESENCE and str(message[USER][ACCOUNT_NAME]).lower() == 'guest':
            server_logger.debug(f'Generated PRESENCE message:{message}')
            send_message(client, {RESPONSE: 200, ERROR: ERR_200, MESSAGE: str(f'Welcome, {message[USER][ACCOUNT_NAME]}')})
            return
        elif message[ACTION] == AUTH and USER in message and str(message[USER][ACCOUNT_NAME]).lower() != 'quest':
            server_logger.info(f'Получено AUTH сообщение: {message}')
            if str(message[USER][ACCOUNT_NAME]).lower() not in str(self.names.keys()).lower():
                server_logger.info(f'Generated AUTH message: {message}. User is listed')
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                # add user to database
                server_logger.debug(f'add user {message[USER][ACCOUNT_NAME]} to database {self.database}')
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip,client_port)

                send_message(client, {RESPONSE: 200, ERROR: ERR_200, MESSAGE: str(f'Welcome, {message[USER][ACCOUNT_NAME]}')})
                return
            else:
                server_logger.error(f'{ERR_USER_ALREADY_EXIST}: {message}')
                responce = RESPONSE_400
                responce[ERROR] = ERR_USER_ALREADY_EXIST
                send_message(client, responce)
                self.clients.remove(client)
                client.close()
            return
        elif message[ACTION] == MESSAGE and DESTINATION in message and SENDER in message and MESSAGE_TEXT in message:
            server_logger.debug(f'Generated MSG message: {message}')
            self.message.append((message))
            return
        elif ACTION in message and message[ACTION] == WHO:
            server_logger.debug(f'Generated WHO message: {message}')
            message[DESTINATION] = message[SENDER]
            all_names = ''
            for el in self.names:
                all_names = all_names + '|' + el
                # function in database
            all_names = ''
            for user in sorted(self.database.active_users_list()):
                all_names = all_names + '|' + user[0]

            all_names = f'online users:{all_names[3:]}'
            message[MESSAGE_TEXT] = all_names
            self.message.append((message))
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            server_logger.info(f'User {message[ACCOUNT_NAME]} logged out')
            self.database.user_logout(message[ACCOUNT_NAME])
            print(f'User {message[ACCOUNT_NAME]} logged out')
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            print(self.names)
            return
        else:
            server_logger.error(f'function to parse message from the client, none of the conditions matched: {message}')
            print(f'function to parse message from the client, none of the conditions matched: {message}')
            responce = RESPONSE_400
            responce[ERROR] = 'The request is invalid.'
            send_message(client, responce)
            return

    def print_help():
        print('Supported commands:')
        print('users (u)- list of famous users')
        print('connected (c) - list of connected users')
        print('loghist (lh) - user login history')
        print('exit (e /q)- server shutdown')
        print('help (h)- displaying help on supported commands')

    def start_server():
    #     srv_settings = server_settings()
    #     server_address = srv_settings[0]
    #     server_port = srv_settings[1]
    #
    #     database = ServerStorage()
    #     SERVER_LOGGER.info(f"server start on:{server_address}:{server_port}")
    #     SERVER_LOGGER.info(f"connected to DB: {database.database_engine}")
    #     #SERVER_LOGGER.debug(f'srv_settings:{server_address}:{server_port}')
    #     server = Server(server_address, server_port, database)
    #     #server.main_loop()
    #     server.daemon = True
    #     server.start()
    #     print_help()
    #
    # while True:
    #     command = input('Input the command: ')
    #     if command in ('help', 'h'):
    #         print_help()
    #     elif command in ('exit', 'e', 'q'):
    #         break
    #     elif command in ('user', 'u'):
    #         for user in sorted(database.users_list()):
    #             print(f'User {user[0]}, last login: {user[1]}')
    #     elif command in ('connected', 'c'):
    #         for user in sorted(database, active_users_list):
    #             print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
    #     elif command in ('loghist','lh'):
    #         name = input('Enter a username to view history. To display the entire history, just press Enter:')
    #         for user in sorted(database.login_history(name)):
    #             print(f'User: {user[0]} Login Time: {user[1]}. Login with: {user[2]}:{user[3]}')
    #     else:
    #         print('The command is not recognized.')
        config = configparser.ConfigParser()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config.read(f"{dir_path}/{'server.ini'}")

        listen_address, listen_port = arg_parser(
            config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])


        database = ServerStorage(
            os.path.join(
                config['SETTINGS']['Database_path'],
                config['SETTINGS']['Database_file']))

        server = Server(listen_address, listen_port, database)
        server.daemon = True
        server.start()

        server_app = QApplication(sys.argv)
        main_window = MainWindow()

        main_window.statusBar().showMessage('Server Working')
        main_window.active_clients_table.setModel(gui_create_model(database))
        main_window.active_clients_table.resizeColumnsToContents()
        main_window.active_clients_table.resizeRowsToContents()



        def list_update():
            global new_connection
            if new_connection:
                main_window.active_clients_table.setModel(gui_create_model(database))
                main_window.active_clients_table.resizeColumnsToContents()
                main_window.active_clients_table.resizeRowsToContents()
                with conflag_lock:
                    new_connection = False


        def show_statistics():
            global stat_window
            stat_window = HistoryWindow()
            stat_window.history_table.setModel(create_stat_model(database))
            stat_window.history_table.resizeColumnsToContents()
            stat_window.history_table.resizeRowsToContents()
            stat_window.show()


        def show_login_history():
            global stat_window
            stat_window = LoginHistoryWindow()
            stat_window.history_table.setModel(create_stat_login_history_model(database))
            stat_window.history_table.resizeColumnsToContents()
            stat_window.history_table.resizeRowsToContents()
            stat_window.show()


        def server_config():
            global config_window

            config_window = ConfigWindow()
            config_window.db_path.insert(config['SETTINGS']['Database_path'])
            config_window.db_file.insert(config['SETTINGS']['Database_file'])
            config_window.port.insert(config['SETTINGS']['Default_port'])
            config_window.ip.insert(config['SETTINGS']['Listen_Address'])
            config_window.save_btn.clicked.connect(save_server_config)


        def save_server_config():
            global config_window
            message = QMessageBox()
            config['SETTINGS']['Database_path'] = config_window.db_path.text()
            config['SETTINGS']['Database_file'] = config_window.db_file.text()
            try:
                port = int(config_window.port.text())
            except ValueError:
                message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
            else:
                config['SETTINGS']['Listen_Address'] = config_window.ip.text()
                if 1023 < port < 65536:
                    config['SETTINGS']['Default_port'] = str(port)
                    # print(port)
                    with open('server.ini', 'w') as conf:
                        config.write(conf)
                        message.information(config_window, 'OK', 'Настройки успешно сохранены!')
                else:
                    message.warning(config_window, 'Ошибка', 'Порт должен быть от 1024 до 65536')


        timer = QTimer()
        timer.timeout.connect(list_update)
        timer.start(1000)


        main_window.refresh_button.triggered.connect(list_update)
        main_window.show_history_button.triggered.connect(show_statistics)
        main_window.config_btn.triggered.connect(server_config)
        main_window.show_login_history_button.triggered.connect(show_login_history)

    # GUI
        server_app.exec_()

if __name__ == '__main__':
   # Server.start_server()
    start_server()














