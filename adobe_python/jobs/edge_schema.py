#!/usr/bin/python3

import argparse, datetime, json, os, pandas, platform, re, sys, time
import pandas as pd
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess
from adobe_python.jobs import ims_client, oauth

timestamp_numeric = int(time.time() * 1000.0)
dir_admin = f"{project_dir}/myfolder/adobe-admin"
dir_schema = f"{project_dir}/myfolder/schema"
dir_schema_md = f"{project_dir}/myfolder/schema-markdown"

def main():
    imp = parseArgs(sys.argv)
    parseJson(imp.get('filelist'))
    createAdoc()

def parseArgs(argv) -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-im', '--import', dest='import')
    namespace = parser.parse_known_args(argv)[0]
    
    args = {k: v for k, v in vars(namespace).items() if v is not None}
    request = json.loads(args.get('import')) if isinstance(args.get('import'), str) else None
    return request

def parseJson(filelist:list) -> dict:
    if isinstance(filelist, list) and len(filelist) > 0:
        d = class_files.Files({}).readJson(f"{project_dir}/{filelist[0]}")
        parseTableTwoColumns("Overview", d)
        parseTableTwoColumns("Properties", d.get('properties'))
        
        _id = d.get('properties').get('_id')
        customDimensions = d.get('properties').get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties').get('customDimensions')
        advertising = d.get('properties').get('advertising')
        application = d.get('properties').get('application')
        channel = d.get('properties').get('channel')
        commerce = d.get('properties').get('commerce')
        dataSource = d.get('properties').get('dataSource')
        device = d.get('properties').get('device')
        directMarketing = d.get('properties').get('directMarketing')
        endUserIDs = d.get('properties').get('endUserIDs')
        environment = d.get('properties').get('environment')
        eventMergeId = d.get('properties').get('eventMergeId')
        eventType = d.get('properties').get('eventType')
        identityMap = d.get('properties').get('identityMap').get('additionalProperties').get('items')
        marketing = d.get('properties').get('marketing')
        media = d.get('properties').get('media')
        placeContext = d.get('properties').get('placeContext')
        producedBy = d.get('properties').get('producedBy')
        productListItems = d.get('properties').get('productListItems')
        profileStitch = d.get('properties').get('profileStitch').get('items')
        receivedTimestamp = d.get('properties').get('receivedTimestamp')
        search = d.get('properties').get('search')
        segmentMembership = d.get('properties').get('segmentMembership')
        segmentMemberships = d.get('properties').get('segmentMemberships')
        timestamp = d.get('properties').get('timestamp')
        userActivityRegion = d.get('properties').get('userActivityRegion')
        web = d.get('properties').get('web')
       
        #parseTable("_id", _id)
        parseObject("_id", _id)        
        
        parseTable("customDimensions", customDimensions.get('properties'))
        parseObject("customDimensions", customDimensions)        
        
        parseTable("advertising", advertising.get('properties'))
        parseObject("advertising", advertising)        
        
        parseTable("application", application.get('properties'))
        parseObject("application", application)        
        
        parseTable("channel", channel.get('properties'))
        parseObject("channel", channel)        

        parseTable("commerce", commerce.get('properties'))
        parseObject("commerce", commerce)        

        parseTable("dataSource", dataSource.get('properties'))
        parseObject("dataSource", dataSource)        

        parseTable("device", device.get('properties'))
        parseObject("device", device)        

        parseTable("directMarketing", directMarketing.get('properties'))
        parseObject("directMarketing", directMarketing)        

        parseTable("endUserIDs", endUserIDs.get('properties'))
        parseObject("endUserIDs", endUserIDs)        

        parseTable("environment", environment.get('properties'))
        parseObject("environment", environment)        
        
        parseTable("eventMergeId", eventMergeId)
        parseObject("eventMergeId", eventMergeId)        
        
        parseTable("eventType", eventType)
        parseObject("eventType", eventType)        

        parseTable("identityMap", identityMap.get('properties'))
        parseObject("identityMap", identityMap)        

        parseTable("marketing", marketing.get('properties'))
        parseObject("marketing", marketing)        

        parseTable("media", media.get('properties'))
        parseObject("media", media)        

        #parseTable("placeContext", placeContext.get('properties'))
        #parseObject("placeContext", placeContext)        

        #parseTable("producedBy", producedBy.get('properties'))
        #parseObject("producedBy", producedBy)        

        #parseTable("productListItems", productListItems.get('properties'))
        #parseObject("productListItems", productListItems)        

        parseTable("profileStitch", profileStitch.get('properties'))
        parseObject("profileStitch", profileStitch)        

        parseTable("receivedTimestamp", receivedTimestamp)
        parseObject("receivedTimestamp", receivedTimestamp)        
        
        parseTable("search", search.get('properties'))
        parseObject("search", search)        

        #parseTable("segmentMembership", segmentMembership.get('properties'))
        #parseObject("segmentMembership", segmentMembership)        

        #parseTable("segmentMemberships", segmentMemberships.get('properties'))
        #parseObject("segmentMemberships", segmentMemberships)        

        parseTable("timestamp", timestamp)
        parseObject("timestamp", timestamp)        

        parseTable("userActivityRegion", userActivityRegion.get('properties'))
        parseObject("userActivityRegion", userActivityRegion)        

        parseTable("web", web.get('properties'))
        parseObject("web", web)        
        

