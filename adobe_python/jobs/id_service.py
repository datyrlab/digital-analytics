#!/usr/bin/python3

import argparse, configparser, datetime, json, os, platform, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint
import uuid

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess

timestamp_numeric = int(time.time() * 1000.0)
dir_device = f"{project_dir}/myfolder/device"

def getTimestamp() -> int:
    date_time = datetime.datetime.now()
    if re.search("^Windows", platform.platform()):
        return int(date_time.timestamp())
    return date_time.strftime('%s')

def randomUniqueString() -> str:
    return uuid.uuid4()
    #return uuid.uuid4().hex[:25].upper()

def getEnvVars() -> dict:
    config_parser = configparser.ConfigParser()
    config_parser.read(os.environ['ADOBE_CONFIG'])
    config = dict(config_parser["default"])
    return {"orgid":config.get('orgid')}

def getCommand(ecid:int) -> str:
    t = getEnvVars()
    ts = getTimestamp()
    u = []
    u.append(f"https://dpm.demdex.net/id")
    u.append(f"?d_visid_ver=2.5.0")
    u.append(f"&d_fieldgroup=MC")
    u.append(f"&d_rtbd=json")
    u.append(f"&d_ver=2")
    u.append(f"&d_verify=1")
    u.append(f"&d_nsid=0")
    u.append(f"&d_orgid={t.get('orgid')}")
    if ecid:
        u.append(f"&ts={ecid}")
    u.append(f"&ts={ts}")
    url = "".join(u)

    s = []
    #s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl -v")
    s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
    s.append(f"-X GET {url}")
    command = " ".join(s)
    return {"timestamp":ts, "command":command} 

def fpidNew() -> dict:
    i = randomUniqueString()
    directory = f"{dir_device}/{i}"
    makeDirectory(directory)
    return ecidNew({"directory":directory, "id":str(i)})

def fpidGet(directory:str) -> str:
    filelist = os.listdir(directory) if os.path.exists(directory) else None
    if isinstance(filelist, list) and len(filelist) > 0:
        paths = [os.path.join(directory, basename) for basename in filelist]
        return max(paths, key=os.path.getctime)

def ecidNew(fpid:dict) -> dict:
    r = getCommand(None)
    run = class_subprocess.Subprocess({}).run(r.get('command'))
    try:
        response = json.loads("{\""+ run +"}") if re.search("^id", run) else run
        end_seconds = int(r.get('timestamp'))+int(response.get('id_sync_ttl'))
        request = {"command":r.get('command'), "timestamp":int(r.get('timestamp'))}
        response['timestamp'] = {"start":{"seconds":int(r.get('timestamp')), "string":datetime.datetime.fromtimestamp(int(r.get('timestamp'))).strftime("%A, %B %d, %Y %I:%M:%S")}, "end":{"seconds":end_seconds, "string":datetime.datetime.fromtimestamp(end_seconds).strftime("%A, %B %d, %Y %I:%M:%S")}}
        filepath = f"{fpid.get('directory')}/{response.get('id')}.json"
        c = {"fpid":fpid, "ecid":response}
        class_files.Files({}).writeFile({"file":filepath, "content":json.dumps(c, sort_keys=False, default=str)})  
        print("ecid:", response.get('id')) if isinstance(response, dict) else print("error:", run)
        return c
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e) 

def makeDirectory(directory:str) -> None:
    if isinstance(directory, str) and not os.path.exists(directory):
        os.makedirs(directory)



