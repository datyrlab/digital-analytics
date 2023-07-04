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
dir_device_rel = f"myfolder/device"
dir_tmp = f"{project_dir}/myfolder/events-sent/tmp"
dir_log = f"{project_dir}/myfolder/events-sent/logs"
dir_json = f"{package_dir}/json"
dir_response = f"{project_dir}/myfolder/events-sent/response"
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

def parseRequest(request:dict) -> None:
    if isinstance(request, dict):
        token = {} if dev else oauth.getAccessToken()
        request.update({"identityMap":fpidNew()}) if not isinstance(request.get('identityMap'), str) else None
        profileid = getUserID(request, "ProfileID")
        customerid = getUserID(request, "CustomerID")
        request.update({"ProfileID":[{"id":profileid, "primary": True}]}) if not isinstance(request.get('ProfileID'), list) else None
        request.update({"CustomerID":[{"id":customerid, "primary": False}]}) if not isinstance(request.get('CustomerID'), list) else None
        eventlist = getEventList(request.get('eventlist'))
        print(request)
        [(lambda x: makeRequest(i, eventlist, token, request, f"{project_dir}/{x}"))(x) for i, x in enumerate(eventlist)] if isinstance(eventlist, list) and len(eventlist) > 0 else print("Event list is empty")

def fpidNew() -> dict:
    i = str(uuid.uuid4())
    directory = f"{project_dir}/{dir_device_rel}/{i}"
    makeDirectory(directory)
    return f"{dir_device_rel}/{i}"

def getEventList(eventlist:list) -> list:
    if isinstance(eventlist, list):
        return eventlist
    filepath = f"{project_dir}/{eventlist}"
    return class_files.Files({}).readFile(filepath) if os.path.exists(filepath) else None

def randomUniqueString() -> str:
    return uuid.uuid4().hex[:25].upper()

def randomUniqueStringSha() -> str:
    t = str(time.time())
    sh = hashlib.sha1(t.encode())
    hd = sh.hexdigest()
    return str(hd)

def storeUserID(directory:str, filepath:str, item:str) -> None:
    if not os.path.exists(filepath):
        makeDirectory(directory)
        class_files.Files({}).writeFile({"file":filepath, "content":item})
    return item

def getUserID(request:dict, name:str) -> str:
    print()
    directory = f"{project_dir}/{request.get('identityMap')}/userids"
    filepath = f"{directory}/{name}.txt"
    item = [ x.get('id') for x in request.get(name) ][0] if isinstance(request.get(name), list) else randomUniqueStringSha()
    storeUserID(directory, filepath, item)
    c = class_files.Files({}).readFile(filepath)
    return storeUserID(directory, filepath, c[0]) if isinstance(c, list) and len(c) > 0 else storeUserID(directory, filepath, randomUniqueStringSha()) 

def authState(request:dict) -> str:
    profileid = [ x.get('id') for x in request.get('ProfileID') ][0] if isinstance(request.get('ProfileID'), list) else None
    customerid = [ x.get('id') for x in request.get('CustomerID') ][0] if isinstance(request.get('CustomerID'), list) else None  
    return "loggedOut" if not profileid and not customerid else "authenticated"

def idObj(timestamp:dict, request:dict, device:dict) -> dict:
    """ custom to the implementation, build the identityMap object to include specific id keys """
    #dev = device if isinstance(device.get('ecid'), dict) and int(timestamp.get('integer')) < device.get('ecid',{}).get('timestamp',{}).get('end',{}).get('seconds') else id_service.ecidNew(device.get('fpid'))
    dev = device
    fpid = dev.get('fpid',{}).get('id') if isinstance(dev, dict) and isinstance(dev.get('fpid'), dict) else None 
    ecid = dev.get('ecid',{}).get('id') if isinstance(dev, dict) and isinstance(dev.get('ecid'), dict) else None
    result = {} 
    result["FPID"] = [{"id":fpid, "authenticatedState": authState(request), "primary": True}]
    if isinstance(ecid, str):
        result["ECID"] = [{"id":ecid,"primary": True}]
    if isinstance(request.get('ProfileID'), list):
        result["ProfileID"] = request.get('ProfileID')
    if isinstance(request.get('CustomerID'), list):
        result["CustomerID"] = request.get('CustomerID')
    return result

