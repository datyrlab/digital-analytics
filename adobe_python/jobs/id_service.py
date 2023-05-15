#!/usr/bin/python3

import argparse, configparser, datetime, json, os, platform, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess
from adobe_python.jobs import ims_client

timestamp_numeric = int(time.time() * 1000.0)
dir_fcid = f"{project_dir}/myfolder/adobe-fcid"
dir_cookies = f"{project_dir}/myfolder/adobe-cookies"
dir_cookies_for = f"{project_dir}/myfolder/adobe-cookies-format"
dir_cookies_exp = f"{project_dir}/myfolder/adobe-cookies-expired"


def getTimestamp() -> int:
    date_time = datetime.datetime.now()
    if re.search("^Windows", platform.platform()):
        return int(date_time.timestamp())
    return date_time.strftime('%s')

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

def idNew() -> None:
    """ response
            id: ECID
            id_sync_ttl: total seconds (7 days) the ECID is valid before a refresh
            dcs_region: nearest data center
    """
    r = getCommand(None)
    run = class_subprocess.Subprocess({}).run(r.get('command'))
    try:
        makeDirectory(dir_cookies)
        makeDirectory(dir_cookies_for)
        response = json.loads("{\""+ run +"}") if re.search("^id", run) else run
        end_seconds = int(r.get('timestamp'))+int(response.get('id_sync_ttl'))
        request = {"command":r.get('command'), "timestamp":int(r.get('timestamp'))}
        response['timestamp'] = {"start":{"seconds":int(r.get('timestamp')), "string":datetime.datetime.fromtimestamp(int(r.get('timestamp'))).strftime("%A, %B %d, %Y %I:%M:%S")}, "end":{"seconds":end_seconds, "string":datetime.datetime.fromtimestamp(end_seconds).strftime("%A, %B %d, %Y %I:%M:%S")}}
        class_files.Files({}).writeFile({"file":f"{dir_cookies}/{response.get('id')}.json", "content":json.dumps({"request":request, "response":response}, sort_keys=False, default=str)})  
        class_files.Files({}).writeFile({"file":f"{dir_cookies_for}/{response.get('id')}.json", "content":json.dumps({"request":request, "response":response}, sort_keys=False, indent=4, default=str)})  
        print("id:", response.get('id')) if isinstance(response, dict) else print("error:", run)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e) 
 
def idRefresh() -> None:
    pass

def makeDirectory(directory:str) -> None:
    if isinstance(directory, str) and not os.path.exists(directory):
        os.makedirs(directory)



