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
dir_global = f"{package_dir}/json"
dir_response = f"{project_dir}/myfolder/adobe/events-sent/response"
file_previous = f"{dir_tmp}/previous.json"
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
        g = {"application":getApplication(r.get('application')), "environment":getEnvironment(r.get('environment'))}
        [(lambda x: makeRequest(i, r.get('eventlist'), t, g, r, f"{project_dir}/{x}"))(x) for i, x in enumerate(r.get('eventlist'))]
        
def randomUniqueString() -> str:
    return uuid.uuid4().hex[:25].upper()

def getApplication(index:int) -> dict:
    e = class_files.Files({}).readJson(f"{dir_global}/xdm-application.json") 
    return e[index] if isinstance(index, int) else random.choice(e)

def getEnvironment(index:int) -> dict:
    e = class_files.Files({}).readJson(f"{dir_global}/xdm-environment.json") 
    return e[index] if isinstance(index, int) else random.choice(e)

def getPrevious(f):
    c = class_files.Files({}).readJson(f"{project_dir}/{f}")
    return c.get('event',{}).get('xdm',{}).get('web',{}).get('webPageDetails')
        
def parsePrevious(index:int, eventlist:list):
    if index < 1:
        os.remove(file_previous) if os.path.exists(file_previous) else None
    else:
        f = eventlist[index-1]
        r = getPrevious(f)
        if not r:
            parsePrevious(index-1, eventlist)
        else:
            makeDirectory(dir_tmp)
            os.remove(file_previous) if os.path.exists(file_previous) else None
            class_files.Files({}).writeFile({"file":file_previous, "content":json.dumps(r, sort_keys=False, default=str)})

def getResolution(e:dict) -> dict:
    if isinstance(e.get('device'), dict):
        return {"width":e.get('device',{}).get('screenWidth'), "height":e.get('device',{}).get('screenHeight'), "res":f"{e.get('device',{}).get('screenWidth')} x {e.get('device',{}).get('screenHeight')}"}

