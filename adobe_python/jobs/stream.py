#!/usr/bin/python3

import argparse, copy, datetime, hashlib, json, os, platform, random, re, sys, time
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
dir_json = f"{package_dir}/json"
dir_response = f"{project_dir}/myfolder/adobe/events-sent/response"
file_previous = f"{dir_tmp}/previous.json"
dev = False

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
        t = {} if dev else oauth.getAccessToken()
        [(lambda x: makeRequest(i, r.get('eventlist'), t, r, f"{project_dir}/{x}"))(x) for i, x in enumerate(r.get('eventlist'))]
        
def randomUniqueString() -> str:
    return uuid.uuid4().hex[:25].upper()

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

def getPrevious(f):
    c = class_files.Files({}).readJson(f"{project_dir}/{f}")
    return c.get('web',{}).get('webPageDetails')
        
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

def getApplication(d) -> dict:
    if "application" in d.get('request'):
        index = d.get('request',{}).get('application')
        e = class_files.Files({}).readJson(f"{dir_json}/xdm-application.json") 
        i = e[index] if isinstance(index, int) else random.choice(e)
        return  {"application":i}

def getEnvironment(d) -> dict:
    index = d.get('request',{}).get('environment')
    e = class_files.Files({}).readJson(f"{dir_json}/xdm-environment.json") 
    i = e[index] if isinstance(index, int) else random.choice(e)
    return  {"environment":i}

def getWebReferrer(pageprevious:dict, webpagedetails:dict, webreferrer:dict) -> dict:
    if not isinstance(webpagedetails, dict):
        return None
    if isinstance(webreferrer, dict):
        return webreferrer
    return {"URL":pageprevious.get('URL'), "type":"internal"} if pageprevious else None

def getWebPageDetails(hitid:str, g:dict, webpagedetails, webreferrer, webinteraction) -> dict:
    if webpagedetails:
        c = copy.deepcopy(g)
        webpagedetails.update({"pageViews": {"value": 1.0}}) 
        c.update({"eventType":"web.webPageDetails.pageViews", "web":{"webPageDetails":webpagedetails, "webReferrer":webreferrer}}) if isinstance(webreferrer, dict) and isinstance(webreferrer.get('URL'), dict) else c.update({"eventType":"web.webPageDetails.pageViews", "web":{"webPageDetails":webpagedetails}})
        return c

def getWebInteraction(hitid:str, g:dict, webpagedetails, webreferrer, webinteraction) -> dict:
    if webinteraction:
        c = copy.deepcopy(g)
        webinteraction.update({"linkClicks": {"type":"other", "value": 1.0, "id":hitid}}) 
        c.update({"eventType":"web.webInteraction.linkClicks", "web":{"webInteraction":webinteraction}})
        return c

def getWeb(g:dict, d:dict) -> tuple:
    hitid = randomUniqueString()
    webpagedetails = d.get('eventcontent',{}).get('web',{}).get('webPageDetails')
    webinteraction = d.get('eventcontent',{}).get('web',{}).get('webInteraction')
    parsePrevious(d.get('index'), d.get('eventlist'))
    pageprevious = class_files.Files({}).readJson(file_previous)
    pagecurrent = webpagedetails if isinstance(webpagedetails, dict) else pageprevious
    webreferrer = getWebReferrer(pageprevious, webpagedetails, d.get('eventcontent',{}).get('web',{}).get('webReferrer'))
    
    #print(f"\033[1;30;43m{d.get('index')} pageprevious =====> {pageprevious}\033[0m") if not re.search("^Windows", platform.platform()) else None 
    #print(f"\033[1;30;42m{d.get('index')} pagecurrent =====> {pagecurrent}\033[0m") if not re.search("^Windows", platform.platform()) else None
    #print(f"\033[1;30;45m{d.get('index')} webreferrer =====> {webreferrer}\033[0m") if not re.search("^Windows", platform.platform()) else None 
    
    l = list(filter(None,[f(hitid, g, webpagedetails, webreferrer, webinteraction) for f in [getWebPageDetails, getWebInteraction]]))
    w = {k:v for x in l for (k,v) in x.items()}
    w.update({"hitid":hitid, "pageprevious":pageprevious, "pagecurrent":pagecurrent})
    return w

def getIdentityMap(ts:dict, r:dict) -> dict:
    if isinstance(r.get('identityMap'), dict):
        return r.get('identityMap')
    path = f"{project_dir}/{r.get('identityMap')}" if isinstance(r.get('identityMap'), str) and os.path.exists(f"{project_dir}/{r.get('identityMap')}") else None
    device = getStoredECID(path) if isinstance(path, str) and os.path.exists(path) and os.path.isdir(path) else id_service.fpidNew()
    return idObj(ts, r, device)

def getResolution(e:dict) -> dict:
    if isinstance(e.get('device'), dict):
        return {"width":e.get('device',{}).get('screenWidth'), "height":e.get('device',{}).get('screenHeight'), "res":f"{e.get('device',{}).get('screenWidth')} x {e.get('device',{}).get('screenHeight')}"}

