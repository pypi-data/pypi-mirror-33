
import unittest
import os
import json

import asf_granule_util as gu


class TestDownloadPairs(unittest.TestCase):
    def setUp(self):
        path = os.path.dirname(__file__)
        test_granules_path = os.path.join(
            path, 'data/granules.json'
        )

        with open(test_granules_path, 'r') as f:
            self.ga, self.gb = json.load(f)

        self.ga_obj = gu.SentinelGranule(self.ga)
        self.gb_obj = gu.SentinelGranule(self.gb)

        self.pair = gu.SentinelGranulePair(self.ga_obj, self.gb_obj)

        self.directory = '.'

        username, password = get_creds(os.path.join(path, '..', 'creds.txt'))
        self.creds = {
            'username': username,
            'password': password
        }

    def test_pair_download(self):
        pass
        # gu.download(
            # self.pair,
            # credentials=self.creds,
            # progess_bar=True
        # )


def get_creds(path):
    with open(path, 'r') as f:
        out = f.read().strip().split()

    return out


if __name__ == "__main__":
    unittest.main()
