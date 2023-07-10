#!/usr/bin/python3

import argparse, datetime, json, os, platform, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess
from adobe_python.jobs import ims_client, oauth, parse_reportsuite

timestamp_numeric = int(time.time() * 1000.0)
dir_admin = f"{project_dir}/myfolder/adobe"
dir_tmp = f"{project_dir}/myfolder/adobe/events-sent/tmp"

def main():
    request = parseArgs(sys.argv)
    makeRequest(request)

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

def useFile(data:dict) -> str:
    makeDirectory(dir_tmp)
    filepath = f"{dir_tmp}/data.json"
    os.remove(filepath) if os.path.exists(filepath) else None
    class_files.Files({}).writeFile({"file":filepath, "content":json.dumps(data, sort_keys=False, default=str)})
    return filepath

def getCommand_1_4(url:str, r:dict) -> str:
    if not re.search("admin/1.4", url):
        return None
    t = oauth.getAccessToken()
    s = []
    s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
    s.append(f"-X GET {r.get('get')}") if r.get('get') else s.append(f"-X POST {r.get('post')}") 
    s.append(f"-H \"Authorization: Bearer {t.get('token')}\"")
    s.append(f"-H \"x-api-key: {t.get('apikey')}\"")
    s.append("-H \"Content-Type: application/json\"")
    s.append(f"-d \"@{useFile(r.get('postdata'))}\"") if re.search("^Windows", platform.platform()) else s.append(f"-d '{json.dumps(r.get('postdata'))}'") 
    command = " ".join(s)
    return command

def getCommand_analytics(url:str, r:dict) -> str:
    if not re.search("analytics.adobe.io", url):
        return None
    urllist = url.split('/')
    t = oauth.getAccessToken()
    s = []
    s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
    s.append(f"-X GET {r.get('get')}") if r.get('get') else s.append(f"-X POST {r.get('post')}") 
    s.append(f"-H \"Accept: application/json\"")
    s.append(f"-H \"Authorization: Bearer {t.get('token')}\"")
    s.append("-H \"Content-Type: application/json\"")
    s.append(f"-H \"x-api-key: {t.get('apikey')}\"")
    s.append(f"-H \"x-proxy-global-company-id: {urllist[0]}\"")
    s.append(f"-d \"@{useFile(r.get('postdata'))}\"") if re.search("^Windows", platform.platform()) else s.append(f"-d '{json.dumps(r.get('postdata'))}'") 
    command = " ".join(s)
    return command

def getCommand_platform(url:str, r:dict) -> str:
    if not re.search("platform.adobe.io|platform-nld2.adobe.io", url):
        return None
    t = oauth.getAccessToken()
    s = []
    s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
    s.append(f"-X GET \"{r.get('get')}\"") if r.get('get') else s.append("-X POST {r.get('post')}") 
    #s.append(f"-H \"Accept: application/vnd.adobe.xed-id+json;version=1\"")
    s.append(f"-H \"Accept: application/vnd.adobe.xed-full+json;version=1\"")
    s.append(f"-H \"Authorization: Bearer {t.get('token')}\"")
    s.append(f"-H \"x-gw-ims-org-id: {t.get('orgid')}\"")
    s.append(f"-H \"x-api-key: {t.get('apikey')}\"")
    s.append(f"-H \"x-sandbox-name: {r.get('sandbox')}\"") if r.get('sandbox') else None
    command = " ".join(s)
    return command

def makeRequest(request:dict) -> None:
    url = request.get('get') if isinstance(request.get('get'), str) else request.get('post')
    funclist = [getCommand_1_4, getCommand_analytics, getCommand_platform]
    clist = list(filter(None,[f(url, request) for f in funclist]))
    command = clist[0] if len(clist) > 0 else None
    print(f"\033[1;37;44m{command}\033[0m") if not re.search("^Windows", platform.platform()) else print("command =====>", command, "\n") 
    run = class_subprocess.Subprocess({}).run(command) if command else None
    parseResult(request, run)  

def parseResult(request:dict, run:Any) -> None:
    try:
        tsinteger = getTimestamp()
        path = re.sub("REPLACETIMESTAMP", str(tsinteger), f"{project_dir}/{request.get('save')}") if request.get('save') else f"{project_dir}/myfolder/adobe-admin/{str(tsinteger)}"
        p = class_files.Files({}).fileProperties(path)
        path_format = f"{p.get('path')}/{p.get('name')}{p.get('file_extension')}" 
        os.remove(path_format) if os.path.exists(path_format) else None
        makeDirectory(os.path.dirname(path))
        response = json.loads("{\""+ run +"}")
        class_files.Files({}).writeFile({"file":f"{path_format}", "content":json.dumps(response, sort_keys=False, indent=4, default=str)})  
        print(f"\033[1;37;42mresponse: {path}\033[0m") if not re.search("^Windows", platform.platform()) else print("response =====>", path, "\n") 
    except Exception as e:
        path_format = f"{p.get('path')}/{p.get('name')}{p.get('file_extension')}" 
        class_files.Files({}).writeFile({"file":f"{path_format}", "content":json.dumps(json.loads("{"+ run), sort_keys=False, indent=4, default=str)})  
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e) 
    finally:
        parseResults(request, path_format)

def parseResults(request:dict, filepath:str):
    if re.search("-Get", filepath):
        class_files.Files({}).fileProperties(filepath)
        parse_reportsuite.parseJson([re.sub(project_dir, '', filepath)])

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