def createAdoc():
    filepath = f"{dir_schema}/index.adoc"
    directory = os.path.dirname(filepath)
    filelist = class_files.Files({}).listDirectory(directory)
    filesort = sortByName(filelist)
    c = [(lambda x: adocCodeBlock(x))(x) for x in filesort if not re.search("index.adoc", x) ] if isinstance(filesort, list) and len(filesort) > 0 else None     
    if isinstance(c, list) and len(c) > 0:
        s = []
        s.append("= Schema\n:doctype: book\n:experimental:\n:toc: left\n:source-highlighter: rouge\n:sectnums:\n")
        s.append("\n\n".join(c))
        os.remove(filepath) if os.path.exists(filepath) else None
        class_files.Files({}).writeFile({"file":filepath, "content":"\n".join(s)})

def adocCodeBlock(filepath:str):
    def letterCase(name:str):
        return name.lower() if name.isupper() == True else name # force all lower if all caps

    p = class_files.Files({}).fileProperties(filepath)
    plist = p.get('path').split("/")
    ext = re.sub('\.', '', p.get('file_extension'))
    name = letterCase(p.get('name'))
    s = []
    s.append(f"== {name}\n") if name[0].isupper() else s.append(f"=== {name}\n")
    if ext != "adoc":
        s.append(f"[source%nowrap,{ext}]")
        s.append("----")
        s.append(f"include::{filepath}[]")
        s.append("----\n")
    else:
        s.append(f"include::{filepath}[]")
        
    return "\n".join(s)

def sortByName(filelist:list) -> list:
    if isinstance(filelist, list) and len(filelist) > 0:
        filelist.sort()
        sorted(set(filelist), key=filelist.index)
        return filelist

def checkKey(d:dict, k:str):
    return k if k in d else False

def convertType(v):
    if isinstance(v, dict):
        return "object"
    if isinstance(v, list):
        return json.dumps(v)
    return str(v)

def parseTableTwoColumns(name:str, d:dict):
    s = []
    s.append("[cols=\"1,1\"]")
    s.append("|===")
    s.append("|Name|Type\n")
    {s.append(f"|{k}\n|{convertType(v)}\n") for (k, v) in d.items()}
    s.append("|===")
    c = "\n".join(s)
    filepath = f"{dir_schema}/{name}/{name.capitalize()}.adoc"
    writeFile(filepath, c)

def parseTable(name:str, d:dict):
    s = []
    s.append("[cols=\"1,1,1,1\"]")
    s.append("|===")
    s.append("|Name|Type|Title|Description\n")
    try:
        {s.append(f"|{k}\n|{v.get('type')}\n|{v.get('title')}\n|{v.get('description')}\n") for (k, v) in d.items()}
    except:
        pass
    finally:
        s.append(f"|{name}\n|{d.get('type')}\n|{d.get('title')}\n|{d.get('description')}\n")
    s.append("|===")
    c = "\n".join(s)
    filepath = f"{dir_schema}/{name}/{name.capitalize()}.adoc"
    writeFile(filepath, c)

def propertiesToList(filepath:str, d:dict):
    if isinstance(d, dict) and d.get('properties'):
        l = [{k:v} for (k, v) in d.get('properties').items()]
        writeFile(filepath, l)
        return l
    writeFile(filepath, d)
    return d

def writeFile(filepath, d:Any) -> None:
    directory = os.path.dirname(filepath) 
    makeDirectory(directory)
    c = json.dumps(d, sort_keys=False, indent=4, default=str) if re.search(".json$", filepath) else d
    class_files.Files({}).writeFile({"file":filepath, "content":c}) if not os.path.exists(filepath) else None
 
def parseObject(name:str, d:dict):
    if d.get('properties'):
        for k in d.get('properties').keys():
            #print(d.get('properties').get(k))
            propertiesToList(f"{dir_schema}/{name}/{k}.json", d.get('properties').get(k))
    else:
        propertiesToList(f"{dir_schema}/{name}/{name}.json", d)

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


