#!/usr/bin/python3

import argparse, copy, datetime, hashlib, json, os, platform, random, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
import uuid
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess
from adobe_python.jobs import oauth

timestamp_numeric = int(time.time() * 1000.0)
dir_device_rel = f"myfolder/device"
dir_tmp = f"{project_dir}/myfolder/events-sent/tmp"
dir_log = f"{project_dir}/myfolder/events-sent/logs"
dir_json = f"{package_dir}/json"
dir_response = f"{project_dir}/myfolder/events-sent/response"
file_previous = f"{dir_tmp}/previous.json"

dev = True

def main():
    requestlist = parseArgs(sys.argv)
    parseRequestList(requestlist)

def parseArgs(argv) -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-re', '--requestlist', dest='requestlist')
    namespace = parser.parse_known_args(argv)[0]
    args = {k: v for k, v in vars(namespace).items() if v is not None}
    requestlist = json.loads(args.get('requestlist')) if isinstance(args.get('requestlist'), str) else None
    return requestlist

def printCol(colour, text) -> None:
    colours = {'black': '30', 'red': '31', 'green': '32', 'yellow': '33', 'blue': '34', 'magenta': '35', 'cyan': '36', 'white': '37'}
    fgcode = colours[colour]
    print(f"\033[{fgcode}m{text}\033[0m")

def parseRequestList(requestlist:list) -> None:
    if isinstance(requestlist, list):
        token = {} if dev else oauth.getAccessToken()
        [(lambda x: parseRequest(token, x))(x) for x in requestlist]
         
def parseRequest(token:dict, request:dict) -> None:
    if isinstance(request, dict):
        printCol("cyan", request.get('device')) if request.get('device') else printCol("magenta", "new device")
        request.update({"device":fpidNew()}) if not isinstance(request.get('device'), str) else None
        profileid = getUserID(request, "ProfileID")
        customerid = getUserID(request, "CustomerID")
        request.update({"ProfileID":[{"id":profileid, "primary": True}]}) if not isinstance(request.get('ProfileID'), list) else None
        request.update({"CustomerID":[{"id":customerid, "primary": False}]}) if not isinstance(request.get('CustomerID'), list) else None
        listoflists = [(lambda x: class_files.Files({}).listDirectory(f"{project_dir}/{x}"))(x) for x in request.get('dirlist')]
        [(lambda x: parseEventlist(i, token, request, x))(x) for i, x in enumerate(listoflists)] if isinstance(listoflists, list) and len(listoflists) > 0 else None

def parseEventlist(index:int, token:dict, request:dict, eventlist:list) -> None:
    l = sortList(eventlist)
    [(lambda x: makeRequest(i, eventlist, token, request, x))(x) for i, x in enumerate(eventlist) if re.search("json$", x)] if isinstance(eventlist, list) and len(eventlist) > 0 else printCol("red", "Event list is empty")

def sortList(filelist:list) -> list:
    if isinstance(filelist, list) and len(filelist) > 0:
        filelist.sort()
        sorted(set(filelist), key=filelist.index)
        return filelist

def fpidNew() -> dict:
    i = str(uuid.uuid4())
    directory = f"{project_dir}/{dir_device_rel}/{i}"
    makeDirectory(directory)
    return f"{dir_device_rel}/{i}"

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
    directory = f"{project_dir}/{request.get('device')}/userids"
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
    fpid = device.get('fpid',{}).get('id') if isinstance(device, dict) and isinstance(device.get('fpid'), dict) else None 
    ecid = device.get('ecid',{}).get('id') if isinstance(device, dict) and isinstance(device.get('ecid'), dict) else None
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
    if isinstance(request.get('device'), dict):
        return request.get('device')
    path = f"{project_dir}/{request.get('device')}" if isinstance(request.get('device'), str) and os.path.exists(f"{project_dir}/{request.get('device')}") else None
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

def getApplication(obj:dict) -> dict:
    def app(event:dict) -> dict:
        if isinstance(event.get('category'), str) and event.get('category') == "moba":
            o = {}
            o.update({"id": event.get('application')}) if isinstance(event.get('application'), str) and not event.get('application') == "" else None
            o.update({"name": event.get('application')}) if isinstance(event.get('application'), str) and not event.get('application') == "" else None
            o.update({"version": event.get('clientVersion')}) if isinstance(event.get('clientVersion'), str) and not event.get('clientVersion') == "" else None
            return {"application":o}
    
    return app(obj.get('event'))
            
