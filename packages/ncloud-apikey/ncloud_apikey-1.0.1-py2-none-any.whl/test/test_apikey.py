# coding: utf-8

from __future__ import absolute_import

import unittest

import ncloud_apikey
from ncloud_apikey.ncloud_key import NcloudKey

class TestApikey(unittest.TestCase):
    """Apikey unit test stubs"""

    def tearDown(self):
        pass

    def test_get_login_key_list(self):
        """Test case for apikey file """
        print(NcloudKey().keys())
        print(NcloudKey().keys())
        print(NcloudKey({'access_key':'abc', 'secret_key':'def'}).keys())
        print(NcloudKey().keys())

        nkey = NcloudKey()
        print(nkey.keys())
        print(nkey.keys())

        pass

if __name__ == '__main__':
    unittest.main()