def recentFile(path:str) -> dict:
    makeDirectory(path)
    if len(os.listdir(path)) > 0:
        filepath = max([os.path.join(path,d) for d in os.listdir(path)], key=os.path.getmtime)
        return class_files.Files({}).readJson(filepath)
        
def getEcid(path:str) -> dict:
    c = recentFile(path)
    if not isinstance(c, dict):
        return None
    handle = c.get('response',{}).get('handle')
    if not isinstance(handle, list):
        return None
    for p in handle:
        e = list(filter(None, [ x.get('id') for x in p.get('payload') if x.get('namespace',{}).get('code') == "ECID"])) if isinstance(p.get('payload'), list) else None
        if isinstance(e, list) and len(e) > 0 and isinstance(e[0], str):
            return {"id":e[0]} 

def getIdentityMap(timestamp:dict, request:dict) -> dict:
    if isinstance(request.get('identityMap'), dict):
        return request.get('identityMap')
    path = f"{project_dir}/{request.get('identityMap')}" if isinstance(request.get('identityMap'), str) and os.path.exists(f"{project_dir}/{request.get('identityMap')}") else None
    if not isinstance(path, str) and os.path.exists(path):
        return None
    plist = path.split("/")
    directory_storage = f"{str(path)}/storage"
    device = {"fpid":{"directory":path, "id":plist[-1]}, "ecid":getEcid(directory_storage)}
    return idObj(timestamp, request, device)

def getPrevious(filename:str) -> dict:
    c = class_files.Files({}).readJson(f"{project_dir}/{filename}")
    return c.get('web',{}).get('webPageDetails')
        
def parsePrevious(index:int, eventlist:list) -> None:
    if index < 1:
        os.remove(file_previous) if os.path.exists(file_previous) else None
    else:
        filepath = eventlist[index-1]
        result = getPrevious(filepath)
        if not result:
            parsePrevious(index-1, eventlist)
        else:
            makeDirectory(dir_tmp)
            os.remove(file_previous) if os.path.exists(file_previous) else None
            class_files.Files({}).writeFile({"file":file_previous, "content":json.dumps(result, sort_keys=False, default=str)})

def getApplication(eventdict:dict) -> dict:
    if "application" in eventdict.get('request'):
        index = eventdict.get('request',{}).get('application')
        a = class_files.Files({}).readJson(f"{dir_json}/xdm-application.json") 
        i = a[index] if isinstance(index, int) else random.choice(a)
        return  {"application":i}

def getEnvironment(eventdict:dict) -> dict:
    index = eventdict.get('request',{}).get('environment')
    e = class_files.Files({}).readJson(f"{dir_json}/xdm-environment.json") 
    i = e[index] if isinstance(index, int) else random.choice(e)
    return  {"environment":i}

def getWebReferrer(pageprevious:dict, webpagedetails:dict, webreferrer:dict) -> dict:
    if not isinstance(webpagedetails, dict):
        return None
    if isinstance(webreferrer, dict):
        return webreferrer
    return {"URL":pageprevious.get('URL'), "type":"internal"} if pageprevious else None

def getWebPageDetails(hitid:str, eventobj:dict, webpagedetails, webreferrer, webinteraction) -> dict:
    if webpagedetails:
        c = copy.deepcopy(eventobj)
        webpagedetails.update({"pageViews": {"value": 1.0}}) 
        c.update({"eventType":"web.webPageDetails.pageViews", "web":{"webPageDetails":webpagedetails, "webReferrer":webreferrer}}) if isinstance(webreferrer, dict) and isinstance(webreferrer.get('URL'), dict) else c.update({"eventType":"web.webPageDetails.pageViews", "web":{"webPageDetails":webpagedetails}})
        return c

