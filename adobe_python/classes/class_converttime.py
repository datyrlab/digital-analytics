#!/usr/bin/python3 

import collections, datetime, json, os, platform, random, re, shutil, subprocess, sys, time
from typing import Any, Callable, Dict, Optional, Union 

import math, copy
import numpy as np, numpy.random

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)

class Converttime:      

    def __init__(self, config:dict):
        self.config = config
    
    def convert_time(self, kwargs:dict) -> dict:
        def timestampToSeconds(timestring:str) -> dict:
            h,m,s = timestring.split(':')
            result = {}
            result['ts'] = timestring
            result['ms'] = float(datetime.timedelta(hours=int(h),minutes=int(m),seconds=float(s)).total_seconds())
            return result

        def secondsToTimestamp(timestring:str) -> dict:
            command = f"date -d@{timestring} -u +%H:%M:%S.%3N"
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            result = {}
            result['ts'] = output.strip().decode("utf-8")  
            result['ms'] = float(timestring)
            return result

        TIMESTRING = str(kwargs.get('timestring'))
        return timestampToSeconds(TIMESTRING) if re.findall("([0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3})", TIMESTRING, re.DOTALL) else secondsToTimestamp(TIMESTRING)

    def getTimestamp(self, kwargs:dict) -> dict:
        increment = kwargs.get('increment') if kwargs.get('increment') else 0
        now = datetime.datetime.now()
        f = now.timestamp()
        ts = math.floor(f)
        ms = int(f * 1000)
        ms_increment = int((f+increment) * 1000)
        date = now.strftime("%Y%m%d")
        utc_iso = datetime.datetime.utcfromtimestamp(f).isoformat()
        utc_iso_increment = datetime.datetime.utcfromtimestamp(f+increment).isoformat()
        return {"date":date, "float":f, "integer":ts, "ms":ms, "ms_increment":ms_increment, "utc_iso":f"{utc_iso[:-3]}Z", "utc_iso_increment":f"{utc_iso_increment[:-3]}Z"}







