
import unittest
from fredapi import Fred


class TestFred(unittest.TestCase):

    def setUp(self):
        self.fred = Fred()

    def testGetSeries(self):
        s = self.fred.get_series('SP500', observation_start='9/2/2014', observation_end='9/5/2014')
        self.assertEqual(s.ix['9/2/2014'], 2002.28)
        self.assertEqual(len(s), 4)

        info = self.fred.get_series_info('PAYEMS')
        self.assertEqual(info['title'], 'All Employees: Total nonfarm')

        # invalid series id
        self.assertRaises(ValueError, self.fred.get_series, 'invalid')
        self.assertRaises(ValueError, self.fred.get_series_info, 'invalid')

        # invalid parameter
        try:
            self.fred.get_series('SP500', observation_start='invalid-datetime-str')
            self.assertTrue(False, 'previous line should have thrown a ValueError')
        except ValueError:
            pass

    def tearDown(self):
        return