def getEnvironment(obj:dict) -> dict:
    def intToBool(value:int):
        pass     
    
    def userAgent(category:str) -> str:
        if category == "dba":
            #return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9"
            return "Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36"
    
    def resolution(orientation:str, s:str):
        x = s.split("x")
        return int(x[0]) if orientation == "h" else int(x[1])   
    
    def getDevice(event:dict) -> dict:
        if isinstance(event.get('category'), str) and event.get('category') == "moba":
            o = {}
            o.update({"screenHeight": resolution("h", event.get('screenResolution'))}) if isinstance(event.get('screenResolution'), str) and re.search("x", event.get('screenResolution')) else None
            o.update({"screenWidth": resolution("w", event.get('screenResolution'))}) if isinstance(event.get('screenResolution'), str) and re.search("x", event.get('screenResolution')) else None
            o.update({"colorDepth": event.get('colorDepth')}) if isinstance(event.get('colorDepth'), int) else None
            o.update({"connectionType": "mobile", "manufacturer": "Samsung", "model": "SM-S906N", "screenOrientation": "Portrait", "type":"application"})
            return {"device":o}
    
    def getBrowser(event:dict) -> dict:
        if isinstance(event.get('browserWidth'), int) and isinstance(event.get('browserHeight'), int):
            o = {}
            o.update({"acceptLanguage": event.get('lang')}) if isinstance(event.get('lang'), str) and not event.get('lang') == "" else None
            o.update({"cookiesEnabled": True}) if isinstance(event.get('cookieEnabled'), int) and event.get('cookieEnabled') == 1 else False
            o.update({"javaScriptEnabled": True}) if isinstance(event.get('javaScriptEnabled'), int) and event.get('javaScriptEnabled') == 1 else False
            o.update({"javaScriptVersion": event.get('javaScriptVersion')}) if isinstance(event.get('javaScriptVersion'), str) and not event.get('javaScriptVersion') == "" else None
            o.update({"javaEnabled": True}) if isinstance(event.get('javaEnabled'), int) and event.get('javaEnabled') == 1 else False
            o.update({"javaVersion": event.get('javaVersion')}) if isinstance(event.get('javaVersion'), str) and not event.get('javaVersion') == "" else None
            #o.update({"userAgent": event.get('userAgent')}) if isinstance(event.get('userAgent'), str) and not event.get('userAgent') == "" else None
            o.update({"userAgent": userAgent(event.get('category'))}) if isinstance(event.get('category'), str) and not event.get('category') == "" else None
            o.update({"viewportWdith": event.get('browserWidth')}) if isinstance(event.get('browserWidth'), int) else None
            o.update({"viewportHeight": event.get('browserHeight')}) if isinstance(event.get('browserHeight'), int) else None
            return {"browserDetails":o}
    
    def environmentObj(event:dict) -> dict:
        browser = getBrowser(event)
        device = getDevice(event)
        o = {"ipV4":"157.97.122.50"}
        o.update(browser) if isinstance(browser, dict) else None
        o.update(device) if isinstance(device, dict) else None
        o.update({"language": event.get('lang')}) if isinstance(event.get('lang'), str) and not event.get('lang') == "" else None
        o.update({"colorDepth": event.get('colorDepth')}) if isinstance(event.get('colorDepth'), int) and event.get('category') == "dba" else None
        o.update({"operatingSystem": "Android", "operatingSystemVersion": "12"}) if isinstance(event.get('category'), str) and event.get('category') == "moba" else None
        return {"environment":o}
    
    return environmentObj(obj.get('event'))

def getWebReferrer(pageprevious:dict, webpagedetails:dict, webreferrer:dict) -> dict:
    if not isinstance(webpagedetails, dict):
        return None
    if isinstance(webreferrer, dict):
        return webreferrer
    return {"URL":pageprevious.get('URL'), "type":"internal"} if pageprevious else None

def getWebPageDetails(event:dict) -> dict:
    def referrerType(s:str):
        if not re.search("ing.be|ing.nl", s):
            return "internal"
        return "external"

    def getWebReferrer(s:str):
        if isinstance(s, str) and not s == "":
            return {"webReferrer": {"URL":s,"type":referrerType(s)}}

    def getParams(s:str) -> str:
        x = s.split("?")
        return x[1] if len(x) > 1 else None

    def getSubsection(s:str):
        if isinstance(s, str) and not s == "":
            x = s.split(":")
            return x[1] if len(x) > 1 else None

    e = {"eventtype": "web.webPageDetails.pageViews"}
    w = {"web":{
        "webPageDetails":{
            "name": event.get('pageName'),
            "server": "https://www.dev.ing.nl",
            "siteSection": event.get('channel'),
            "URL": event.get('pageURL'),
            "pageViews": {"value": 1.0}
        }
    }}
    r = getWebReferrer(event.get('referrer'))
    p = getParams(event.get('fullPageURL'))
    w.update(r) if isinstance(r, dict) else None 
    result = [e, w]
    result.append({"parameters": getParams(event.get('fullPageURL'))}) if isinstance(event.get('fullPageURL'), str) else None
    result.append({"subsection": getSubsection(event.get('pageName'))}) if isinstance(event.get('pageName'), str) else None
    return result
        