def getWebInteraction(hitid:str, eventobj:dict, webpagedetails, webreferrer, webinteraction) -> dict:
    if webinteraction:
        c = copy.deepcopy(eventobj)
        webinteraction.update({"linkClicks": {"type":"other", "value": 1.0, "id":hitid}}) 
        c.update({"eventType":"web.webInteraction.linkClicks", "web":{"webInteraction":webinteraction}})
        return c

def getWeb(eventobj:dict, eventdict:dict) -> dict:
    """ an event is either webPageDetails or webInteraction """
    hitid = randomUniqueString()
    webpagedetails = eventdict.get('eventjson',{}).get('web',{}).get('webPageDetails')
    webinteraction = eventdict.get('eventjson',{}).get('web',{}).get('webInteraction')
    parsePrevious(eventdict.get('index'), eventdict.get('eventlist'))
    pageprevious = class_files.Files({}).readJson(file_previous)
    pagecurrent = webpagedetails if isinstance(webpagedetails, dict) else pageprevious
    webreferrer = getWebReferrer(pageprevious, webpagedetails, eventdict.get('eventjson',{}).get('web',{}).get('webReferrer'))
    
    #print(f"\033[1;30;43m{d.get('index')} pageprevious =====> {pageprevious}\033[0m") if not re.search("^Windows", platform.platform()) else None 
    #print(f"\033[1;30;42m{d.get('index')} pagecurrent =====> {pagecurrent}\033[0m") if not re.search("^Windows", platform.platform()) else None
    #print(f"\033[1;30;45m{d.get('index')} webreferrer =====> {webreferrer}\033[0m") if not re.search("^Windows", platform.platform()) else None 
    
    weblist = list(filter(None,[f(hitid, eventobj, webpagedetails, webreferrer, webinteraction) for f in [getWebPageDetails, getWebInteraction]]))
    web = {k:v for x in weblist for (k,v) in x.items()}
    web.update({"hitid":hitid, "pageprevious":pageprevious, "pagecurrent":pagecurrent})
    return web

def getResolution(environment:dict) -> dict:
    if isinstance(environment.get('device'), dict):
        return {"width":environment.get('device',{}).get('screenWidth'), "height":environment.get('device',{}).get('screenHeight'), "resolution":f"{environment.get('device',{}).get('screenWidth')} x {environment.get('device',{}).get('screenHeight')}"}

def getContextData(eventdict:dict, eventobj:dict) -> dict:
    """ custom context data variables """
    cd = eventdict.get('eventjson',{}).get('data')
    contextdata = cd if isinstance(cd, dict) else {}

    res = getResolution(eventobj.get('environment',{}))

    contextdata.update({"cookielevel": "1"})
    contextdata.update({"countrycode": "be"})
    contextdata.update({"languagebrowserdevice": "en-BE"})
    contextdata.update({"languagepagesetting": "en"})
    contextdata.update({"ossystem": eventobj.get('environment',{}).get('operatingSystem')}) if eventobj.get('environment',{}).get('operatingSystem') else None
    contextdata.update({"osversion": eventobj.get('environment',{}).get('operatingSystemVersion')}) if eventobj.get('environment',{}).get('operatingSystemVersion') else None
    contextdata.update({"pagename": eventobj.get('pagecurrent').get('name')}) if isinstance(eventobj.get('pagecurrent'), dict) and eventobj.get('pagecurrent').get('name') else None
    contextdata.update({"previouspagename": eventobj.get('pageprevious').get('name')}) if isinstance(eventobj.get('pageprevious'), dict) and eventobj.get('pageprevious').get('name') else None
    contextdata.update({"receivedtimestamp": str(eventdict.get('timestamp',{}).get('ms_increment'))})
    contextdata.update({"reference": eventobj.get('hitid')})
    contextdata.update({"resolution": res.get('res')}) if isinstance(res, dict) and isinstance(res.get('resolution'), str) else None
    contextdata.update({"timestamp": str(eventdict.get('timestamp',{}).get('ms'))})
    
    if "device" in eventobj.get('environment'): 
        contextdata.update({"devicename": eventobj.get('environment',{}).get('device',{}).get('model')}) if eventobj.get('environment',{}).get('device',{}).get('model') else None
    if "application" in eventobj: 
        contextdata.update({"appversion": "1.77.1"})
        contextdata.update({"libraryversion": "Android 1.4.2 | CEA 2.4.4-1669628165040"})
    
    return dict(sorted(contextdata.items()))

