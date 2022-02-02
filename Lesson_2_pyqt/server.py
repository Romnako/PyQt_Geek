import logging
import select
from Lesson_2_pyqt.lib.variables import *
from Lesson_2_pyqt.lib.utils import server_settings, create_socket, get_message, send_message
from Lesson_2_pyqt.lib.descriptors import PortValidate, IpValidate
from Lesson_2_pyqt.lib.metaclasses import ServerMaker

SERVER_LOGGER = logging.getLogger('server')



class Server(metaclass=ServerMaker):
    srv_port = PortValidate()
    srv_adr = IpValidate()

    def __init__(self, server_address, server_port):
        self.srv_adr = server_address
        self.srv_port = server_port
        self.clients = []
        self.message = []
        self.names = dict()

    def init_socket(self):
        '''
        Server started
        :return:
        '''
        transport = create_socket()
        transport.bind(self.srv_adr, self.srv_port)
        transport.settimeout(SERVER_TIMEOUT)
        transport.listen(MAX_CONNECTIONS)
        print(f'server start on: {self.srv_adr}:{self.srv_port}')
        SERVER_LOGGER.info(f'server start on: {self.srv_adr}:{self.srv_port}')

        self.socket_transport = transport
        self.socket_transport.listen()

    def main_loop(self):
        self.init_socket()

        while True:
            try:
                client, client_address = self.socket_transport.accept()
                SERVER_LOGGER.debug(f'client | {client_address}')
            except OSError:
                pass
            else:
                print(f'Connection request received from {str(client_address)}')
                SERVER_LOGGER.info(f'connection established with client {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.client_message_handler(get_message(client_with_message), client_with_message)
                    except Exception:
                        SERVER_LOGGER.info(f'Client {client_with_message.getpeername()} disconnected')
                        print(f'Client {client_with_message.getpeername()} disconnected')
                        self.clients.remove(client_with_message)
                        print(self.clients)

            for message in self.message:
                try:
                    self.process_message(message, send_data_lst)
                except:
                    SERVER_LOGGER.info(f'Communication with client {message[DESTINATION]} lost')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
                self.message.clear()

    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            SERVER_LOGGER.info(f'Sent message to user {message[DESTINATION]} from user {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            SERVER_LOGGER.error(f'User {message[DESTINATION]} is not registered on the server, sending a message is not possible.'


    def client_message_handler(self, message, client):
        SERVER_LOGGER.debug(f'Function to parse message from client: {message}')
        if ACTION not in message:
            SERVER_LOGGER.error(f'сообщение от клиента не содержит обязательного поля ACTION: {message}')
            print(f'сообщение от клиента не содержит обязательного поля ACTION: {message}')
            send_message(client, {RESPONSE: 400, ERROR: ERR400})
            return
        elif TIME not in message:
            SERVER_LOGGER.error(f'The message from the client does not contain the required field TIME: {message}')
            print(f'the message from the client does not contain the required field TIME: {message}')
            send_message(client, {RESPONSE: 400, ERROR: ERR400})
            return
        elif message[ACTION] == PRESENCE and str(message[USER][ACCOUNT_NAME]).lower() == 'guest':
            SERVER_LOGGER.debug(f'Generated PRESENCE message:{message}')
            send_message(client, {RESPONSE: 200, ERROR: ERR_200, MSG: str(f'Welcome, {message[USER][ACCOUNT_NAME]}')})
            return
        elif message[ACTION] == AUTH and USER in message and str(message[USER][ACCOUNT_NAME]).lower() != 'quest':
            SERVER_LOGGER.info(f'Получено AUTH сообщение: {message}')
            if str(message[USER][ACCOUNT_NAME]).lower() not in str(self.names.keys()).lower():
                SERVER_LOGGER.info(f'Generated AUTH message: {message}. User is listed')
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, {RESPONSE: 200, ERROR: ERR_200, MSG: str(f'Welcome, {message[USER][ACCOUNT_NAME]}')})
                return
            else:
                SERVER_LOGGER.error(f'{ERR_USER_ALREADY_EXIST}: {message}')
                responce = RESPONSE_400
                responce[ERROR] = ERR_USER_ALREADY_EXIST
                send_message(client, responce)
                self.clients.remove(client)
                client.close()
            return
        elif message[ACTION] == MSG and DESTINATION in message and SENDER in message and MSG_TEXT in message:
            SERVER_LOGGER.debug(f'Generated MSG message: {message}')
            self.messages.append((message))
            return
        elif ACTION in message and message[ACTION] == WHO:
            SERVER_LOGGER.debug(f'Generated WHO message: {message}')
            message[DESTINATION] = message[SENDER]
            all_names = ''
            for el in self.names:
                all_names = all_names + '|' + el
            all_names = f'online users:{all_names[3:]}'
            message[MSG_TEXT] = all_names
            self.messages.append((message))
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            SERVER_LOGGER.info(f'User {message[ACCOUNT_NAME]} logged out')
            print(f'User {message[ACCOUNT_NAME]} logged out')
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            print(self.names)
            return
        else:
            SERVER_LOGGER.error(f'function to parse message from the client, none of the conditions matched: {message}')
            print(f'function to parse message from the client, none of the conditions matched: {message}')
            responce = RESPONSE_400
            responce[ERROR] = 'The request is invalid.'
            send_message(client, responce)
            return

    def start_server():
        srv_settings = server_settings()
        server_address = srv_settings[0]
        server_port = srv_settings[1]
        SERVER_LOGGER.debug(f'srv_settings:{server_address}:{server_port}')
        server = Server(server_address, server_port)
        server.main_loop()


if __name__ == '__main__':
    Server.start_server()