def getWebInteraction(hitid:str, event:dict) -> dict:
    etype = event.get('type') if isinstance(event.get('type'), str) else "ActionEvent"
    e = {"eventtype": "web.webInteraction.linkClicks"}
    w = {"web":{
        "webInteraction":{
            "name": etype,
            "linkClicks": {
                "type": "other",
                "value": 1.0,
                "id": hitid
            }
        }
    }}
    return [e, w]

def getWeb(obj:dict) -> dict:
    hitid = randomUniqueString()
    event = obj.get('event')
    web = getWebPageDetails(event) if isinstance(event.get('type'), str) and event.get('type') == "PAGE" else getWebInteraction(hitid, event)
    return {"event":{"hitid":hitid}, "webevent":web}

def getCustomDimensions(obj:dict, environment:dict, webobj:dict, idmap:dict) -> dict:
    def getVars(var:str, webobj:dict):
        def getItem(webobj:dict, item:str) -> str:
            r = list(filter(None,[ x.get(item) for x in webobj.get('webevent') if x.get(item)])) if isinstance(webobj.get('webevent'), list) else None
            return r[0] if len(r) > 0 else None
        
        parameters = getItem(webobj, "parameters")
        subsection = getItem(webobj, "subsection")

        o = {}
        o.update({f"{var}1": event.get('application')}) if isinstance(event.get('application'), str) and not event.get('application') == "" else None
        o.update({f"{var}2": event.get('pageName')}) if isinstance(event.get('pageName'), str) and not event.get('pageName') == "" else None
        o.update({f"{var}3": event.get('pageType')}) if isinstance(event.get('pageType'), str) and not event.get('pageType') == "" else None
        o.update({f"{var}4": event.get('prevPageName')}) if isinstance(event.get('prevPageName'), str) and not event.get('prevPageName') == "" else None
        o.update({f"{var}5": event.get('pageURL')}) if isinstance(event.get('pageURL'), str) and not event.get('pageURL') == "" else None
        o.update({f"{var}6": subsection}) if isinstance(subsection, str) else None
        o.update({f"{var}7": environment.get('environment',{}).get('ipV4')}) if isinstance(environment, dict) and environment.get('environment',{}).get('ipV4') else None
        o.update({f"{var}8": event.get('channel')}) if isinstance(event.get('channel'), str) and not event.get('channel') == "" else None
        o.update({f"{var}9": event.get('category')}) if isinstance(event.get('category'), str) and not event.get('category') == "" else None
        o.update({f"{var}10": event.get('countryCode')}) if isinstance(event.get('countryCode'), str) and not event.get('countryCode') == "" else None
        o.update({f"{var}11": event.get('lang')}) if isinstance(event.get('lang'), str) and not event.get('lang') == "" else None
        o.update({f"{var}12": customerid}) if not event.get('loginstatus') == "loggedOut" else None 
        o.update({f"{var}13": event.get('loginstatus')}) if event.get('loginstatus') == "loggedOut" else o.update({f"{var}13": authenticatedstate}) 
        o.update({f"{var}14": ecid}) if ecid else None 
        o.update({f"{var}15": event.get('profileType')}) if isinstance(event.get('profileType'), str) and not event.get('profileType') == "" else None
        o.update({f"{var}16": profileid}) if profileid and not event.get('loginstatus') == "loggedOut" else None 
        o.update({f"{var}17": event.get('displayMode')}) if isinstance(event.get('displayMode'), str) and not event.get('displayMode') == "" else None
        o.update({f"{var}18": event.get('eventName')}) if isinstance(event.get('eventName'), str) and not event.get('eventName') == "" else None
        o.update({f"{var}19": event.get('languageBrowser')}) if isinstance(event.get('languageBrowser'), str) and not event.get('languageBrowser') == "" else None
        o.update({f"{var}22": event.get('formStep')}) if isinstance(event.get('formStep'), str) and not event.get('formStep') == "" else None
        o.update({f"{var}25": event.get('cookieLevel')}) if isinstance(event.get('cookieLevel'), str) and not event.get('cookieLevel') == "" else None
        o.update({f"{var}33": event.get('experiments')}) if isinstance(event.get('experiments'), dict) and bool(event.get('experiments')) else None
        o.update({f"{var}35": event.get('error')}) if isinstance(event.get('error'), str) and not event.get('error') == "" else None
        o.update({f"{var}36": event.get('errorType')}) if isinstance(event.get('errorType'), str) and not event.get('errorType') == "" else None
        o.update({f"{var}37": event.get('formType')}) if isinstance(event.get('formType'), str) and not event.get('formType') == "" else None
        o.update({f"{var}38": event.get('formId')}) if isinstance(event.get('formId'), str) and not event.get('formId') == "" else None
        o.update({f"{var}39": event.get('formOutcome')}) if isinstance(event.get('formOutcome'), str) and not event.get('formOutcome') == "" else None
        o.update({f"{var}44": parameters}) if isinstance(parameters, str) else None
        o.update({f"{var}45": event.get('subProduct')}) if isinstance(event.get('subProduct'), str) and not event.get('subProduct') == "" else None
        o.update({f"{var}48": event.get('screenResolution')}) if isinstance(event.get('screenResolution'), str) and not event.get('screenResolution') == "" else None
        o.update({f"{var}50": str(obj.get('timestamp',{}).get('ms'))})
        o.update({f"{var}52": environment.get('environment',{}).get('operatingSystem')}) if isinstance(environment, dict) and environment.get('environment',{}).get('operatingSystem') else None
        o.update({f"{var}53": environment.get('environment',{}).get('operatingSystemVersion')}) if isinstance(environment, dict) and environment.get('environment',{}).get('operatingSystemVersion') else None
        o.update({f"{var}68": str(obj.get('timestamp',{}).get('ms_increment'))})
        if "application" in obj: 
            o.update({f"{var}58": appversion})
            o.update({f"{var}57": libraryversion})
        return o
    
    event = obj.get('event')
    authenticatedstate = [ x.get('authenticatedState') for x in idmap.get('FPID') ][0] if isinstance(idmap.get('FPID'), list) else None  
    customerid = [ x.get('id') for x in idmap.get('CustomerID') ][0] if isinstance(idmap.get('CustomerID'), list) else None
    ecid = [ x.get('id') for x in idmap.get('ECID') ][0] if isinstance(idmap.get('ECID'), list) else None  
    fpid = [ x.get('id') for x in idmap.get('FPID') ][0] if isinstance(idmap.get('FPID'), list) else None  
    profileid = [ x.get('id') for x in idmap.get('ProfileID') ][0] if isinstance(idmap.get('ProfileID'), list) else None
    
    evar = getVars("eVar", webobj)
    prop = getVars("prop", webobj)
    prop.update({"prop49": webobj.get('event').get('hitid')})
    customdimensions = {}
    customdimensions.update({"eVars": evar})
    customdimensions.update({"listProps": prop})
    return customdimensions 

