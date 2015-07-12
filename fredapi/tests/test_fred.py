
import unittest
from fredapi import Fred
from datetime import datetime


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

    def testSearch(self):
        personal_income_series = self.fred.search_by_release(175, limit=3, order_by='popularity', sort_order='desc')
        series_ids = ['PCPI06037', 'PCPI06075', 'PCPI34039']
        for series_id in series_ids:
            self.assertTrue(series_id in personal_income_series.index)
            self.assertEqual(personal_income_series.ix[series_id, 'observation_start'], datetime(1969, 1, 1))

    def tearDown(self):
        return
