#!/usr/bin/python3

import argparse, datetime, json, os, platform, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess
from adobe_python.jobs import ims_client

myplatform = platform.platform()
timestamp_numeric = int(time.time() * 1000.0)
dir_admin = f"{project_dir}/myfolder/adobe-admin"

def main():
    request = parseArgs(sys.argv)
    sendCommand(request)

def parseArgs(argv) -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-re', '--request', dest='request')
    namespace = parser.parse_known_args(argv)[0]
    
    args = {k: v for k, v in vars(namespace).items() if v is not None}
    request = json.loads(args.get('request')) if isinstance(args.get('request'), str) else None
    return request

def getCommand(r:dict) -> str:
    t = ims_client.getAccessToken()
    s = []
    s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
    s.append("-X GET r.get('get')") if r.get('get') else s.append("-X POST r.get('post')") 
    s.append(f"-H \"Authorization: Bearer {t.get('token')}\"")
    s.append(f"-H \"x-gw-ims-org-id: {t.get('orgid')}\"")
    s.append(f"-H \"x-api-key: {t.get('apikey')}\"")
    s.append("-H 'x-sandbox-name: r.get('sandbox')'")
    command = " ".join(s)
    return command

def sendCommand(request:dict) -> None:
    command = getCommand(request)
    run = class_subprocess.Subprocess({}).run(command)
    print(run)

    #if re.search("SUCCESS", run):
    #    makeDirectory(directory)
    #    class_files.Files({}).writeFile({"file":logfile, "content":data})     

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