def getEventMetrics(obj:dict, environment:dict, webobj:dict, customdimensions:dict, idmap:dict) -> dict:
    def eventRange(n:int) -> str:
        if n < 101: 
            return "event1to100"
        elif n > 100: 
            return "event101to200"
        
    def parseList(val:str, key:str, patternlist:list) -> int:
        r = list(filter(None,[x for x in patternlist if re.search(x, val)]))
        return key if len(r) > 0 else None

    def parseMap(obj:dict, val:str, patternmap:dict) -> tuple:
        r = list(filter(None,[parseList(val, k, v) for k, v in patternmap.items()]))
        if len(r) > 0:
            return (eventRange(int(r[0])), {f"event{r[0]}":{"id":str(int(time.time() * 1000.0)),"value":1}})
    
    def parseObj(lookup:list, obj:dict) -> list:
        for k,v in obj.get('event').items():
            if k in lookup:
                return list(filter(None,[(lambda x: parseMap(obj, v, x))(x) for x in lookup.get(k)]))

    def buildObj(rowlist:list) -> dict:
        o = {}
        [o.update(x[1]) for x in rowlist] if isinstance(rowlist, list) and len(rowlist) > 0 else None
        return o if bool(o) else None

    lookup = { 
        "type": [{"16":["^ERROR$"]}, {"20":["^ELEMENTS_ACTIONS$"]}]
    }
    
    return buildObj(parseObj(lookup, obj))
    

