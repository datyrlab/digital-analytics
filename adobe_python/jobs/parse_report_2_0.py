#!/usr/bin/python3

import argparse, datetime, json, os, pandas, platform, re, sys, time
import pandas as pd
import numpy as np
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess
from adobe_python.jobs import oauth

timestamp_numeric = int(time.time() * 1000.0)
dir_admin = f"{project_dir}/myfolder/analytics-parsed"
dir_schema = f"{project_dir}/myfolder/schema"
dir_schema_md = f"{project_dir}/myfolder/schema-markdown"

def main():
    imp = parseArgs(sys.argv)
    parseFilesToDf(imp)

def parseArgs(argv) -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-im', '--import', dest='import')
    namespace = parser.parse_known_args(argv)[0]
    
    args = {k: v for k, v in vars(namespace).items() if v is not None}
    imp = json.loads(args.get('import')) if isinstance(args.get('import'), str) else None
    return imp

def parseFilesToDf(imp:dict) -> dict:
    if isinstance(imp, dict):
        filelist = class_files.Files({}).listDirectory(f"{project_dir}/{imp.get('path')}", imp.get('pattern'))
        #df = pd.read_json('/Users/admin/apps/courses.json', orient='records')
        pd.set_option('display.max_columns', None)
        d = [(lambda x: pd.json_normalize( updateDict(class_files.Files({}).readJson(x), x) ))(x) for x in filelist if os.path.getsize(x) > 0] 
        df = pd.concat(d)
        df1 = df.replace(np.nan, None, regex=True) 
        #df1.sort_values(by=['date'])
        df2 = df1.rename(columns = lambda x : x.replace('.', '_'))
        print(df1)

def updateDict(d:dict, filepath:str) -> dict:
    return d

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


