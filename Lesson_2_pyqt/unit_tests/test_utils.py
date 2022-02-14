import json
import sys
from unittest import TestCase

sys.path.append('../')
from Lesson_2_pyqt.lib.utils import *
from Lesson_2_pyqt.lib.variables import *
import unittest
from Lesson_2_pyqt.lib.errors import NonDictInputError

class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict

    def send(self, message_to_send):
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message_to_send

    def recv(self, max_len):
        self.max_len = max_len
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class Tests(unittest, TestCase):
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 1111.1111,
        USER: {
            ACCOUNT_NAME: 'test_test'
        }
    }
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_err = {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }

    '''Test the correctness of the sending function, create a test socket and check the correctness of sending the dictionary'''
    def test_send_message(self):
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)
        self.assertRaises(NonDictInputError, send_message, test_socket, 1111)

    '''Message receiving function test'''
    def test_get_message(self):
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)
        self.assertEqual(get_message(test_sock_ok), self.test_dict_recv_ok)
        self.assertEqual(get_message(test_sock_err), self.test_dict_recv_err)


if __name__ == '__main__':
    unittest.main()