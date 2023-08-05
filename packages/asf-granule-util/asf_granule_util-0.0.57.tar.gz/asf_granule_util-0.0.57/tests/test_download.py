import unittest
import os
import json

from .timeout import timeout, TimeoutException
import asf_granule_util as gu


class TestDownload(unittest.TestCase):
    def setUp(self):
        path = os.path.dirname(__file__)
        test_granules_path = os.path.join(
            path, 'data/granules.json'
        )

        with open(test_granules_path, 'r') as f:
            self.ga, self.gb = json.load(f)

        self.ga_obj = gu.SentinelGranule(self.ga)
        self.gb_obj = gu.SentinelGranule(self.gb)

        self.directory = 'granules/test'

        username, password = get_creds(os.path.join(path, '..', 'creds.txt'))
        self.creds = {
            'username': username,
            'password': password
        }

    def test_invalid_credentials_raise(self):
        with self.assertRaises(gu.InvalidCredentialsException):
            gu.download(
                to_download=self.ga_obj,
                credentials={
                    'username': 'invalid',
                    'password': 'creds'
                },
                directory=self.directory
            )

    def test_wrong_cred_keys(self):
        bad_creds = [
            {'usrname': 'hello', 'password': 'world'},
            {'username': 'hello', 'passwor': 'world'}
        ]

        for cred in bad_creds:
            with self.assertRaises(KeyError):
                gu.download(
                    to_download=self.ga_obj,
                    credentials=cred,
                    directory=self.directory
                )

        self.cleanup(self.ga_obj)

    def test_download_starts_with_bar(self):
        self.download_test(
            self.ga,
            has_bar=True
        )

    def test_download_starts_without_bar(self):
        self.download_test(
            self.gb_obj,
            has_bar=False
        )

    def download_test(self, granule, has_bar):
        with self.assertRaises(TimeoutException):
            self.download_with_timeout(granule, has_bar=has_bar)

        dl_started = self.has_download_started(granule)
        self.assertTrue(dl_started)

        self.cleanup(granule)

    def download_with_timeout(self, granule, has_bar):
        with timeout(5):
            gu.download(
                to_download=granule,
                credentials=self.creds,
                directory=self.directory,
                progress_bar=has_bar,
                unzip=False
            )

    def has_download_started(self, granule):
        path = self.get_full_download_path(granule)

        return os.path.exists(path)

    def cleanup(self, granule):
        dl_path = self.get_full_download_path(granule)

        if os.path.exists(dl_path):
            os.remove(dl_path)
            os.rmdir(self.directory)

    def get_full_download_path(self, granule):
        return os.path.join(self.directory, str(granule) + '.zip')


def get_creds(path):
    with open(path, 'r') as f:
        out = f.read().strip().split()

    return out


if __name__ == "__main__":
    unittest.main()
