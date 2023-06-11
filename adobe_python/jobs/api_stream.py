#!/usr/bin/python3

import argparse, datetime, hashlib, json, os, platform, random, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
import uuid
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess
from adobe_python.jobs import id_service, oauth

timestamp_numeric = int(time.time() * 1000.0)
dir_tmp = f"{project_dir}/myfolder/adobe/events-sent/tmp"
dir_log = f"{project_dir}/myfolder/adobe/events-sent/logs"
dir_response = f"{project_dir}/myfolder/adobe/events-sent/response"
testcode = None

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
        t = oauth.getAccessToken()
        [(lambda x: makeRequest(i, t, r, f"{project_dir}/{x}"))(x) for i, x in enumerate(r.get('eventlist'))]
        
def getTimestamp():
    increment = 300 # spoof receivedTimestamp by x seconds
    now = datetime.datetime.now()
    date = now.strftime("%Y%m%d")
    f = now.timestamp()
    utc_iso = datetime.datetime.utcfromtimestamp(f).isoformat()
    utc_iso_increment = datetime.datetime.utcfromtimestamp(f+increment).isoformat()
    return {"date":date, "float":f, "integer":str(int(f)), "utc_iso":f"{utc_iso[:-3]}Z", "utc_iso_increment":f"{utc_iso_increment[:-3]}Z"}

def randomUniqueString() -> str:
    return uuid.uuid4().hex[:25].upper()

def replaceString(t:dict, ts:dict, hitid:str, identitymap:dict, s:str) -> str:
    fpid = [ x.get('id') for x in identitymap.get('FPID') ][0] if isinstance(identitymap.get('FPID'), list) else None
    authenticatedstate = [ x.get('authenticatedState') for x in identitymap.get('FPID') ][0] if isinstance(identitymap.get('FPID'), list) else "ambiguous"
    ecid = [ x.get('id') for x in identitymap.get('ECID') ][0] if isinstance(identitymap.get('ECID'), list) else None
    customerid = [ x.get('id') for x in identitymap.get('CustomerID') ][0] if isinstance(identitymap.get('CustomerID'), list) else None  
    profileid = [ x.get('id') for x in identitymap.get('ProfileID') ][0] if isinstance(identitymap.get('ProfileID'), list) else None
    if not customerid:
        s = re.sub('"customerid":"REPLACECUSTOMERID",', "", s)
    if not profileid:
        s = re.sub('"profileid":"REPLACEPROFILEID",', "", s)
    replacelist = [
        ('REPLACEORDERNUMBER', ts.get('integer')),
        ('REPLACEORGID', t.get('orgid')),
        ('REPLACEREFERENCE', hitid),
        ('REPLACELOGINSTATUS', authenticatedstate),
        ('REPLACETERMINALID', randomUniqueString()),
        ('REPLACETIMESTAMP', ts.get('utc_iso')),
        ('timestamp><', f"timestamp>{ts.get('integer')}<")
    ]
    replacelist.append(('REPLACEECID', ecid)) if ecid else None
    replacelist.append(('REPLACECUSTOMERID', customerid)) if customerid else None
    replacelist.append(('REPLACEPROFILEID', profileid)) if profileid else None
    replacelist.append(('REPLACEFPID', fpid)) if fpid else None
    replacelist.append(('REPLACETESTCODE', testcode)) if testcode else None
    for find, replace in replacelist:
        s = re.sub(find, replace, s)
    return s

def authState(r:dict):
    profileid = [ x.get('id') for x in r.get('ProfileID') ][0] if isinstance(r.get('ProfileID'), list) else None
    customerid = [ x.get('id') for x in r.get('CustomerID') ][0] if isinstance(r.get('CustomerID'), list) else None  
    return "loggedOut" if not profileid and not customerid else "authenticated"

def idObj(ts:dict, r:dict, device:dict) -> dict:
    dev = device if int(ts.get('integer')) < device.get('ecid',{}).get('timestamp',{}).get('end',{}).get('seconds') else id_service.ecidNew(device.get('fpid'))
    fpid = dev.get('fpid').get('id')
    ecid = dev.get('ecid').get('id')
    result = {} 
    result["FPID"] = [{"id":fpid, "authenticatedState": authState(r), "primary": True}] 
    result["ECID"] = [{"id":ecid,"primary": True}]
    if isinstance(r.get('ProfileID'), list):
        result["ProfileID"] = r.get('ProfileID')
    return result

