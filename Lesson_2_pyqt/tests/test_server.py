import sys
import os
import unittest
from Lesson_2_pyqt.lib.variables import *
from Lesson_2_pyqt.server import client_message_handler

sys.path.append(os.path.join(os.getcwd(), '..'))

class Test_Server(unittest.TestCase):
    '''
    There is only 1 function in server.py that returns a result: client_message_handler
     the input is a dictionary with the required keys: ACTION, TIME, USER
    '''

    failed_dict = {RESPONSE: 400, ERROR: ERR400}
    success_dict_quest = {'error': '200:OK','msg': 'Welcome, Guest', 'responce': 200 }
    success_dict_auth_user = {'error': '200:OK', 'msg': 'Welcome, AUTH_USER', 'response': 200}

    def test_fail_message_object(self):
        '''
        The input of the function was not a dictionary
        :return:
        '''
        self.assertEqual(client_message_handler('AUTH_USER'), self.failed_dict)

    def test_no_key_action(self):
        '''
        Missing required ACTION key
        :return:
        '''
        self.assertEqual(client_message_handler({TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.failed_dict)

    def test_no_key_time(self):
        '''
        Missing required TIME key
        :return:
        '''
        self.assertEqual(client_message_handler({ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.failed_dict)

    def test_no_key_user(self):
        '''
        Missing required USER key
        :return:
        '''
        self.assertEqual(client_message_handler({ACTION: PRESENCE, TIME: '2'}), self.failed_dict)

    def test_wrong_action_value(self):
        '''
        The ACTION key was set to a value not in the list (PRESENCE,AUTH,MSG)
        :return:
        '''
        self.assertEqual(client_message_handler(
            {ACTION: 'abrakadabra', TIME: '2', USER: {ACCOUNT_NAME: 'GUEST'}}), self.failed_dict)

    def test_Guest_with_AUTH(self):
        '''
        If ACTION:AUTH and USER='Guest' (must be end name for authentication)
        :return:
        '''
        self.assertEqual(client_message_handler(
            {ACTION: AUTH, TIME: '2', USER: {ACCOUNT_NAME: 'Guest'}}), self.failed_dict)

    def test_Guest_with_MSG(self):
        '''
        If ACTION:AUTH and USER='Guest' (the guest cannot send a message).
        :return:
        '''
        self.assertEqual(client_message_handler(
            {ACTION: MSG, TIME: '2', USER: {ACCOUNT_NAME: 'Guest'}}), self.failed_dict)

    def test_Success_PRESENCE_Guest(self):
        '''
        If ACTION:PRESENCE and USER='Guest'
        :return:
        '''
        self.assertEqual(client_message_handler(
            {ACTION: PRESENCE, TIME: '2', USER: {ACCOUNT_NAME: 'Guest'}}), self.success_dict_guest)

    def test_Success_PRESENCE_not_Guest(self):
        '''
        If ACTION:PRESENCE and USER!='Guest'
        :return:
        '''
        self.assertEqual(client_message_handler(
            {ACTION: PRESENCE, TIME: '2', USER: {ACCOUNT_NAME: 'AUTH_USER'}}), self.success_dict_guest)

    def test_Success_AUTH_not_Guest(self):
        '''
        If ACTION:AUTH and USER!='Guest'
        :return:
        '''
        self.assertEqual(client_message_handler(
            {ACTION: AUTH, TIME: '2', USER: {ACCOUNT_NAME: 'AUTH_USER'}}), self.success_dict_auth_user)

    def test_Success_MSG_not_Guest(self):
        '''
        If ACTION:MSG and USER!='Guest'
        :return:
        '''
        self.assertEqual(client_message_handler(
            {ACTION: MSG, TIME: '2', USER: {ACCOUNT_NAME: 'AUTH_USER'}}), self.success_dict_auth_user)


if __name__ == '__main__':
    unittest.main()
