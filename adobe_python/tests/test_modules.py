#!/usr/bin/python3

import json, os, platform, re, sys, unittest, time

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)

class TestModules(unittest.TestCase):

    def test_platform(self):
        print(platform.platform())

    def test_env(self):
        print(os.environ)

    def test_env_adobe(self):
        print("ADOBE_CONFIG", os.environ['ADOBE_CONFIG'])



if __name__ == '__main__':
    unittest.main()

