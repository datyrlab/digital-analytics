#!/usr/bin/python3
import argparse, configparser, datetime, json, os, platform, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess

timestamp_numeric = int(time.time() * 1000.0)
dir_oauth = f"{project_dir}/myfolder/adobe/oauth"

def getAccessToken() -> dict:
    return getBearer(getEnv())
    
def getEnv() -> dict:
    config_parser = configparser.ConfigParser()
    config_parser.read(os.environ['ADOBE_CONFIG'])
    config = dict(config_parser["default"])
    return config

def getBearer(env:dict) -> dict:
    s = []
    s.append(f"curl.exe") if re.search("^Windows", platform.platform()) else s.append("curl")
    s.append(f"-X POST \"https://ims-na1.adobelogin.com/ims/token/v3?client_id={env.get('apikey')}\"")
    s.append(f"-H \"Content-Type: application/x-www-form-urlencoded\"")
    s.append(f"-d \"client_secret={env.get('secret')}&grant_type=client_credentials&scope={env.get('scope')}\"")
    #s.append(f"-d \"@{useFile(data)}\"") if re.search("^Windows", platform.platform()) else s.append(f"-d '{json.dumps(data)}'")
    command = " ".join(s)
    run = class_subprocess.Subprocess({}).run(command)
    response = json.loads("{\""+ run +"}") if re.search("^access_token", run) else run
    if isinstance(response, dict):
        f = f"{dir_oauth}/bearer.json"
        makeDirectory(dir_oauth)
        os.remove(f) if os.path.exists(f) else None
        class_files.Files({}).writeFile({"file":f, "content":json.dumps(response, sort_keys=False, default=str)})
        return {"token":response.get('access_token'), "apikey":env.get('apikey'), "orgid":env.get('orgid')}

def useFile(data:dict) -> str:
    makeDirectory(dir_tmp)
    filepath = f"{dir_tmp}/data.json"
    os.remove(filepath) if os.path.exists(filepath) else None
    class_files.Files({}).writeFile({"file":filepath, "content":json.dumps(data, sort_keys=False, default=str)})
    return filepath

def makeDirectory(directory:str) -> None:
    if isinstance(directory, str) and not os.path.exists(directory):
        os.makedirs(directory)

