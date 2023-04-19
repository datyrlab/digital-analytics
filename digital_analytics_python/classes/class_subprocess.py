import collections, datetime, json, os, platform, random, re, shutil, subprocess, sys, time
from typing import Any, Callable, Dict, Optional, Union 

import math, copy
import numpy as np, numpy.random

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)

class Subprocess:      

    def __init__(self, config:dict):
        self.config = config
    
    # tag::runGetDict[]
    def runGetDict(self, command:str) -> dict:
        """ returns a dictionary """
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        return json.loads("{" + stdout.strip()[2:-1].decode("utf-8") + "}")

    # end::runGetDict[]


    # tag::run[]
    def run(self, command:str) -> Any:
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        return output.strip()[2:-1].decode("utf-8")     

    # end::run[]
