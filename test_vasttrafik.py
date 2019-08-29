import unittest
from vasttrafik import *
from config import CONSUMER_KEY, CONSUMER_SECRET

from datetime import datetime

BERGSPRANGAREGATAN = '9022014001390001'
ENGDAHLSGATAN = '9022014002230002'

class MyTestCase(unittest.TestCase):
    def test_something(self):
        a = Server(CONSUMER_KEY, CONSUMER_SECRET)
        t = datetime(2019,8,18,22,8,0)
        b = a.getDepartures(BERGSPRANGAREGATAN, t)
        mylist = b.search("18", "A")
        mylist.extend(b.search("52", "A"))
        # TODO: list must be sorted
        #pprint(mylist)

        print(int(59.2 / 60))
        print(int(-59.2 / 60))
        print(int(-61.2 / 60))
        print(int(-1.2 / 60))
        print(int(-1.2 // 60))
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
