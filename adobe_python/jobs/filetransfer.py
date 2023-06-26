#!/usr/bin/python3

import argparse, datetime, json, os, pandas, platform, re, sys, time
import paramiko, gzip, zipfile
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess
from adobe_python.jobs import ims_client, oauth

timestamp_numeric = int(time.time() * 1000.0)
dir_log = f"{project_dir}/myfolder/adobe/log"

def main():
    conn, transfer = parseArgs(sys.argv)
    sftp = connSFTP(conn)
    itemTransfer(sftp, conn, transfer)
    sftp.close()

def parseArgs(argv) -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-co', '--conn', dest='conn')
    parser.add_argument('-tr', '--transfer', dest='transfer')
    namespace = parser.parse_known_args(argv)[0]
    
    args = {k: v for k, v in vars(namespace).items() if v is not None}
    conn = json.loads(args.get('conn')) if isinstance(args.get('conn'), str) else None
    transfer = json.loads(args.get('transfer')) if isinstance(args.get('transfer'), str) else None
    return (conn, transfer)

def connSFTP(conn:dict) -> paramiko.sftp_client.SFTPClient:
    if isinstance(conn, dict):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(conn.get('host'), username=conn.get('user'), password=conn.get('pass'))
        return ssh.open_sftp()    

def getFilelistx(sftp:paramiko.sftp_client.SFTPClient, directory:dict, pattern:dict) -> None:
    if isinstance(sftp, paramiko.sftp_client.SFTPClient):
        sftp.chdir(directory) if isinstance(directory, str) else None
        l = sftp.listdir() 
        return [x.filename for x in sftp.listdir_attr() if re.search(pattern, x.filename)] if len(l) > 0 and pattern else [x.filename for x in sftp.listdir_attr()]

def getItemlist(sftp:paramiko.sftp_client.SFTPClient, directory:dict, transfer:dict) -> None:
    if isinstance(sftp, paramiko.sftp_client.SFTPClient):
        sftp.chdir(directory) if isinstance(directory, str) else None
        l = sftp.listdir() 
        if transfer.get('dirpattern'):
            return [x for x in l if re.search(transfer.get('dirpattern'), x)] if len(l) > 0 else [x for x in l]
        return [x.filename for x in sftp.listdir_attr() if re.search(transfer.get('filepattern'), x.filename)] if len(l) > 0 and transfer.get('filepattern') else [x.filename for x in sftp.listdir_attr()]

def itemTransfer(sftp:paramiko.sftp_client.SFTPClient, conn:dict, transfer:dict) -> None:
    itemlist = getItemlist(sftp, conn.get('directory'), transfer)
    if isinstance(itemlist, list) and len(itemlist) > 0:
        [(lambda x: parseFunc(sftp, transfer, x))(x) for x in itemlist]

def parseFunc(sftp:paramiko.sftp_client.SFTPClient, transfer:dict, item):
    [x(sftp, transfer, item) for x in [download]]

def download(sftp:paramiko.sftp_client.SFTPClient, transfer:dict, item):
    if isinstance(transfer.get('download'), str):
        directory = f"{project_dir}/{transfer.get('download')}"
        makeDirectory(directory) if isinstance(directory, str) else None
        properties = class_files.Files({}).fileProperties(item)
        target = os.path.join(directory, item)
        try:
            sftp.get(item, target)
            print(f"download success: {target}") if os.path.exists(target) else print(f"download fail: {target}")
            funclist = [uncompressZip]
            [f(target, directory) for f in funclist]

        except FileNotFoundError as e:
            print("File not found:", str(e))
        except PermissionError as e:
            print("Permission denied:", str(e))
        except Exception as e:
            print("Error occurred:", str(e))
            makeDirectory(dir_log)
            paramiko.util.log_to_file(f"{dir_log}/filetransfer-error.log", level=paramiko.util.DEBUG)
    
def remove(sftp:paramiko.sftp_client.SFTPClient, transfer:dict, item) -> None:
    if isinstance(transfer.get('remove'), bool) and transfer.get('remove') == True:
        sftp.rmdir(item) if isinstance(transfer.get('dirpattern'), str) else sftp.remove(item)

def uncompressZip(filepath, directory):
    if os.path.exists(filepath) and filepath.lower().endswith(('.zip')):
        with zipfile.ZipFile(filepath) as zf:
            zf.extractall(directory)
        os.remove(filepath)     

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


