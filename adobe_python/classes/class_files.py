#!/usr/bin/python3 

import collections, datetime, json, os, platform, random, re, shutil, subprocess, sys, time
from typing import Any, Callable, Dict, Optional, Union 

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)

class Files:      
    def __init__(self,config):
        self.config = config

    # tag::fileOrDirectory[]
    def fileOrDirectory(self, datapath:str) -> str:
        """ check if path is a directory or file """
        if isinstance(datapath, str) and os.path.exists(datapath):
            if os.path.isdir(datapath):
                return "dir"
            elif os.path.isfile(datapath):
                return "file"
    
    # end::fileOrDirectory[]


    # tag::list_directory[]
    def listDirectory(self, directory:str, pattern:Optional[str]=None) -> list:
        """ recursive list files in a directory  """
        def recursiveFilelist(directory):
            if os.path.exists(directory):
                filelist = []
                for dirpath, dirnames, filenames in os.walk(directory):
                    for filename in filenames:
                        filelist.append(os.path.join(dirpath, filename))
                return filelist

        def filterFiles(filelist:list, pattern:str) -> list:
            """ if pattern is included then filter files """
            return [x for x in filelist if re.search(rf"{pattern}", x)]

        filelist = recursiveFilelist(directory)
        return filelist if pattern == None else filterFiles(filelist, pattern) if pattern != "" else None
    
    # end::list_directory[]


    # tag::readFile[]
    def readFile(self, filepath:str) -> list:
        """ opens and reads a files, returns the content """
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                filelist = [line.strip() for line in f if line.strip()]
            f.close()
            return filelist

    # end::readFile[]
    

    # tag::readJson[]
    def readJson(self, filepath:str) -> dict:
        """ opens a file """
        if isinstance(filepath, str) and os.path.exists(filepath):
            def openJson(filepath):
                with open(filepath, "r") as f:
                    data = json.load(f)
                f.close()
                return data
            return openJson(filepath)
    
    # end::readJson[]


    # tag::writeFile[]
    def writeFile(self, kwargs:dict) -> None:
        """ writes content to a file, will open a new empty file if content is 'None' """
        def createEmptyFile(filepath:str, content:Any) -> None:
            os.mknod(filepath)
            
        def createFile(filepath:str, content:Any) -> None:
            with open(filepath, 'a') as out:
                out.write("{}\n".format(content))
            out.close() 
        
        def fileLogic(filepath:str, content:str):
            createFile(filepath, content) if content != None else None
            createEmptyFile(filepath, content) if content == None else None
            
        fileLogic(kwargs.get('file'), kwargs.get('content'))
    
    # end::writeFile[]


    # tag::fileProperties[]
    def fileProperties(self, filepath:str) -> dict:
        def getProperties(filepath:str) -> dict:
            today = datetime.datetime.today()
            hour = today.strftime("%H")
            month = today.strftime("%m")
            label = today.strftime("%Y%m%d_%H%M%S")
            
            path, filename = os.path.split(filepath)
            name, file_extension = os.path.splitext(filename)
            name_text = re.sub(r'-|_', ' ', name) # remove hyphens and underscores
            name_list = name_text.split(" ")

            result = {}
            result['fullpath'] = filepath
            result['path'] = path
            result['filename'] = filename
            result['name'] = name
            result['name_text'] = name_text
            result['name_list'] = name_list
            result['file_extension'] = file_extension
            result['current_time'] = int(time.time() * 1000.0)
            result['today'] = today
            return result 
        
        def getStats(properties:dict) -> dict:
            if os.path.exists(properties.get('fullpath')):
                stats = os.stat(properties.get('fullpath'))
                result = {}
                result['st_mode'] = stats.st_mode
                result['st_ino'] = stats.st_ino
                result['st_dev'] = stats.st_dev
                result['st_nlink'] = stats.st_nlink
                result['st_uid'] = stats.st_uid
                result['st_gid'] = stats.st_gid
                result['st_size'] = stats.st_size
                result['st_atime'] = stats.st_atime
                result['st_mtime'] = stats.st_mtime
                result['st_ctime'] = stats.st_ctime
                properties['stats'] = result
            return properties
        
        def getOrientation(width:int, height:int) -> str:
            if height > width:
                return "portrait"
            elif width > height:
                return "landscape"
            elif width == height:
                return "square" 

        def getImage(properties:str) -> dict:
            if isinstance(properties.get('stats'), dict) and "cv" in sys.modules:
                img = cv.imread(properties.get('fullpath'))
                if re.search(".jpg$|.JPG$|.png$|.PNG$", properties.get('file_extension')) and isinstance(img, np.ndarray):
                    height, width, channels = img.shape
                    result = {}
                    result['height'] = height
                    result['width'] = width
                    result['channels'] = channels
                    result['orientation'] = getOrientation(width, height)
                    properties["image"] = result
            return properties

        properties = getProperties(filepath)
        stats = getStats(properties)
        return getImage(stats)

    # end::fileProperties[]


    # tag::createFile[]
    def createFile(self, filepath:str, content:str, directory:Optional[str]=None) -> None:    
        os.makedirs(directory) if isinstance(directory, str) and not os.path.exists(directory) else None
        os.remove(filepath) if os.path.exists(filepath) else None
        Files(self.config).writeFile({"file":filepath, "content":content})
    
    # end::createFile[]