def userAuth(eventdict:dict, eventobj:dict, contextdata:dict, idmap:dict) -> dict:
    """ custom to the implementation, 
        custom identitymap keys
        custom contextdata key name
        finalizes eventobj if user is loggedOut """
    hitid = eventobj.get('hitid')
    del eventobj['pageprevious']
    del eventobj['pagecurrent']
    del eventobj['hitid']

    loginstatus = eventdict.get('eventjson').get('data',{}).get('loginstatus')
    ecid = [ x.get('id') for x in idmap.get('ECID') ][0] if isinstance(idmap.get('ECID'), list) else None  
    ecidprimary = [ x.get('primary') for x in idmap.get('ECID') ][0] if isinstance(idmap.get('ECID'), list) else None  
    fpid = [ x.get('id') for x in idmap.get('FPID') ][0] if isinstance(idmap.get('FPID'), list) else None  
    authenticatedState = [ x.get('authenticatedState') for x in idmap.get('FPID') ][0] if isinstance(idmap.get('FPID'), list) else None  
    profileid = [ x.get('id') for x in idmap.get('ProfileID') ][0] if isinstance(idmap.get('ProfileID'), list) else None
    customerid = [ x.get('id') for x in idmap.get('CustomerID') ][0] if isinstance(idmap.get('CustomerID'), list) else None
    auth = loginstatus if isinstance(loginstatus, str) and loginstatus == "loggedOut" else authenticatedState
    query = {"identity":{"fetch":["ECID"]}}
    identification = {"Identification":{"ecid":ecid}} if isinstance(ecid, str) else {}

    contextdata.update({"fpid": fpid}) if isinstance(contextdata, dict) and fpid else None
    contextdata.update({"marketingcloudid": ecid}) if isinstance(contextdata, dict) and ecid else None
    eventobj.update({"_id":hitid})
    eventobj.update({"timestamp":eventdict.get('timestamp',{}).get('utc_iso')})
    eventobj.update({"receivedTimestamp":eventdict.get('timestamp',{}).get('utc_iso_increment')})
    
    identitymap = {}
    if auth == "loggedOut":
        identitymap['FPID'] = [{"id":fpid, "authenticatedState":"loggedOut", "primary": True}]
        if isinstance(idmap.get('ECID'), list):
            identitymap['ECID'] = idmap.get('ECID')
        eventobj.update({"_ing_intermediairs":identification}) if isinstance(identification.get('ecid'), str) else None
        eventobj.update({"cea":contextdata}) # custom contextdata key name
        eventobj.update({"identityMap":identitymap})
        return {"event":{"xdm":eventobj}, "query":query}
    
    if not isinstance(identification.get('Identification'), dict):
        identification.update({"Identification":{"profileid":profileid}})
    else:
        identification["Identification"]["profileid"] = profileid

    identitymap['FPID'] = [{"id":fpid, "authenticatedState":auth, "primary": True}]
    if isinstance(idmap.get('ECID'), list):
        identitymap['ECID'] = idmap.get('ECID')
    identitymap['ProfileID'] = idmap.get('ProfileID')
    
    contextdata.update({"customerid": customerid}) if isinstance(contextdata, dict) and customerid else None
    contextdata.update({"profileid": profileid}) if isinstance(contextdata, dict) and profileid else None
    contextdata.update({"loginstate": authenticatedState}) if isinstance(contextdata, dict) and authenticatedState else None
    
    eventobj.update({"_ing_intermediairs":identification})
    eventobj.update({"cea":contextdata}) # custom contextdata key name
    eventobj.update({"identityMap":identitymap})
    return {"event":{"xdm":eventobj}, "query":query}

