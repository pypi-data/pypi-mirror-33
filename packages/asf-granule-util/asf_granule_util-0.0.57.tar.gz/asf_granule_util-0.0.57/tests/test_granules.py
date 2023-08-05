import os
import unittest
import json
import datetime

from hypothesis import given, assume, strategies as st

import asf_granule_util as gu


class TestSentinelGranule(unittest.TestCase):
    def setUp(self):
        self.data_path = os.path.join(
            os.path.dirname(__file__), 'data'
        )

        test_granules_path = os.path.join(self.data_path, 'granules.json')
        with open(test_granules_path, 'r') as f:
            self.ga, self.gb = json.load(f)

        self.ga_obj = gu.SentinelGranule(self.ga)
        self.gb_obj = gu.SentinelGranule(self.gb)

    @given(st.from_regex(gu.SentinelGranule.pattern_exact))
    def test_granules_are_ascii(self, gran):
        gran.decode('ascii')
        self.assertTrue(gran)

    @given(st.text())
    def test_is_false_with_random_strings(self, random_text):
        assume(len(random_text) != 67)
        self.assertFalse(gu.SentinelGranule.is_valid(random_text))

    @given(st.text())
    def test_is_valid_fails_with_granule_in_string(self, random_text):
        assume(random_text != "")
        self.invalid_granules_raise_with(random_text)

        before = random_text + str(self.gb_obj)
        after = str(self.ga_obj) + random_text

        self.assertFalse(gu.SentinelGranule.is_valid(before))
        self.assertFalse(gu.SentinelGranule.is_valid(after))

    def invalid_granules_raise_with(self, test_str):
        with self.assertRaises(gu.InvalidGranuleException):
            gu.SentinelGranule(test_str)

    def test_datetime_objects(self):
        start_date = datetime.datetime(
            year=2015, month=8, day=29, hour=12, minute=37, second=51
        )
        stop_date = datetime.datetime(
            year=2015, month=8, day=29, hour=12, minute=38, second=21
        )

        self.assertEqual(
            start_date,
            self.ga_obj.get_start_date()
        )
        self.assertEqual(
            stop_date,
            self.ga_obj.get_stop_date()
        )

    def test_date_strings(self):
        start_date, stop_date = self.ga[17:25], self.ga[33:41]

        self.assertEqual(start_date, self.ga_obj.start_date)
        self.assertEqual(stop_date, self.ga_obj.stop_date)

    def test_time_strings(self):
        start_time, stop_time = self.ga[26:32], self.ga[42:48]

        self.assertEqual(start_time, self.ga_obj.start_time)
        self.assertEqual(stop_time, self.ga_obj.stop_time)

    def test_str_and_repr(self):
        path = os.path.join(self.data_path, 'correct_prints.json')
        with open(path, 'r') as f:
            correct = json.load(f)['sentinel']

        self.assertEqual(
            correct['str'],
            str(self.ga_obj)
        )

        self.assertEqual(
            correct['repr'],
            repr(self.ga_obj)
        )


if __name__ == '__main__':
    unittest.main()
