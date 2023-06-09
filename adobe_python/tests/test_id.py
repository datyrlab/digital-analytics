#!/usr/bin/python3

import json, os, platform, re, shutil, sys, unittest, time

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_files, class_subprocess
from adobe_python.jobs import stream

dir_tmp = f"{project_dir}/myfolder/device-tmp"

class TestIDservice(unittest.TestCase):
    
    def test_fpidNew(self):
        print(stream.fpidNew())

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
        
        def saveCommands(timestamp:str, device:str, devicetype:str):
            testcase = getTestCase(devicetype)
            linux = f"# {devicetype}\npython3 $HOME/myprojects/digital-analytics/adobe_python/jobs/stream.py -re '[{{\"streamid\":\"xxxx\", \"device\":\"{device}\", \"dirlist\":[\"{testcase}\"]}}]'\n"
            windows = f"# {devicetype}\npython $HOME/myprojects/digital-analytics/adobe_python/jobs/stream.py -re '[{{\\\"streamid\\\":\\\"xxxx\\\", \\\"device\\\":\\\"{device}\\\", \\\"dirlist\\\":[\\\"{testcase}\\\"]}}]'\n"
            content = linux if not re.search("^Windows", platform.platform()) else windows
            file = f"{dir_tmp}/{timestamp}.txt"
            class_files.Files({}).writeFile({"file":file, "content":f"# {devicetype}\n{linux}"})
            stream.printCol("cyan", content)
            
        def createIDs(timestamp:str, index:int, devicetype:str) -> str:
            if index == 0:
                device = stream.fpidNew()
                stream.getUserID({'device': device}, "ProfileID")    
                stream.getUserID({'device': device}, "CustomerID")
                file = f"{dir_tmp}/device.txt"
                makeDirectory(dir_tmp)
                os.remove(file) if os.path.exists(file) else None
                class_files.Files({}).writeFile({"file":file, "content":device})
                saveCommands(timestamp, device, devicetype) 
                print(devicetype, device)

        def copyIDs(timestamp:str, index:int, dev:dict, devicetype:str):
            if index > 0:
                c = class_files.Files({}).readFile(f'{dir_tmp}/device.txt')[0]
                source = f"{project_dir}/{c}"
                t = stream.fpidNew()
                target = f"{project_dir}/{t}"
                command  = f"cp -a '{source}/.' '{target}'" if not re.search("^Windows", platform.platform()) else f"powershell -Command \"Copy-Item -Path '{source}\*' -Destination '{target}' -PassThru\""
                class_subprocess.Subprocess({}).run(command)
                saveCommands(timestamp, t, devicetype) 
                print(devicetype, target)
        
        def createDevice(timestamp:str, index:int, devicetype:dict):
            dev = createIDs(timestamp, index, devicetype)
            copyIDs(timestamp, index, dev, devicetype)
            
        funclist = ["desktop", "mobile-app", "mobile-browser"]
        timestamp = str(int(time.time() * 1000.0))
        [ createDevice(timestamp, i, x) for i, x in enumerate(funclist)]


if __name__ == '__main__':
    unittest.main()

