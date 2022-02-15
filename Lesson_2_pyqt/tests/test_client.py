import sys
import os
import unittest
from Lesson_2_pyqt.lib.variables import *
from Lesson_2_pyqt.client import *

sys.path.append(os.path.join(os.getcwd(), '..'))


class Test_Client(unittest.TestCase):

    def test_get_user_success(self):
        '''
        Latin characters only, length from 3 to 25.
        :return: the username for authorization.
        '''
        self.assertEqual('NEW_USER', 'NEW_USER')

    def test_presence_guest(self):
        '''
        Checking the presence of the Guest
        :return: names of guest
        '''
        test = create_presence()
        # Force change the key in the dictionary
        test[TIME] = 2
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 2, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_presence_user(self):
        '''
        Checking the presence of the user (not Guest)
        :return: names of user
        '''
        test = create_presence(account_name='NEW_USER')
        test[TIME] = 2
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 2, USER: {ACCOUNT_NAME: 'NEW_USER'}})

    def test_create_action(self):
        '''
          The function returns a dictionary with the message text
          account_name and action are required, msg is None by default, filled in this test
        :return:dictionary with the message text
        '''
        test = create_action(account_name='NEW_USER', action='action', msg='New_Message')
        test[TIME] = 2
        self.assertEqual(test, {ACTION: 'action', TIME: 2, USER: {ACCOUNT_NAME: 'NEW_USER'}, MESSAGE: 'New_Message'})

    def test_create_action_none_msg(self):
        '''
        The function returns a dictionary with the message text
          account_name and action are required, msg is None by default.
        :return:dictionary with the message text
        '''
        test = create_action(account_name='NEW_USER', action='action')
        test[TIME] = 2
        self.assertEqual(test, {ACTION: 'action', TIME: 2, USER: {ACCOUNT_NAME: 'NEW_USER'}, MESSAGE: None})

    def test_process_handler_not_200ok(self):
        '''
        Checking the response from the server, if the required RESPONCE field is missing, there should be a 400 error
        :return: answer from the server
        '''
        self.assertEqual(process_handler({MESSAGE: 'msg_srv'}), '400:Bad request')

    def test_process_handler_ok(self):
        '''
        Checking the response from the server, the correct response is code 200
        for {RESPONSE:200, MSG:"not an empty message"}
        :return: answer from the server
        '''
        self.assertEqual(process_handler({RESPONSE: 200, MESSAGE: 'msg_srv'}), 'msg_srv')


if __name__ == '__main__':
    unittest.main()

