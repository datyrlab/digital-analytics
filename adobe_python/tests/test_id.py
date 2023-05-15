#!/usr/bin/python3

import json, os, platform, re, sys, unittest, time

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.jobs import id_service

class TestIDservice(unittest.TestCase):

    def test_fpid(self):
        id_service.fpid()

    def test_ecidNew(self):
        id_service.ecidNew()

    def test_ecidRefresh(self):
        id_service.ecidRefresh()

if __name__ == '__main__':
    unittest.main()

