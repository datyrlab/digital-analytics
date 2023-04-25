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
directory = f"{project_dir}/myfolder/logs"

def main():
    request = parseArgs(sys.argv)
    parseRequest(request)

def parseArgs(argv) -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-re', '--request', dest='request')
    namespace = parser.parse_known_args(argv)[0]
    
    args = {k: v for k, v in vars(namespace).items() if v is not None}
    request = json.loads(args.get('request')) if isinstance(args.get('request'), str) else None
    return request

def parseRequest(r:dict) -> None:
    if isinstance(r, dict) and isinstance(r.get('eventlist'), list) and len(r.get('eventlist')) > 0:
        [(lambda x: sendCommand(i, r.get('url'), f"{project_dir}/{x}"))(x) for i, x in enumerate(r.get('eventlist'))]
        
def getTimestamp() -> int:
    date_time = datetime.datetime.now()
    if re.search("^Windows", myplatform):
        return date_time.timestamp()
    return date_time.strftime('%s')
    
def getCommand(url:str, filepath:str) -> tuple:
    c = class_files.Files({}).readFile(filepath)
    if re.search(".xml$", filepath):
        tsinteger = getTimestamp()
        data = re.sub(r'timestamp><', f"timestamp>{tsinteger}<", "".join(c)) if isinstance(c, list) and len(c) > 0 else None
        logfile = f"{directory}/{tsinteger}.xml" 
        return {"logfile":logfile, "data":data, "command":f"curl -X POST \"{url}\" -H \"Accept: application/xml\" -H \"Content-Type: application/xml\" -d \"{data}\""}
    
    elif re.search(".json$", filepath):
        tsformat = getTimestampFormat()
        
        """t = ims_client.getAccessToken()
        data = re.sub(r'timestamp><', f"timestamp>{tsinteger}<", "".join(c)) if isinstance(c, list) and len(c) > 0 else None
        logfile = f"{directory}/{tsinteger}.json"
        s = []
        s.append(f"curl -X POST \"https://server.adobedc.net/ee/v2/interact?dataStreamId=xxxxxx\"")
        s.append(f"-H \"Authorization: Bearer {t.get('token')}\"")
        s.append(f"-H \"x-gw-ims-org-id: {t.get('orgid')}\"")
        s.append(f"-H \"x-api-key: {t.get('apikey')}\"")
        s.append(f"-H \"Content-Type: application/json\"")
        s.append(f"-d \"{data}\"")
        command = " ".join(s)
        print("command: ", command)
        return {"logfile":logfile, "data":data, "command":command}
        """

def getTimestampFormat() -> int:
    date_time = datetime.datetime.utcnow()
    t = date_time.strftime("%Y-%m-%dT%H:%M:%f:%z")
    print(t)

    
def sendCommand(index:int, url:str, filepath:str) -> None:
    d = getCommand(url, filepath)
    if isinstance(d, dict):
        run = class_subprocess.Subprocess({}).run(d.get('command'))
        if re.search("SUCCESS", run):
            makeDirectory(directory)
            class_files.Files({}).writeFile({"file":d.get('logfile'), "content":d.get('data')})     

def makeDirectory(directory:str) -> None:
    if isinstance(directory, str) and not os.path.exists(directory):
        os.makedirs(directory)

if __name__ == '__main__':
    time_start = time.time()
    main()
    #stop timer
    if re.search("^Linux", myplatform):
        time_finish = time.time()
        start_time = datetime.datetime.fromtimestamp(int(time_start)).strftime('%Y-%m-%d %H:%M:%S')
        finish_time = datetime.datetime.fromtimestamp(int(time_finish)).strftime('%Y-%m-%d %H:%M:%S')
        finish_seconds = round(time_finish - time_start,3)
        t = class_converttime.Converttime(config={}).convert_time({"timestring":finish_seconds}) 
        print(f"Time start: {start_time}")
        print(f"Time finish: {finish_time} | Total time: {t.get('ts')}")


