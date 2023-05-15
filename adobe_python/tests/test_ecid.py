#!/usr/bin/python3

import json, os, platform, re, sys, unittest, time

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.jobs import id_service

class TestIDservice(unittest.TestCase):

    def test_idNew(self):
        id_service.idNew()

    def idNew(self):
        id_service.idRefresh()


if __name__ == '__main__':
    unittest.main()