def getStoredECID(path:str):
    if len(os.listdir(path)) > 0:
        filepath = max([os.path.join(path,d) for d in os.listdir(path)], key=os.path.getmtime)
        return class_files.Files({}).readJson(filepath)
    plist = path.split("/")
    return id_service.ecidNew({"directory":path, "id":plist[-1]})

def getIdentityMap(ts:dict, r:dict) -> dict:
    if isinstance(r.get('identityMap'), dict):
        return r.get('identityMap')
    path = f"{project_dir}/{r.get('identityMap')}" if isinstance(r.get('identityMap'), str) and os.path.exists(f"{project_dir}/{r.get('identityMap')}") else None
    device = getStoredECID(path) if isinstance(path, str) and os.path.exists(path) and os.path.isdir(path) else id_service.fpidNew()
    return idObj(ts, r, device)

def logout(d:dict):
    x = d.copy()
    if x.get('event',{}).get('xdm',{}).get('cea',{}).get('loginstatus') == "loggedout":
        del x['event']['xdm']['cea']['profileid']
        if x.get('event',{}).get('xdm',{}).get('identityMap',{}).get('ProfileID'):
            del x['event']['xdm']['identityMap']['ProfileID']
    return x

def getCommand(t:dict, r:dict, eventfile:str) -> dict:
    ts = getTimestamp()
    hitid = randomUniqueString()
    url = r.get('url')
    streamid = r.get('streamid')
    identitymap = getIdentityMap(ts, r)
    eventcontent = class_files.Files({}).readFile(eventfile)
    eventstr = replaceString(t, ts, hitid, identitymap, "".join(eventcontent)) if isinstance(eventcontent, list) and len(eventcontent) > 0 else None
    
    if re.search(".xml$", eventfile):
        return {"data":eventstr, "time":ts.get('tsinteger'), "command":f"curl -X POST \"{url}\" -H \"Accept: application/xml\" -H \"Content-Type: application/xml\" -d \"{eventstr}\""}
    
    elif re.search(".json$", eventfile):
        d = json.loads(eventstr) if isinstance(eventstr, str) else None
        if isinstance(d, dict) and isinstance(d.get('event',{}).get('xdm'), dict):
            d["event"]["xdm"]["_id"] = hitid
            d["event"]["xdm"]["receivedTimestamp"] = ts.get('utc_iso_increment')
            d["event"]["xdm"]["timestamp"] = ts.get('utc_iso')
            if not isinstance(d.get('event',{}).get('xdm',{}).get('identityMap'), dict):
                d["event"]["xdm"]["identityMap"] = identitymap
        data = logout(d)
        
        s = []
        s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
        s.append(f"-X POST \"https://server.adobedc.net/ee/v2/interact?dataStreamId={streamid}\"")
        s.append(f"-H \"Authorization: Bearer {t.get('token')}\"")
        s.append(f"-H \"x-gw-ims-org-id: {t.get('orgid')}\"")
        s.append(f"-H \"x-api-key: {t.get('apikey')}\"")
        s.append(f"-H \"Content-Type: application/json\"")
        s.append(f"-d \"@{useFile(data)}\"") if re.search("^Windows", platform.platform()) else s.append(f"-d '{json.dumps(data)}'")
        command = " ".join(s)
        return {"date":ts.get('date'), "time":ts.get('integer'), "data":data, "command":command}

def useFile(data:dict) -> str:
    makeDirectory(dir_tmp)
    filepath = f"{dir_tmp}/data.json"
    os.remove(filepath) if os.path.exists(filepath) else None
    class_files.Files({}).writeFile({"file":filepath, "content":json.dumps(data, sort_keys=False, default=str)})
    return filepath

def makeRequest(index:int, t:dict, request:dict, eventfile:str) -> None:
    time.sleep(random.randint(3, 15)) if index > 0 else None
    r = getCommand(t, request, eventfile)
    if isinstance(r, dict):
        print(f"\033[1;37;44mdata =====> {json.dumps(r.get('data'))}\033[0m") if not re.search("^Windows", platform.platform()) else print("data =====>", json.dumps(r.get('data')), "\n")
        run = class_subprocess.Subprocess({}).run(r.get('command'))
        parseResult(index, request, eventfile, r, run)

def parseResult(index:int, request:dict, filepath:str, r:dict, run:Any) -> None:
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