def replaceString(index:int, eventlist:list, t:dict, g:dict, r:dict, ts:dict, hitid:str, identitymap:dict, s:str) -> str:
    fpid = [ x.get('id') for x in identitymap.get('FPID') ][0] if isinstance(identitymap.get('FPID'), list) else None
    authenticatedstate = [ x.get('authenticatedState') for x in identitymap.get('FPID') ][0] if isinstance(identitymap.get('FPID'), list) else "ambiguous"
    ecid = [ x.get('id') for x in identitymap.get('ECID') ][0] if isinstance(identitymap.get('ECID'), list) else None
    customerid = [ x.get('id') for x in identitymap.get('CustomerID') ][0] if isinstance(identitymap.get('CustomerID'), list) else None  
    profileid = [ x.get('id') for x in identitymap.get('ProfileID') ][0] if isinstance(identitymap.get('ProfileID'), list) else None
    parsePrevious(index, eventlist)
    pageprevious = class_files.Files({}).readJson(file_previous)
    s_dict = json.loads(s)
    webPageDetails = s_dict.get('event',{}).get('xdm',{}).get('web',{}).get('webPageDetails')
    pagecurrent = webPageDetails if isinstance(webPageDetails, dict) else pageprevious
    resolution = getResolution(g.get('environment'))
    print(f"\033[1;30;43mpageprevious =====> {pageprevious}\033[0m") if not re.search("^Windows", platform.platform()) else None 
    print(f"\033[1;30;42mpagecurrent =====> {pagecurrent}\033[0m") if not re.search("^Windows", platform.platform()) else None

    if not pagecurrent.get('name'):
        s = re.sub('"pagename":"REPLACEPAGENAME",', "", s)
    if not pagecurrent.get('URL'):
        s = re.sub('"previousurl":"REPLACEPREVIOUSURL",', "", s)
    if not pageprevious:
        s = re.sub('"previouspagename":"REPLACEPREVIOUSPAGENAME",', "", s)
    if not g.get('environment',{}).get('operatingSystem'):
        s = re.sub('"ossystem":"REPLACEOPERATINGSYSTEM",', "", s)
    if not g.get('environment',{}).get('operatingSystemVersion'):
        s = re.sub('"osversion":"REPLACEOSVERSION",', "", s)
    if not resolution:
        s = re.sub('"resolution":"REPLACERESOLUTION",', "", s)
    
    replacelist = [
        ('replaceordernumber', str(ts.get('integer'))),
        ('REPLACEREFERENCE', hitid),
        ('REPLACELINKCLICKID', hitid),
        ('REPLACETERMINALID', randomUniqueString()),
        ('REPLACERECEIVEDTIMESTAMP', str(ts.get('ms_increment'))),
        ('REPLACETIMESTAMP', str(ts.get('ms'))),
        ('timestamp><', f"timestamp>{str(ts.get('integer'))}<")
    ]
    replacelist.append(('"REPLACEAPPLICATION"', json.dumps(g.get('application'))))
    replacelist.append(('"REPLACEENVIRONMENT"', json.dumps(g.get('environment'))))
    replacelist.append(('REPLACEDEVICENAME', g.get('environment',{}).get('device',{}).get('model'))) if g.get('environment',{}).get('device',{}).get('model') else None
    replacelist.append(('REPLACELANGUAGE', g.get('environment',{}).get('language')))
    replacelist.append(('REPLACEPAGENAME', pagecurrent.get('name'))) if pagecurrent.get('name') else None
    replacelist.append(('REPLACEPREVIOUSPAGENAME', pageprevious.get('name'))) if isinstance(pageprevious, dict) and pageprevious.get('name') else None
    replacelist.append(('REPLACEPREVIOUSURL', pageprevious.get('URL'))) if isinstance(pageprevious, dict) and pageprevious.get('URL') else None
    replacelist.append(('REPLACEOPERATINGSYSTEM', g.get('environment',{}).get('operatingSystem'))) if g.get('environment',{}).get('operatingSystem') else None
    replacelist.append(('REPLACEOSVERSION', g.get('environment',{}).get('operatingSystemVersion'))) if g.get('environment',{}).get('operatingSystemVersion') else None
    replacelist.append(('REPLACERESOLUTION', resolution.get('res'))) if isinstance(resolution, dict) and isinstance(resolution.get('res'), str) else None
    replacelist.append(('REPLACETESTCODE', testcode)) if testcode else None
    replacelist.append(('REPLACEURL', pagecurrent.get('URL'))) if pagecurrent.get('URL') else None
    for find, replace in replacelist:
        s = re.sub(find, replace, s)
    return s

def authState(r:dict) -> str:
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
    if isinstance(r.get('CustomerID'), list):
        result["CustomerID"] = r.get('CustomerID')
    return result

def getStoredECID(path:str) -> dict:
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

