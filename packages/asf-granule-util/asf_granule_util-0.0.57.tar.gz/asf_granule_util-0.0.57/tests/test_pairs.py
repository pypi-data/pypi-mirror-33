import unittest
import os
import json
import datetime as dt

import asf_granule_util as gu


class TestPairs(unittest.TestCase):
    def setUp(self):
        self.data_path = os.path.join(
            os.path.dirname(__file__), 'data'
        )

        test_granules_path = os.path.join(self.data_path, 'granules.json')
        with open(test_granules_path, 'r') as f:
            self.ga, self.gb = json.load(f)

        self.ga_obj = gu.SentinelGranule(self.ga)
        self.gb_obj = gu.SentinelGranule(self.gb)

        self.pair = gu.SentinelGranulePair(
            self.ga_obj,
            self.gb_obj
        )

    def test_make_pair_keys(self):
        self.assertEqual(self.gb_obj, self.pair.master)
        self.assertEqual(self.ga_obj, self.pair.slave)

    def test_str_and_repr(self):
        path = os.path.join(self.data_path, 'correct_prints.json')
        with open(path, 'r') as f:
            correct = json.load(f)['pair']

        self.assertEqual(
            correct['str'],
            str(self.pair)
        )

        self.assertEqual(
            correct['repr'],
            repr(self.pair)
        )

    def test_tuple(self):
        g_tuple = (self.gb_obj, self.ga_obj)

        self.assertEqual(g_tuple, self.pair.tuple)

    def test_time_delta(self):
        delta = dt.timedelta(days=544, hours=13, minutes=52, seconds=59)

        self.assertEqual(self.pair.get_time_delta(), delta)


if __name__ == '__main__':
    unittest.main()
