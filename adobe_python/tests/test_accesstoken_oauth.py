#!/usr/bin/python3

import json, os, platform, re, sys, unittest, time

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.jobs import oauth
from adobe_python.classes import class_converttime, class_files, class_subprocess 

class TestOauthAccessToken(unittest.TestCase):

    def setUp(self):
        self.t = oauth.getAccessToken()
    
    def test_showToken(self):
        print(self.t)

    def listClientSecrets(self):
        if isinstance(self.access_token, str):
            s = []
            s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
            s.append(f"-X GET \"https://api.adobe.io/console/organizations/{self.env.get('oauthorgid')}/credentials/{self.env.get('oauthcredentialid')}/secrets\"")
            s.append(f"-H \"-H 'Authorization: Bearer {self.access_token}'\"")
            s.append(f"-H \"x-api-key: {self.env.get('apikey')}\"")
            command = " ".join(s)
            run = class_subprocess.Subprocess({}).run(command)
            print(run)


if __name__ == '__main__':
    unittest.main()

