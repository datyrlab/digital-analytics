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

def main():
    imp = parseArgs(sys.argv)
    parseJson(imp.get('filelist'))

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
        parse(None, d)

        print()
        parse("properties", d.get('properties'))
        
        _id = d.get('properties').get('_id')
        customDimensions = d.get('properties').get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties').get('customDimensions')
        application = d.get('properties').get('application')
        channel = d.get('properties').get('channel')
        commerce = d.get('properties').get('commerce')
        environment = d.get('properties').get('environment')
        eventType = d.get('properties').get('eventType')
        identityMap = d.get('properties').get('identityMap').get('additionalProperties').get('items')
        profileStitch = d.get('properties').get('profileStitch').get('items')
        receivedTimestamp = d.get('properties').get('receivedTimestamp')
        timestamp = d.get('properties').get('timestamp')
        web = d.get('properties').get('web')
        
        print("\n_id")
        print(_id)
        
        parse("customDimensions", customDimensions.get('properties'))
        parseObject("customDimensions", customDimensions)        
        
        parse("web", web.get('properties'))
        parseObject("web", web)        
        
        parse("application", application.get('properties'))
        parseObject("application", application)        
        
        parse("channel", channel.get('properties'))
        parseObject("channel", channel)        

        parse("commerce", commerce.get('properties'))
        parseObject("commerce", commerce)        

        parse("environment", environment.get('properties'))
        parseObject("environment", environment)        

        parse("eventType", eventType)
        parseObject("eventType", eventType)        

        parse("identityMap", identityMap.get('properties'))
        parseObject("identityMap", identityMap)        

        parse("profileStitch", profileStitch.get('properties'))
        parseObject("profileStitch", profileStitch)        

        parse("receivedTimestamp", receivedTimestamp)
        parseObject("receivedTimestamp", receivedTimestamp)        

        parse("timestamp", timestamp)
        parseObject("timestamp", timestamp)        


def checkKey(d:dict, k:str):
    return k if k in d else False

def parse(name, d:dict):
    print(name)
    #{print(f"{k}\t{v}") if not isinstance(v, dict) else print(f"\033[1;33m{k}\t{str(type(v))}\033[0m") for (k, v) in d.items()} 
    {print(f"{k}\t{v}") if not isinstance(v, dict) else print(f"{k}\t{str(type(v))}") for (k, v) in d.items()} 

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
    class_files.Files({}).writeFile({"file":filepath, "content":json.dumps(d, sort_keys=False, indent=4, default=str)}) if not os.path.exists(filepath) else None
 
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


