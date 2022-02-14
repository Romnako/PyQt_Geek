import sys
sys.path.append('../')
from Lesson_2_pyqt.client import create_presence, process_response_ans
import unittest
from Lesson_2_pyqt.lib.errors import ReqFieldMissingError, ServerError
from Lesson_2_pyqt.lib.variables import *


class TestClass(unittest.TestCase):

    def test_def_presense(self):
        test = create_presence('Guest')
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENSE, TIME: 1.1, USER: {ACCOUNT_NAME; 'Guest'}})

    def test_200_ans(self):
        self.assertEqual(process_response_ans({RESPONSE: 200}), '200: OK')

    def test_400_ans(self):
        self.assertRaises(ServerError, process_response_ans, {RESPONSE: 400, ERROR: 'Bad Request'})

    def test_no_response(self):
        self.assertRaises(ReqFieldMissingError, process_response_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