def getIdentification(eventdict:dict, idmap:dict) -> dict:
    d = eventdict.get('event')
    ecid = [ x.get('id') for x in idmap.get('ECID') ][0] if isinstance(idmap.get('ECID'), list) else None  
    profileid = [ x.get('id') for x in idmap.get('ProfileID') ][0] if isinstance(idmap.get('ProfileID'), list) else None
    if isinstance(ecid, str) and d.get('loginstatus') == "loggedOut":
        return {"Identification":{"ecid":ecid}}
    elif isinstance(ecid, str) and isinstance(profileid, str):
        return {"Identification":{"ecid":ecid, "profileid":profileid}}
    elif isinstance(profileid, str) and not isinstance(ecid, str):
        return {"Identification":{"profileid":profileid}}

def getIdentityAuth(eventdict:dict, idmap:dict) -> dict:
    cd = eventdict.get('event')
    authenticatedstate = [ x.get('authenticatedState') for x in idmap.get('FPID') ][0] if isinstance(idmap.get('FPID'), list) else None  
    ecid = [ x.get('id') for x in idmap.get('ECID') ][0] if isinstance(idmap.get('ECID'), list) else None  
    fpid = [ x.get('id') for x in idmap.get('FPID') ][0] if isinstance(idmap.get('FPID'), list) else None  
    profileid = [ x.get('id') for x in idmap.get('ProfileID') ][0] if isinstance(idmap.get('ProfileID'), list) else None
    customerid = [ x.get('id') for x in idmap.get('CustomerID') ][0] if isinstance(idmap.get('CustomerID'), list) else None
    identitymap = {}
    
    if cd.get('loginstatus') == "loggedOut":
        identitymap['FPID'] = [{"id":fpid, "authenticatedState":"loggedOut", "primary": True}]
        if isinstance(idmap.get('ECID'), list):
            identitymap['ECID'] = idmap.get('ECID')
        return identitymap

    identitymap['FPID'] = [{"id":fpid, "authenticatedState":authenticatedstate, "primary": True}]
    if isinstance(idmap.get('ECID'), list):
        identitymap['ECID'] = idmap.get('ECID')
    identitymap['ProfileID'] = idmap.get('ProfileID')
    #identitymap['CustomerID'] = idmap.get('CustomerID')
    return identitymap

def getEvent(obj:dict, application:dict, environment:dict, webobj:dict, customdimensions:dict, eventmetrics:dict, identification:dict, idmap:dict) -> dict:
    hitid = webobj.get('event',{}).get('hitid')
    web = [ x.get('web') for x in webobj.get('webevent') if x.get('web')][0] if isinstance(webobj.get('webevent'), list) else None
    eventtype = [ x.get('eventtype') for x in webobj.get('webevent') if x.get('eventtype')][0] if isinstance(webobj.get('webevent'), list) else None
    o = {"_id":hitid}
    o.update(application) if isinstance(application, dict) else None
    o.update(environment)
    o.update({"eventType":eventtype})
    o.update({"web":web})
    analytics = {}
    analytics.update({"customDimensions":customdimensions}) if isinstance(customdimensions, dict) else None
    analytics.update({"event1to100":eventmetrics}) if isinstance(eventmetrics, dict) else None
    o.update({"_experience":{"analytics":analytics}}) if bool(analytics) else None
    o.update({"_ing_intermediairs":identification}) if isinstance(identification, dict) else None 
    o.update({"identityMap":getIdentityAuth(obj, idmap)})
    o.update({"timestamp":obj.get('timestamp',{}).get('utc_iso')})
    o.update({"receivedTimestamp":obj.get('timestamp',{}).get('utc_iso_increment')})
    return {"event":{"xdm":o}, "query":{"identity":{"fetch":["ECID"]}}}

def buildRequest(index:int, eventlist:list, token:dict, request:dict, eventfile:str) -> dict:
    timestamp = class_converttime.Converttime({}).getTimestamp({"increment":300})
    url = request.get('url')
    streamid = request.get('streamid')
    idmap = getIdentityMap(timestamp, request)
    event = class_files.Files({}).readJson(eventfile)
    obj = {"index":index, "timestamp":timestamp, "eventlist":eventlist, "event":event, "request":request}
    application = getApplication(obj)
    environment = getEnvironment(obj)
    webobj = getWeb(obj)
    customdimensions = getCustomDimensions(obj, environment, webobj, idmap)
    eventmetrics = getEventMetrics(obj, environment, webobj, customdimensions, idmap)
    identification = getIdentification(obj, idmap)
    data = getEvent(obj, application, environment, webobj, customdimensions, eventmetrics, identification, idmap)
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
    printCol("green", eventfile)
    reqbuild = buildRequest(index, eventlist, token, request, eventfile)
    if isinstance(reqbuild, dict):
        printCol("yellow", json.dumps(reqbuild.get('data')))
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


