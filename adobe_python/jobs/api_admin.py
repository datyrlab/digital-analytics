#!/usr/bin/python3

import argparse, datetime, json, os, platform, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess
from adobe_python.jobs import ims_client

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

def getTimestamp() -> int:
    date_time = datetime.datetime.now()
    if re.search("^Windows", platform.platform()):
        return int(date_time.timestamp())
    return date_time.strftime('%s')

def getCommand14(r:dict) -> str:
    # adobe analytics 1.4
    if r.get('get') and re.search(r.get('get'), "admin/1.4") or r.get('post') and re.search(r.get('post'), "admin/1.4"):
        t = ims_client.getAccessToken()
        s = []
        s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
        s.append(f"-X GET {r.get('get')}") if r.get('get') else s.append("-X POST {r.get('post')}") 
        s.append(f"-H \"Authorization: Bearer {t.get('token')}\"")
        s.append(f"-H \"x-api-key: {t.get('apikey')}\"")
        s.append("-H \"Content-Type: application/json\"")
        s.append("-d '{r.get('postdata')}'") if r.get('postdata') else None
        command = " ".join(s)
        return command

def getCommand(r:dict) -> str:
    # default edge server
    if r.get('get') and not re.search(r.get('get'), "admin/1.4") or r.get('post') and not re.search(r.get('post'), "admin/1.4"):
        t = ims_client.getAccessToken()
        s = []
        s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
        s.append(f"-X GET \"{r.get('get')}\"") if r.get('get') else s.append("-X POST {r.get('post')}") 
        #if re.search("schema/registry/tenant", r.get('get')):
        s.append(f"-H \"Accept: application/vnd.adobe.xed-id+json\"")
        s.append(f"-H \"Authorization: Bearer {t.get('token')}\"")
        s.append(f"-H \"x-gw-ims-org-id: {t.get('orgid')}\"")
        s.append(f"-H \"x-api-key: {t.get('apikey')}\"")
        s.append(f"-H \"x-sandbox-name: {r.get('sandbox')}\"") if r.get('sandbox') else None
        command = " ".join(s)
        return command

def sendCommand(request:dict) -> None:
    command = getCommand(request)
    funclist = [getCommand14, getCommand]
    clist = list(filter(None,[f(request) for f in funclist]))
    command = clist[0] if len(clist) > 0 else None
    print("command ====>", command)

    run = class_subprocess.Subprocess({}).run(command) if command else None
    
    try:
        tsinteger = getTimestamp()
        path = f"{project_dir}/{request.get('save')}" if request.get('save') else f"{project_dir}/myfolder/adobe-admin/{tsinteger}"
        os.remove(path) if os.path.exists(path) else None
        makeDirectory(os.path.dirname(path))
        response = json.loads("{\""+ run +"}")
        class_files.Files({}).writeFile({"file":f"{path}-log.json", "content":json.dumps(response, sort_keys=False, default=str)})  
        class_files.Files({}).writeFile({"file":f"{path}-format.json", "content":json.dumps(response, sort_keys=False, indent=4, default=str)})  
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e) 

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


