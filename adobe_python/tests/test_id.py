#!/usr/bin/python3

import json, os, platform, re, shutil, sys, unittest, time

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_files, class_subprocess
from adobe_python.jobs import id_service, stream_aep

dir_tmp = f"{package_dir}/tests/tmp"
dir_fpid = f"{project_dir}/myfolder/device/CB97A43915A948729C77CF6AC"

class TestIDservice(unittest.TestCase):
    
    def test_randomUniqueString(self):
        print(id_service.randomUniqueString())

    def test_fpidNew(self):
        print(stream_aep.fpidNew())

    def test_fpidNewMultiple(self):
        def makeDirectory(directory:str) -> None:  
            if isinstance(directory, str) and not os.path.exists(directory):
                os.makedirs(directory)
        
        def getTestCase(devicetype:str):
            match devicetype:
                case "desktop":
                    return "myfolder/testcases/test-desktop"
                case "mobile-app":
                    return "myfolder/testcases/test-mobile-app"
                case "mobile-browser":
                    return "myfolder/testcases/test-mobile-browser"
                case other:
                    return "myfolder/testcases/xxxx"
        
        def commandsLinux(timestamp:str, device:str, devicetype:str):
            testcase = getTestCase(devicetype)
            linux = f"python3 $HOME/myprojects/digital-analytics/adobe_python/jobs/stream_aep.py -re '[{{\"streamid\":\"xxxx\", \"device\":\"{device}\", \"dirlist\":[\"{testcase}\"]}}]'\n"
            class_files.Files({}).writeFile({"file":f"{dir_tmp}/{timestamp}-linux.txt", "content":f"# {devicetype}\n{linux}"})
        
        def commandsWindows(timestamp:str, device:str, devicetype:str):
            testcase = getTestCase(devicetype)
            windows = f"python3 $HOME/myprojects/digital-analytics/adobe_python/jobs/stream_aep.py -re '[{{\\\"streamid\\\":\\\"xxxx\\\", \\\"device\\\":\\\"{device}\\\", \\\"dirlist\\\":[\\\"{testcase}\\\"]}}]'\n"
            class_files.Files({}).writeFile({"file":f"{dir_tmp}/{timestamp}-windows.txt", "content":f"# {devicetype}\n{windows}"})
        
        def createIDs(timestamp:str, index:int, devicetype:str) -> str:
            if index == 0:
                device = stream_aep.fpidNew()
                stream_aep.getUserID({'device': device}, "ProfileID")    
                stream_aep.getUserID({'device': device}, "CustomerID")
                file = f"{dir_tmp}/device.txt"
                makeDirectory(dir_tmp)
                os.remove(file) if os.path.exists(file) else None
                class_files.Files({}).writeFile({"file":file, "content":device})
                commandsLinux(timestamp, device, devicetype) 
                commandsWindows(timestamp, device, devicetype) 
                print(devicetype, device)

        def copyIDs(timestamp:str, index:int, dev:dict, devicetype:str):
            if index > 0:
                c = class_files.Files({}).readFile(f'{dir_tmp}/device.txt')[0]
                source = f"{project_dir}/{c}"
                t = stream_aep.fpidNew()
                target = f"{project_dir}/{t}"
                class_subprocess.Subprocess({}).run(f"cp -a '{source}/.' '{target}'")
                commandsLinux(timestamp, t, devicetype) 
                commandsWindows(timestamp, t, devicetype)
                print(devicetype, target)
        
        def createDevice(timestamp:str, index:int, devicetype:dict):
            dev = createIDs(timestamp, index, devicetype)
            copyIDs(timestamp, index, dev, devicetype)
            
        funclist = ["desktop", "mobile-app", "mobile-browser"]
        timestamp = str(int(time.time() * 1000.0))
        [ createDevice(timestamp, i, x) for i, x in enumerate(funclist)]


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