def getContextData(d:dict, g:dict) -> dict:
    cd = d.get('eventcontent',{}).get('cea')
    c = cd if isinstance(cd, dict) else {}

    resolution = getResolution(g.get('environment',{}))

    c.update({"cookielevel": "1"})
    c.update({"countrycode": "be"})
    c.update({"languagebrowserdevice": "en-BE"})
    c.update({"languagepagesetting": "en"})
    c.update({"ossystem": g.get('environment',{}).get('operatingSystem')}) if g.get('environment',{}).get('operatingSystem') else None
    c.update({"osversion": g.get('environment',{}).get('operatingSystemVersion')}) if g.get('environment',{}).get('operatingSystemVersion') else None
    c.update({"pagename": g.get('pagecurrent').get('name')}) if isinstance(g.get('pagecurrent'), dict) and g.get('pagecurrent').get('name') else None
    c.update({"previouspagename": g.get('pageprevious').get('name')}) if isinstance(g.get('pageprevious'), dict) and g.get('pageprevious').get('name') else None
    c.update({"receivedtimestamp": str(d.get('timestamp',{}).get('ms_increment'))})
    c.update({"reference": g.get('hitid')})
    c.update({"resolution": resolution.get('res')}) if isinstance(resolution, dict) and isinstance(resolution.get('res'), str) else None
    c.update({"timestamp": str(d.get('timestamp',{}).get('ms'))})
    
    if "device" in g.get('environment'): 
        c.update({"devicename": g.get('environment',{}).get('device',{}).get('model')}) if g.get('environment',{}).get('device',{}).get('model') else None
    if "application" in g: 
        c.update({"appversion": "1.77.1"})
        c.update({"libraryversion": "Android 1.4.2 | CEA 2.4.4-1669628165040"})
    
    return dict(sorted(c.items()))

def userAuth(d:dict, g:dict, c:dict, i:dict) -> dict:
    hitid = g.get('hitid')
    del g['pageprevious']
    del g['pagecurrent']
    del g['hitid']

    loginstatus = d.get('eventcontent').get('cea',{}).get('loginstatus')
    ecid = [ x.get('id') for x in i.get('ECID') ][0] if isinstance(i.get('ECID'), list) else None  
    ecidprimary = [ x.get('primary') for x in i.get('ECID') ][0] if isinstance(i.get('ECID'), list) else None  
    fpid = [ x.get('id') for x in i.get('FPID') ][0] if isinstance(i.get('FPID'), list) else None  
    authenticatedState = [ x.get('authenticatedState') for x in i.get('FPID') ][0] if isinstance(i.get('FPID'), list) else None  
    profileid = [ x.get('id') for x in i.get('ProfileID') ][0] if isinstance(i.get('ProfileID'), list) else None
    customerid = [ x.get('id') for x in i.get('CustomerID') ][0] if isinstance(i.get('CustomerID'), list) else None
    auth = loginstatus if isinstance(loginstatus, str) and loginstatus == "loggedOut" else authenticatedState
    query = {"identity":{"fetch":["ECID"]}}

    endUserIDs = { \
        "_experience":{ \
            "mcid":{ \
                "namespace":{"code":"ECID"}, \
                "id":ecid, \
                "authenticatedState":auth, \
                "primary":ecidprimary \
            } \
        } \
    }
    
    c.update({"fpid": fpid}) if isinstance(c, dict) and fpid else None
    c.update({"marketingcloudid": ecid}) if isinstance(c, dict) and ecid else None
    g.update({"_id":hitid})
    g.update({"timestamp":d.get('timestamp',{}).get('utc_iso')})
    g.update({"receivedTimestamp":d.get('timestamp',{}).get('utc_iso_increment')})
    g.update({"endUserIDs":endUserIDs})
    
    identitymap = {}
    if auth == "loggedOut":
        identitymap['FPID'] = [{"id":fpid, "authenticatedState":"loggedOut", "primary": True}]
        identitymap['ECID'] = i.get('ECID')
        g.update({"cea":c})
        g.update({"identityMap":identitymap})
        return {"event":{"xdm":g}, "query":query}
    
    identitymap['FPID'] = [{"id":fpid, "authenticatedState":auth, "primary": True}]
    identitymap['ECID'] = i.get('ECID')
    identitymap['ProfileID'] = i.get('ProfileID')
    
    c.update({"customerid": customerid}) if isinstance(c, dict) and customerid else None
    c.update({"profileid": profileid}) if isinstance(c, dict) and profileid else None
    c.update({"loginstate": authenticatedState}) if isinstance(c, dict) and authenticatedState else None
    
    experience = {
        "analytics":{ \
            "customDimensions":{ \
                "eVars":{ \
                    "eVar16":profileid \
                } \
            } \
        } \
    }
    
    g.update({"cea":c})
    g.update({"identityMap":identitymap})
    g.update({"_experience":experience})
    return {"event":{"xdm":g}, "query":query}

def getCommand(index:int, eventlist:list, t:dict, r:dict, eventfile:str) -> dict:
    ts = class_converttime.Converttime({}).getTimestamp({"increment":300})
    url = r.get('url')
    streamid = r.get('streamid')
    identitymap = getIdentityMap(ts, r)
    eventcontent = class_files.Files({}).readJson(eventfile)
    d = {"index":index, "timestamp":ts, "eventlist":r.get('eventlist'), "eventcontent":eventcontent, "request":r}
    glist = list(filter(None,[f(d) for f in [getEnvironment, getApplication]]))
    g = {k:v for x in glist for (k,v) in x.items()}
    c = getContextData(d, getWeb(g, d))
    data = userAuth(d, getWeb(g, d), c, identitymap)
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

def makeRequest(index:int, eventlist:list, t:dict, request:dict, eventfile:str) -> None:
    time.sleep(random.randint(3, 15)) if not dev and index > 0 else None
    r = getCommand(index, eventlist, t, request, eventfile)
    if isinstance(r, dict):
        print(f"\033[1;37;44mdata =====> {json.dumps(r.get('data'))}\033[0m") if not re.search("^Windows", platform.platform()) else print("data =====>", json.dumps(r.get('data')), "\n")
        if not dev:
            run = class_subprocess.Subprocess({}).run(r.get('command'))
            parseResult(index, request, eventfile, r, run)

def storeResponse(request:str, response:dict) -> None:
    directory = f"{project_dir}/{request.get('identityMap')}"

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
            storeResponse(request, response)
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