def buildRequest(index:int, eventlist:list, token:dict, request:dict, eventfile:str) -> dict:
    timestamp = class_converttime.Converttime({}).getTimestamp({"increment":300})
    url = request.get('url')
    streamid = request.get('streamid')
    idmap = getIdentityMap(timestamp, request)
    eventjson = class_files.Files({}).readJson(eventfile)
    eventdict = {"index":index, "timestamp":timestamp, "eventlist":eventlist, "eventjson":eventjson, "request":request}
    glist = list(filter(None,[f(eventdict) for f in [getEnvironment, getApplication]]))
    eventobj = {k:v for x in glist for (k,v) in x.items()}
    cd = getContextData(eventdict, getWeb(eventobj, eventdict))
    data = userAuth(eventdict, getWeb(eventobj, eventdict), cd, idmap)
    s = []
    s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
    s.append(f"-X POST \"https://server.adobedc.net/ee/v2/interact?dataStreamId={streamid}\"")
    s.append(f"-H \"Authorization: Bearer {token.get('token')}\"")
    s.append(f"-H \"x-gw-ims-org-id: {token.get('orgid')}\"")
    s.append(f"-H \"x-api-key: {token.get('apikey')}\"")
    s.append(f"-H \"Content-Type: application/json\"")
    s.append(f"-d \"@{useFile(data)}\"") if re.search("^Windows", platform.platform()) else s.append(f"-d '{json.dumps(data)}'")
    command = " ".join(s)
    return {"date":timestamp.get('date'), "time":timestamp.get('integer'), "data":data, "command":command}

def useFile(data:dict) -> str:
    makeDirectory(dir_tmp)
    filepath = f"{dir_tmp}/data.json"
    os.remove(filepath) if os.path.exists(filepath) else None
    class_files.Files({}).writeFile({"file":filepath, "content":json.dumps(data, sort_keys=False, default=str)})
    return filepath

def makeRequest(index:int, eventlist:list, token:dict, request:dict, eventfile:str) -> None:
    time.sleep(random.randint(3, 15)) if not dev and index > 0 else None
    reqbuild = buildRequest(index, eventlist, token, request, eventfile)
    if isinstance(reqbuild, dict):
        print(f"\033[1;37;44mdata =====> {json.dumps(reqbuild.get('data'))}\033[0m") if not re.search("^Windows", platform.platform()) else print("data =====>", json.dumps(reqbuild.get('data')), "\n")
        if not dev:
            run = class_subprocess.Subprocess({}).run(reqbuild.get('command'))
            parseResult(index, request, eventfile, reqbuild, run)

def deviceStorage(directory_storage:str, reqbuild:str, response:dict) -> None:
    if isinstance(response, dict): 
        makeDirectory(directory_storage)
        file_response = f"{directory_storage}/response.json"
        os.remove(file_response) if os.path.exists(file_response) else None
        class_files.Files({}).writeFile({"file":file_response, "content":json.dumps({"previousrequest":reqbuild.get('data'), "response":response}, sort_keys=False, indent=4, default=str)})  

def parseResult(index:int, request:dict, filepath:str, reqbuild:dict, run:str) -> None:
    try:
        directory_response = f"{dir_response}/{reqbuild.get('date')}"
        directory_log = f"{dir_log}/{reqbuild.get('date')}"
        makeDirectory(directory_response)
        makeDirectory(directory_log)
        response = json.loads("{\""+ run +"}") if re.search("^requestId", run) else run
        class_files.Files({}).writeFile({"file":f"{directory_response}/{response.get('requestId')}_{reqbuild.get('time')}.json", "content":json.dumps(response, sort_keys=False, default=str)}) if re.search("^requestId", run) else None 
        class_files.Files({}).writeFile({"file":f"{directory_log}/{reqbuild.get('time')}.json", "content":json.dumps({"request":reqbuild.get('data'), "response":response}, sort_keys=False, indent=4, default=str)})  
        deviceStorage(f"{project_dir}/{request.get('identityMap')}/storage", reqbuild, response)
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


