#!/usr/bin/python3

import argparse, datetime, json, os, platform, re, sys, time
from typing import Any, Callable, Dict, Optional, Union

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess
from adobe_python.jobs import stream

timestamp_numeric = int(time.time() * 1000.0)
dir_tmp = f"{project_dir}/myfolder/device-tmp"

def main():
    request = parseArgs(sys.argv)
    funclist = ["desktop", "mobile-app", "mobile-browser"]
    [createDevice(request, str(timestamp_numeric), i, x) for i, x in enumerate(funclist)]

def parseArgs(argv) -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-re', '--request', dest='request')
    namespace = parser.parse_known_args(argv)[0]
    args = {k: v for k, v in vars(namespace).items() if v is not None}
    request = json.loads(args.get('request')) if isinstance(args.get('request'), str) else None
    return request

def printCol(colour, text) -> None:
    colours = {'black': '30', 'red': '31', 'green': '32', 'yellow': '33', 'blue': '34', 'magenta': '35', 'cyan': '36', 'white': '37'}
    fgcode = colours[colour]
    print(f"\033[{fgcode}m{text}\033[0m")

def createDevice(request:dict, timestamp:str, index:int, devicetype:dict) -> None:
    dev = createIDs(request, timestamp, index, devicetype)
    copyIDs(request, timestamp, index, dev, devicetype)
    
def createIDs(request:dict, timestamp:str, index:int, devicetype:str) -> str:
    if index == 0:
        device = stream.fpidNew()
        stream.getUserID({'device': device}, "ProfileID")    
        stream.getUserID({'device': device}, "CustomerID")
        file = f"{dir_tmp}/device.txt"
        makeDirectory(dir_tmp)
        os.remove(file) if os.path.exists(file) else None
        class_files.Files({}).writeFile({"file":file, "content":device})
        saveCommands(request, timestamp, device, devicetype) 

def copyIDs(request:dict, timestamp:str, index:int, dev:dict, devicetype:str) -> None:
    if index > 0:
        c = class_files.Files({}).readFile(f'{dir_tmp}/device.txt')[0]
        source = f"{project_dir}/{c}"
        t = stream.fpidNew()
        target = f"{project_dir}/{t}"
        command  = f"cp -a '{source}/.' '{target}'" if not re.search("^Windows", platform.platform()) else f"powershell -Command \"Copy-Item -Path '{source}\*' -Destination '{target}' -PassThru\""
        class_subprocess.Subprocess({}).run(command)
        saveCommands(request, timestamp, t, devicetype) 

def getTestCase(devicetype:str) -> str:
    match devicetype:
        case "desktop":
            return "myfolder/testcases/test-desktop"
        case "mobile-app":
            return "myfolder/testcases/test-mobile-app"
        case "mobile-browser":
            return "myfolder/testcases/test-mobile-browser"
        case other:
            return "myfolder/testcases/xxxx"

def saveCommands(request:dict, timestamp:str, device:str, devicetype:str) -> None:
    testcase = getTestCase(devicetype)
    streamid = request.get('streamid') if isinstance(request.get('streamid'), str) else "xxxx"
    linux = f"# {devicetype}\npython3 $HOME/myprojects/digital-analytics/adobe_python/jobs/stream.py -re '[{{\"streamid\":\"{streamid}\", \"device\":\"{device}\", \"dirlist\":[\"{testcase}\"]}}]'\n"
    windows = f"# {devicetype}\npython $HOME/myprojects/digital-analytics/adobe_python/jobs/stream.py -re '[{{\\\"streamid\\\":\\\"{streamid}\\\", \\\"device\\\":\\\"{device}\\\", \\\"dirlist\\\":[\\\"{testcase}\\\"]}}]'\n"
    content = linux if not re.search("^Windows", platform.platform()) else windows
    file = f"{dir_tmp}/{timestamp}.txt"
    class_files.Files({}).writeFile({"file":file, "content":content})
    stream.printCol("cyan", content)
    
def makeDirectory(directory:str) -> None:  
    if isinstance(directory, str) and not os.path.exists(directory):
        os.makedirs(directory)


if __name__ == '__main__':
    time_start = time.time()
    main()
    if not re.search("^Windows", platform.platform()):
        time_finish = time.time()
        start_time = datetime.datetime.fromtimestamp(int(time_start)).strftime('%Y-%m-%d %H:%M:%S')
        finish_time = datetime.datetime.fromtimestamp(int(time_finish)).strftime('%Y-%m-%d %H:%M:%S')
        finish_seconds = round(time_finish - time_start,3)
        t = class_converttime.Converttime(config={}).convert_time({"timestring":finish_seconds}) 
        print(f"Time start: {start_time}")
        print(f"Time finish: {finish_time} | Total time: {t.get('ts')}")


