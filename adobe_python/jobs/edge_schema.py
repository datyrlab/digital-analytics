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
            print(f"{k}: {v}") if isinstance(v, str) or isinstance(v, list)  else print(f"\033[1;33m{k}: {str(type(v))}\033[0m") 

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


