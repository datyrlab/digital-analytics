#!/usr/bin/python3

import json, os, platform, re, sys, unittest, time

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.jobs import ims_client

class TestJWTaccessToken(unittest.TestCase):

    def test_JWTaccesstoken(self):
        print(ims_client.getAccessToken())


if __name__ == '__main__':
    unittest.main()

