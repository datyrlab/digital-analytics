#!/usr/bin/python3

import argparse, datetime, hashlib, json, os, platform, random, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess
from adobe_python.jobs import ims_client

timestamp_numeric = int(time.time() * 1000.0)
dir_tmp = f"{project_dir}/myfolder/adobe-events-sent/tmp"
dir_log = f"{project_dir}/myfolder/adobe-events-sent/logs"
dir_response = f"{project_dir}/myfolder/adobe-events-sent/response"
testcode = "alpha"

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
        [(lambda x: sendCommand(i, r, f"{project_dir}/{x}"))(x) for i, x in enumerate(r.get('eventlist'))]
        
def getTimestamp() -> int:
    date_time = datetime.datetime.now()
    if re.search("^Windows", platform.platform()):
        return int(date_time.timestamp())
    return date_time.strftime('%s')
    
def getTimestampFormat() -> int:
    s = datetime.datetime.utcnow().isoformat()
    return f"{s[:-3]}Z"

def randomUniqueString() -> str:
    # alpha-numeric
    import uuid
    return uuid.uuid4().hex[:25].upper()

def replaceString(s:str, tsinteger:str) -> str:
    replacelist = [
        ('timestamp><', f"timestamp>{tsinteger}<"),
        ('REPLACETESTCODE', testcode),
        ('REPLACEORDERNUMBER', tsinteger)
    ]
    for find, replace in replacelist:
        s = re.sub(find, replace, s)
    return s

def getIdentityMap(r:dict) -> dict:
    if isinstance(r.get('identityMap'), dict):
        return r.get('identityMap')
    filepath = f"{project_dir}/{r.get('identityMap')}" if isinstance(r.get('identityMap'), str) and os.path.exists(f"{project_dir}/{r.get('identityMap')}") else f"{project_dir}/adobe_python/json/profilelist.json"
    r = class_files.Files({}).readJson(filepath) if os.path.exists(filepath) else None
    result = random.choice(r) if isinstance(r, list) and len(r) > 0 else {"identityMap":[{"Email_LC_SHA256": [{"id":"bfdb4e7af1447741addddba0f7c8ff34114be39926cb1e7e71b69b3b9c49821b", "primary": True}]}]}
    return result.get('identityMap')

def getCommand(r:dict, filepath:str) -> dict:
    url = r.get('url')
    streamid = r.get('streamid')
    tsinteger = getTimestamp()
    c = class_files.Files({}).readFile(filepath)
    cstr = replaceString("".join(c), str(tsinteger)) if isinstance(c, list) and len(c) > 0 else None

    if re.search(".xml$", filepath):
        return {"data":cstr, "time":tsinteger, "command":f"curl -X POST \"{url}\" -H \"Accept: application/xml\" -H \"Content-Type: application/xml\" -d \"{cstr}\""}
    
    elif re.search(".json$", filepath):
        tsformat = getTimestampFormat()
        t = ims_client.getAccessToken()
        data = json.loads(cstr) if isinstance(cstr, str) else None
        if isinstance(data, dict) and isinstance(data.get('event',{}).get('xdm'), dict):
            identitymap = getIdentityMap(r)
            profileid = [(lambda x: x)(x) for x in identitymap.get('ProfileID') if x.get('id')][0].get('id') if isinstance(identitymap.get('ProfileID'), list) else None
            data["event"]["xdm"]["_id"] = randomUniqueString()
            data["event"]["xdm"]["timestamp"] = tsformat
            if not isinstance(data.get('event',{}).get('xdm',{}).get('identityMap'), dict):
                data["event"]["xdm"]["identityMap"] = identitymap
            if not isinstance(data.get('event',{}).get('xdm',{}).get('cea'), dict):
                data["event"]["xdm"]["cea"] = {"profileid":profileid}
            else: 
                data["event"]["xdm"]["cea"]["profileid"] = profileid
                
        s = []
        s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
        s.append(f"-X POST \"https://server.adobedc.net/ee/v2/interact?dataStreamId={streamid}\"")
        s.append(f"-H \"Authorization: Bearer {t.get('token')}\"")
        s.append(f"-H \"x-gw-ims-org-id: {t.get('orgid')}\"")
        s.append(f"-H \"x-api-key: {t.get('apikey')}\"")
        s.append(f"-H \"Content-Type: application/json\"")
        s.append(f"-d \"@{useFile(data)}\"") if re.search("^Windows", platform.platform()) else s.append(f"-d '{json.dumps(data)}'")
        command = " ".join(s)
        return {"date":datetime.datetime.now().strftime("%Y%m%d"), "time":tsinteger, "data":data, "command":command}

def useFile(data:dict) -> str:
    makeDirectory(dir_tmp)
    filepath = f"{dir_tmp}/data.json"
    os.remove(filepath) if os.path.exists(filepath) else None
    class_files.Files({}).writeFile({"file":filepath, "content":json.dumps(data, sort_keys=False, default=str)})
    return filepath

def sendCommand(index:int, request:dict, filepath:str) -> None:
    r = getCommand(request, filepath)
    if isinstance(r, dict):
        print("data =====>", json.dumps(r.get('data')), "\n")
        run = class_subprocess.Subprocess({}).run(r.get('command'))
        if re.search(".xml$", filepath) and re.search("SUCCESS", run):
            directory_log = f"{dir_log}/{r.get('date')}"
            makeDirectory(directory_log)
            class_files.Files({}).writeFile({"file":f"{directory_log}/{r.get('time')}.xml", "content":r.get('data')})  
        elif re.search(".json$", filepath):
            try:
                directory_response = f"{dir_response}/{r.get('date')}"
                directory_log = f"{dir_log}/{r.get('date')}"
                makeDirectory(directory_response)
                makeDirectory(directory_log)
                response = json.loads("{\""+ run +"}") if re.search("^requestId", run) else run
                class_files.Files({}).writeFile({"file":f"{directory_response}/{response.get('requestId')}_{r.get('time')}.json", "content":json.dumps(response, sort_keys=False, default=str)}) if re.search("^requestId", run) else None 
                class_files.Files({}).writeFile({"file":f"{directory_log}/{r.get('time')}-log.json", "content":json.dumps({"request":r.get('data'), "response":response}, sort_keys=False, default=str)})  
                class_files.Files({}).writeFile({"file":f"{directory_log}/{r.get('time')}-format.json", "content":json.dumps({"request":r.get('data'), "response":response}, sort_keys=False, indent=4, default=str)})  
                print("requestId:", response.get('requestId')) if isinstance(response, dict) else print("error:", run)
                time.sleep(random.randint(2, 8)) if len(request.get('eventlist')) > 1 and request.get('delay') else None
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
        t = class_converttime.Converttime({}).convert_time({"timestring":finish_seconds}) 
        print(f"Time start: {start_time}")
        print(f"Time finish: {finish_time} | Total time: {t.get('ts')}")