def logout(d:dict, identitymap:dict) -> dict:
    x = d.copy()
    ecid = [ x.get('id') for x in identitymap.get('ECID') ][0] if isinstance(identitymap.get('ECID'), list) else None  
    ecidprimary = [ x.get('primary') for x in identitymap.get('ECID') ][0] if isinstance(identitymap.get('ECID'), list) else None  
    fpid = [ x.get('id') for x in identitymap.get('FPID') ][0] if isinstance(identitymap.get('FPID'), list) else None  
    authenticatedState = [ x.get('authenticatedState') for x in identitymap.get('FPID') ][0] if isinstance(identitymap.get('FPID'), list) else None  
    profileid = [ x.get('id') for x in identitymap.get('ProfileID') ][0] if isinstance(identitymap.get('ProfileID'), list) else None
    customerid = [ x.get('id') for x in identitymap.get('CustomerID') ][0] if isinstance(identitymap.get('CustomerID'), list) else None
    loginstatus = x.get('event',{}).get('xdm',{}).get('cea',{}).get('loginstatus')
    auth = loginstatus if isinstance(loginstatus, str) and loginstatus == "loggedOut" else authenticatedState
    
    if x.get('event',{}).get('xdm',{}).get('cea') and fpid:
        x['event']['xdm']['cea']['fpid'] = fpid

    if x.get('event',{}).get('xdm',{}).get('cea') and ecid:
        x['event']['xdm']['cea']['marketingcloudid'] = ecid
    
    x["event"]["xdm"]["endUserIDs"] = { \
        "_experience":{ \
            "mcid":{ \
                "namespace":{"code":"ECID"}, \
                "id":ecid, \
                "authenticatedState":auth, \
                "primary":ecidprimary \
            } \
        } \
    }
    
    if auth == "loggedOut":
        x['event']['xdm']['identityMap'] = {}
        x['event']['xdm']['identityMap']['FPID'] = [{"id":fpid, "authenticatedState":auth, "primary": True}]
        x['event']['xdm']['identityMap']['ECID'] = identitymap.get('ECID')
        return x
    
    x['event']['xdm']['identityMap'] = {}
    x['event']['xdm']['identityMap']['FPID'] = [{"id":fpid, "authenticatedState":"loggedOut", "primary": True}]
    x['event']['xdm']['identityMap']['ECID'] = identitymap.get('ECID')
    x['event']['xdm']['identityMap']['ProfileID'] = identitymap.get('ProfileID')
    
    if x.get('event',{}).get('xdm',{}).get('cea') and customerid:
        x['event']['xdm']['cea']['customerid'] = customerid

    if x.get('event',{}).get('xdm',{}).get('cea'):
        x['event']['xdm']['cea']['profileid'] = profileid
    
    if x.get('event',{}).get('xdm',{}).get('cea'):
        x['event']['xdm']['cea']['loginstatus'] = authenticatedState
    
    x["event"]["xdm"]["_experience"] = {
        "analytics":{ \
            "customDimensions":{ \
                "eVars":{ \
                    "eVar16":profileid \
                } \
            } \
        } \
    }
    
    return x

def getCommand(index:int, eventlist:list, t:dict, g:dict, r:dict, eventfile:str) -> dict:
    ts = class_converttime.Converttime({}).getTimestamp({"increment":300})
    hitid = randomUniqueString()
    url = r.get('url')
    streamid = r.get('streamid')
    identitymap = getIdentityMap(ts, r)
    eventcontent = class_files.Files({}).readFile(eventfile)
    eventstr = replaceString(index, eventlist, t, g, r, ts, hitid, identitymap, "".join(eventcontent)) if isinstance(eventcontent, list) and len(eventcontent) > 0 else None
    
    if re.search(".xml$", eventfile):
        return {"data":eventstr, "time":ts.get('integer'), "command":f"curl -X POST \"{url}\" -H \"Accept: application/xml\" -H \"Content-Type: application/xml\" -d \"{eventstr}\""}
    
    elif re.search(".json$", eventfile):
        d = json.loads(eventstr) if isinstance(eventstr, str) else None
        if isinstance(d, dict) and isinstance(d.get('event',{}).get('xdm'), dict):
            d["event"]["xdm"]["_id"] = hitid
            d["event"]["xdm"]["receivedTimestamp"] = ts.get('utc_iso_increment')
            d["event"]["xdm"]["timestamp"] = ts.get('utc_iso')
            d["query"] = { \
                "identity":{ \
                    "fetch":["ECID"] \
                } \
            }
        
        data = logout(d, identitymap)
        
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

def makeRequest(index:int, eventlist:list, t:dict, g:dict, request:dict, eventfile:str) -> None:
    time.sleep(random.randint(3, 15)) if index > 0 else None
    r = getCommand(index, eventlist, t, g, request, eventfile)
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


