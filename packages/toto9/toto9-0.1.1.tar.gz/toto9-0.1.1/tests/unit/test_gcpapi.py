#!/usr/bin/env python3

import warnings
import unittest
import googleapiclient.discovery

from toto9.gcp_api import GenericGcpApi

class TestGcpApi(unittest.TestCase):

    def setUp(self):
        # ignore the requests session open warning -
        # https://github.com/requests/requests/issues/3912
        warnings.filterwarnings(
            "ignore",
            category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")

        self.gcp_api = GenericGcpApi(
            'iam', 'v1'
        )

    def test_gcp_api(self):
        self.assertIsInstance(
            self.gcp_api.initialized_gcp_service(),
            googleapiclient.discovery.Resource
        )

if __name__ == '__main__':
    unittest.main()
