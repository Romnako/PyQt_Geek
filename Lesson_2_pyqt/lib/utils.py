import json
import socket
import sys
sys.path.append('../')
from Lesson_2_pyqt.lib.errors import IncorrectDataReceivedError, NonDictInputError
from Lesson_2_pyqt.lib.variables import PACKAGE_LENGTH, ENCODING, DEFAULT_PORT, DEFAULT_IP, MAX_CONNECTIONS, CLIENT_LISTEN
from Lesson_2_pyqt.logs.decoration_log import log


def validate_ip(ip_str):
    '''
    :param ip_str:Verify that the string is a valid IPv4 address.
    :return: True / False
    '''
    tmp_str = ip_str.split('.')
    if len(tmp_str) != 4:
        raise False
    for el in tmp_str:
        if not el.isdigit():
            return False
        i = int(el)
        if i < 0 or i > 255:
            return False
    return True

def validate_port(ip_port):
    '''

    :param ip_port: Checking if a string can be an allowed port
    :return: True/False
    '''
    try:
        ip_port = int(ip_port)
        if ip_port < 1025 or ip_port > 65535:
            return False
        else:
            return True
    except:
        return False


def server_settings():
    '''
    Loading command line parameters, if there are no parameters, then set the default values.
     server.py -i(or -ip) 192.168.1.125 -p(or -port) 9999
    :return:
    '''
    client_listen = CLIENT_LISTEN
    try:
        if '-l'in sys.argv:
            client_listen = True
        if '-ip' in sys.argv:
            server_address = sys.argv[sys.argv.index('-ip') + 1]
        elif '-i' in sys.argv:
            server_address = sys.argv[sys.argv.index('-i') + 1]
        else:
            server_address = DEFAULT_IP

        if '-p' in sys.argv:
            server_port = int(sys.argv[sys.argv.index('-p') + 1])
        elif '-port' in sys.argv:
            server_port = int(sys.argv[sys.argv.index('-port') + 1])
        else:
            server_port = DEFAULT_PORT

    except ValueError:
        print('Invalid address. Running the script should be: ****.py -i(or -ip) XXX.XXX.XXX.XXX -p(or -port) 9999')
        sys.exit(1)
    return [server_address, server_port, client_listen]


def create_socket():
    '''
    create socket for connection
    :return: socket
    '''
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


@log
def get_message(client):
    '''

    :param client: Utility for receiving and decoding messages
     accepts bytes
    :return: dictionary, if something else is accepted, it gives a value error
    '''
    response_bytes = client.recv(PACKAGE_LENGTH)
    if isinstance(response_bytes, bytes):
        json_response = response_bytes.decode(ENCODING)
        response = json.loads(json_response)

        if isinstance(response, dict):
            return response
        raise IncorrectDataReceivedError
    raise IncorrectDataReceivedError


@log
def send_message(sock_obj, message):
    '''
    Message encoding and sending utility
     takes a dictionary and sends it
    :param sock_obj:message
    :param message:dictionary
    :return:message
    '''
    if not isinstance(message, dict):
        raise NonDictInputError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock_obj.send(encoded_message)

