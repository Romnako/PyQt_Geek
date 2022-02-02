import sys
import os
import unittest
from unittest import TestCase

import json
from Lesson_2_pyqt.lib.variables import *
from Lesson_2_pyqt.lib.utils import *

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestSocket:
    '''
    Test class for testing sending and receiving,
     on creation requires a dictionary to be run through
     via test function
    '''


    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        '''

        :param message_to_send: Test send function, correctly encodes the message,
         also saves what should have been sent to the socket.
        :return: message_to_send - what we send to the socket
        '''
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message_to_send

    def resv(self, max_len):
        '''

        :param max_len: Getting data from a socket
        :return: encoding data
        '''
        json_test_messsage = json.dumps(self, max_len)
        return json_test_messsage.encode(ENCODING)


class Tests(unittest, TestCase):
        '''
        Test class for testing
        '''
        test_dict_send = {ACTION: PRESENCE, TIME: 2, USER: {ACCOUNT_NAME: 'NEW_USER'}}
        test_dict_resv_ok = {RESPONSE: 200}
        test_dict_resv_err = {RESPONSE: 400, ERROR: ERR400}

        def test_validate_ip_success(self):
            '''
            Checks if the string contains the correct IP address
            :return: boolean
            '''
            self.assertEqual(validate_ip('127.0.0.1'), True)

        def test_validate_ip_fail_str_is_long(self):
            '''
            Checks if the string contains the correct IP address
            :return: boolean
            '''
            self.assertEqual(validate_ip('127.0.0.1.1.1'), False)

        def test_validate_ip_fail_str_is_not_digit(self):
            '''
            Checks if the string contains the correct IP address
            :return: boolean
            '''
            self.assertEqual(validate_ip('127.0.a.1'), False)

        def test_validate_ip_fail_ipport(self):
            '''
            Checks if the string contains the correct IP address
            :return: boolean
            '''
            self.assertEqual(validate_ip('127.0.0.1:8080'), False)

        def test_validate_ip_fail_incorrect_number(self):
            '''
            Checks if the string contains the correct IP address
            :return: boolean
            '''
            self.assertEqual(validate_ip('127.555.0.0'), False)

        def test_validate_port_ok(self):
            '''
             Check string can be an allowed port
            :return: boolean
            '''
            self.assertEqual(validate_port('8080'), False)

        def test_validate_port_forbidden(self):
            '''
             Check string can be an allowed port
            :return: boolean
            '''
            self.assertEqual(validate_port('1010'), False)

        def test_validate_port_not_number(self):
            '''
             Check string can be an allowed port
            :return: boolean
            '''
            self.assertEqual(validate_port('port'), False)

        def test_server_setting_default(self):
            '''
            Command line startup test
            :return:
            '''
            self.assertEqual(server_settings(), [DEFAULT_IP, DEFAULT_PORT])

        def test_send_message(self):
            '''
            Test the correctness of the send function,
            create a test socket and check the correctness of sending the dictionary
            :return:
            '''
            test_soket = TestSocket(self.test_dict_send)
            send_message(test_soket, self.test_dict_send)
            self.assertEqual(test_soket.encoded_message, test_soket.received_message)

            with self.assertRaises(Exception):
                send_message(test_soket, test_soket)

        def test_get_message(self):
            '''
            Receive message function test
            :return:
            '''
            test_sock_ok = TestSocket(self.test_dict_resv_ok)
            test_sock_err = TestSocket(self.test_dict_resv_err)

            self.assertEqual(get_message(test_sock_ok), self.test_dict_resv_ok)
            self.assertEqual(get_message(test_sock_ok), self.test_dict_resv_err)


if __name__ == '__main__':
    unittest.main()