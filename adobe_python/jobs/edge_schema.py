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
        for k, v in d.items():
            print(f"{k}: {v}") if isinstance(v, str) or isinstance(v, list) else print(f"\033[1;33m{k}: {str(type(v))}\033[0m") 
        for k, v in d.items():
            if isinstance(v, dict):
                print(f"\033[1;36m{k}: {str(type(v))}\033[0m")
                
                parseProperties(v.get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties'))

                #parseProperties(v.get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties'), "customDimensions")
                #parseProperties(v.get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties'), "endUser")
                #parseProperties(v.get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties'), "environment")

                """
                parseKeys(properties)
                parseFields("^eVar", v.get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties',{}).get('customDimensions',{}).get('properties',{}).get('eVars',{}).get('properties'))
                parseFields("^hier", v.get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties',{}).get('customDimensions',{}).get('properties',{}).get('hierarchies',{}).get('properties',{}))
                parseFields("^prop", v.get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties',{}).get('customDimensions',{}).get('properties',{}).get('listProps',{}).get('properties'))
                parseFields("^List", v.get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties',{}).get('customDimensions',{}).get('properties',{}).get('lists',{}).get('properties'))
                #parseFields("^none", v.get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties',{}).get('customDimensions',{}).get('properties',{}).get('postalCode',{}))
                parseFields("^none", v.get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties',{}).get('endUser',{}).get('properties'))
                parseFields("^none", v.get('_experience',{}).get('properties',{}).get('analytics',{}).get('properties',{}).get('environment',{}).get('properties'))
                """

def parseProperties(properties:dict):
    if isinstance(properties, dict):
        for k in properties.keys():
            parseObj(k, properties.get(k)) if isinstance(properties.get(k), dict) else None

def parseObj(pk:str, properties:dict):
    for k, v in properties.items():
        parseObjProperties(pk, v) if isinstance(v, dict) else None # k = properties

def parseObjProperties(pk:str, properties:dict):
    for k, v in properties.items():
        parseFields(pk, k, v)

def parseFields(pk:str, key:str, properties:dict):
    for k, v in properties.items():
        #int(pk, key, v) if isinstance(v, dict) else None # k = properties
        parseFieldNames(pk, key, v)  if isinstance(v, dict) else None # k = properties

def parseFieldNames(pk:str, key:str, properties:dict):
    for k, v in properties.items():
        print(pk, key, k, v) if isinstance(v, dict) else None # k = properties



def parsePropertiesy(properties:dict, pk):
    if isinstance(properties, dict) and isinstance(properties.get(pk,{}).get('properties'), dict):
        p = properties.get(pk,{}).get('properties')
        {k:parseFields(f"{pk}\t{k}", v) for (k, v) in p.items()} 
    else:
        print(type(properties))

def parsePropertiesx(item:dict):
    if isinstance(item, dict) and isinstance(item.get('properties'), dict):
        {k:parseFields(k, v.get(k)) for (k, v) in item.get('properties').items() if isinstance(v, dict)} 

def parseFieldsx(pk:str, properties:dict):
    if isinstance(properties, dict):
        for k, v in properties.items():
            if isinstance(v, dict):
                print(f"{pk}\t{k}\t{ v.get('title')}\t{v.get('type')}\t{v.get('description')}")
                parseNested(k, v.get('properties'))

def parseNested(parentKey:str, properties:dict):
    if isinstance(properties, dict):
        for k, v in properties.items():
            print(f"{parentKey} -> {k}\t{ v.get('title')}\t{v.get('type')}\t{v.get('description')}")
            parseNested(f"{parentKey} -> {k}", v.get('properties'))

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


