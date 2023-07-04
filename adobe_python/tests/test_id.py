#!/usr/bin/python3

import json, os, platform, re, sys, unittest, time

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_files, class_subprocess
from adobe_python.jobs import id_service, stream_aep

dir_fpid = f"{project_dir}/myfolder/device/CB97A43915A948729C77CF6AC"

class TestIDservice(unittest.TestCase):
    
    def test_randomUniqueString(self):
        print(id_service.randomUniqueString())

    def test_fpidNew(self):
        print(stream_aep.fpidNew())

    def test_fpidNewIdservice(self):
        id_service.fpidNew()
    
    def test_fpidGet(self):
        file = id_service.fpidGet(dir_fpid)
        command = f'powershell -command "Get-Content -Path {file}"' if re.search("^Windows", platform.platform()) else f"cat {file}"
        run = class_subprocess.Subprocess({}).run(command) if file else None
        print(run)

    def test_ecidNew(self):
        id_service.ecidNew(dir_fpid)

    def test_ecidRefresh(self):
        id_service.ecidRefresh()

    def test_storeResponse(self):
        c = class_files.Files({}).readJson(f"{project_dir}/myfolder/device/f2dc4a6f-bd5c-4bd7-bbc1-395191dd814e/response.json")
        handle = c.get('response',{}).get('handle')
        for p in handle:
            e = list(filter(None, [ x.get('id') for x in p.get('payload') if x.get('namespace',{}).get('code') == "ECID"]))
            print("e---", e)

if __name__ == '__main__':
    unittest.main()

