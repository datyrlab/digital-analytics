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


def main():
    imp = parseArgs(sys.argv)
    parseJson(imp.get('filelist'))
    #createAdoc()

def parseArgs(argv) -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-im', '--import', dest='import')
    namespace = parser.parse_known_args(argv)[0]
    
    args = {k: v for k, v in vars(namespace).items() if v is not None}
    imp = json.loads(args.get('import')) if isinstance(args.get('import'), str) else None
    return imp

def parseJson(filelist:list) -> None:
    if isinstance(filelist, list) and len(filelist) > 0:
        l = list(filter(None,[(lambda x: {"content":class_files.Files({}).readJson(f"{project_dir}/{x}"), "filepath":f"{project_dir}/{x}"})(x) for x in filelist if os.path.exists(f"{project_dir}/{x}") ]))
        [(lambda x: parse(x))(x) for x in l] if isinstance(l, list) and len(l) > 0 else None

def getKey(item:dict) -> str:
    if isinstance(item.get('events'), list):
        return "events"
    if isinstance(item.get('evars'), list):
        return "evars"
    if isinstance(item.get('list_variables'), list):
        return "list_variables"
    if isinstance(item.get('props'), list):
        return "props"

def parse(item:dict) -> None:
    if isinstance(item, dict):
        key = getKey(item.get('content'))
        if isinstance(key, str) and isinstance(item.get('content').get(key), list):
            rows = list(filter(None, [f(key, item.get('content').get(key)) for f in [dimensions, events]]))
            createAdoc(key, f"{os.path.splitext(item.get('filepath'))[0]}.adoc", rows[0]) if isinstance(rows, list) and len(rows) > 0 else None

def dimensions(key:str, l:list):
    if not re.search("events", key):
        return [f"|{x.get('id')}\n|{x.get('name')}\n|{x.get('enabled')}" for x in l if x.get('enabled') == True]

def events(key:str, l:list):
    if re.search("events", key):
        return [f"|{x.get('id')}\n|{x.get('name')}\n|{x.get('type')}\n|{x.get('participation')}\n|{x.get('serialization')}\n|{x.get('polarity')}" for x in l if not x.get('type') == "disabled"]

def createAdoc(key:str, filepath:str, rows:str) -> dict:
    if isinstance(rows, list):
        s = []
        s.append('[cols="1,1,1"]') if not re.search("events", key) else s.append('[cols="1,1,1,1,1,1"]')
        s.append("|===")
        s.append("|id|name|enabled\n") if not re.search("events", key) else s.append("|id|name|type|participation|serialization|polarity\n")
        s.append("\n\n".join(rows))
        s.append("|===")
        os.remove(filepath) if os.path.exists(filepath) else None
        class_files.Files({}).writeFile({"file":filepath, "content":"\n".join(s)})


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


