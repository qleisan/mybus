import unittest
from helpers import *
from datetime import datetime

class TestHelperFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setupClass')

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass')


    def test_getcolor(self):
        t = datetime(2016, 11, 15, 21, 59, 25, 608206)
        self.assertEqual(getcolor(t), ('white', 'black', 'blue'))

    def test_apa(selfself):
        outDict = {"aaa": 10+10,
                   "bbb": "qqq"+"www"}
        print(outDict)

if __name__ == '__main__':
    unittest.main()
