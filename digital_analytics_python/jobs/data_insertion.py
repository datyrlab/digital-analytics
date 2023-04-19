#!/usr/bin/python3

import argparse, datetime, json, os, platform, re, sys, time
from typing import Any, Callable, Dict, Optional, Union
from pprint import pprint

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from digital_analytics_python.classes import class_converttime, class_files, class_subprocess

timestamp_numeric = int(time.time() * 1000.0)
directory = f"{project_dir}/myfolder/logs"

def main():
    request = parseArgs(sys.argv)
    parseRequest(request)

def parseArgs(argv) -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-re', '--request', dest='request')
    namespace = parser.parse_known_args(argv)[0]
    
    args = {k: v for k, v in vars(namespace).items() if v is not None}
    request = json.loads(args.get('request')) if isinstance(args.get('request'), str) else None
    return request

def parseRequest(r:dict) -> None:
    if isinstance(r, dict) and isinstance(r.get('eventlist'), list) and len(r.get('eventlist')) > 0:
        [(lambda x: xmlTest(i, r.get('url'), r.get('marketingcloudorgid'), r.get('rsid'), x))(x) for i, x in enumerate(r.get('eventlist'))] if r.get('type') == "test" else None
        [(lambda x: xmlWeb(i, r.get('url'), r.get('marketingcloudorgid'), r.get('rsid'), x))(x) for i, x in enumerate(r.get('eventlist'))] if r.get('type') == "web" else None
        [(lambda x: xmlMob(i, r.get('url'), r.get('marketingcloudorgid'), r.get('rsid'), x))(x) for i, x in enumerate(r.get('eventlist'))] if r.get('type') == "mobile" else None
        
def getTimestamp() -> int:
    date_time = datetime.datetime.now()
    return date_time.strftime('%s')

def xmlTest(index:int, url:str, marketingcloudorgid:str, rsid:str, r:dict) -> None:
    tsinteger = getTimestamp()
    s = []
    s.append(f"<?xml version=1.0 encoding=UTF-8?>")
    s.append(f"<request>")
    s.append(f"<reportSuiteID>{rsid}</reportSuiteID>")
    s.append(f"<visitorID>1286556420966514130</visitorID>")
    s.append(f"<pageURL>{r.get('pageUrl')}</pageURL>")
    s.append(f"<pageName>{r.get('pageName')}</pageName>")
    s.append(f"<timestamp>{tsinteger}</timestamp>")
    s.append(f"</request>")
    data = "".join(s)
    sendCommand(tsinteger, url, data)

def xmlWeb(index:int, url:str, marketingcloudorgid:str, rsid:str, r:dict) -> None:
    tsinteger = getTimestamp()
    s = []
    s.append(f"<?xml version=1.0 encoding=UTF-8?>")
    s.append(f"<request>")
    s.append(f"<sc_xml_ver>1.0</sc_xml_ver>")
    s.append(f"<marketingcloudorgid>{r.get('marketingcloudorgid')}</marketingcloudorgid>")
    s.append(f"<imregion></region>")
    s.append(f"<reportSuiteID>{rsid}</reportSuiteID>")
    s.append(f"<marketingCloudVisitorID>xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</marketingCloudVisitorID>")
    s.append(f"<resolution>1792x1120</resolution>")
    s.append(f"<browserHeight>1120</browserHeight>")
    s.append(f"<browserWidth>1792</browserWidth>")
    s.append(f"<colorDepth>30</colorDepth>")
    s.append(f"<cookiesEnabled>Y</cookiesEnabled>")
    s.append(f"<javaEnabled>N</javaEnabled>")
    s.append(f"<currencyCode>EUR</currencyCode>")
    s.append(f"<userAgent>Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0 Safari/537.36</userAgent>")
    s.append(f"<ipaddress>156.114.160.14</ipaddress>")
    s.append(f"<timestamp>{tsinteger}</timestamp>")
    s.append(f"<language></language>")
    s.append(f"<pageName>{r.get('pageName')}</pageName>")
    s.append(f"<pageUrl>{r.get('pageUrl')}</pageUrl>")
    s.append(f"<referrer>https://ebanking.test.ing.be/login/?xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</referrer>")
    s.append(f"<channel>{r.get('channel')}</channel>")
    s.append(f"<contextData>")
    s.append(f"<cea.pagename>{r.get('pageName')}</cea.pagename>")
    s.append(f"<cea.resolution>1792x1120</cea.resolution>")
    s.append(f"<cea.timestamp>{tsinteger}</cea.timestamp>")
    s.append(f"<cea.applicationname>daily-banking-app</cea.applicationname>")
    s.append(f"<cea.pagetype></cea.pagetype>")
    s.append(f"<cea.previouspagename>open:login</cea.previouspagename>")
    s.append(f"<cea.sitesubsection>overview</cea.sitesubsection>")
    s.append(f"<cea.category>dba</cea.category>")
    s.append(f"<cea.countrycode>be</cea.countrycode>")
    s.append(f"<cea.languagepagesetting>en</cea.languagepagesetting>")
    s.append(f"<cea.customerid>xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</cea.customerid>")
    s.append(f"<cea.loginstatus></cea.loginstatus>")
    s.append(f"<cea.marketingcloudid>xxxxxxxxxxxxxxxxxxxxxxxxxxxx</cea.loginstatus>")
    s.append(f"<cea.profiletype>PRVT</cea.profiletype>")
    s.append(f"<cea.profileid>_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</cea.profileid>")
    s.append(f"<cea.displaymode>regular</cea.displaymode>")
    s.append(f"<cea.terminalid></cea.terminalid>")
    s.append(f"<cea.languagebrowserdevice>nl-NL</cea.languagebrowserdevice>")
    s.append(f"<cea.branchid></cea.branchid>")
    s.append(f"<cea.offlineclickid></cea.offlineclickid>")
    s.append(f"<cea.partyUUID>xxxxxxxxxxxxxxxxxxxxxxxxxxxx</cea.partyUUID>")
    s.append(f"<cea.experiments></cea.experiments>")
    s.append(f"<cea.cookielevel>1</cea.cookielevel>")
    s.append(f"<cea.libraryversion>Android 1.4.2 | CEA 2.7.0-1681720306992</cea.libraryversion>")
    s.append(f"<cea.reference>Iap88vgSjE0Q7hUA</cea.reference>")
    s.append(f"</contextData>")
    s.append(f"</request>")
    s.append(f"\"")
    data = "".join(s)
    sendCommand(tsinteger, data)

def xmlMobile(index:int, url:str, marketingcloudorgid:str, rsid:str, r:dict) -> None:
    tsinteger = getTimestamp()
    s = []
    s.append(f"<?xml version=1.0 encoding=UTF-8?>")
    s.append(f"<request>")
    s.append(f"<sc_xml_ver>1.0</sc_xml_ver>")
    s.append(f"<marketingcloudorgid>{r.get('marketingcloudorgid')}</marketingcloudorgid>")
    s.append(f"<imregion></region>")
    s.append(f"<reportSuiteID>{rsid}</reportSuiteID>")
    s.append(f"<marketingCloudVisitorID>xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</marketingCloudVisitorID>")
    s.append(f"<resolution>360x800</resolution>")
    s.append(f"<browserHeight>800</browserHeight>")
    s.append(f"<browserWidth>360</browserWidth>")
    s.append(f"<colorDepth>24</colorDepth>")
    s.append(f"<cookiesEnabled>Y</cookiesEnabled>")
    s.append(f"<javaEnabled>N</javaEnabled>")
    s.append(f"<currencyCode>EUR</currencyCode>")
    s.append(f"<userAgent>Mozilla/5.0 (Linux; Android 13; SM-G998B)</userAgent>")
    s.append(f"<ipaddress>156.114.160.14</ipaddress>")
    s.append(f"<timestamp>{tsinteger}</timestamp>")
    s.append(f"<language></language>")
    s.append(f"<pageNamei>{r.get('pageName')}</pageName>")
    s.append(f"<pageUrl></pageUrl>")
    s.append(f"<referrer></referrer>")
    s.append(f"<channel></channel>")
    s.append(f"<languagedevice></languagedevice>")
    s.append(f"<products></products>")
    s.append(f"<contextData>")
    s.append(f"<cea.pagename>{r.get('pageName')}</cea.pagename>")
    s.append(f"<cea.resolution>360x800</cea.resolution>")
    s.append(f"<cea.timestamp>{tsinteger}</cea.timestamp>")
    s.append(f"<cea.applicationname>mobilebanking.be</cea.applicationname>")
    s.append(f"<cea.pagetype></cea.pagetype>")
    s.append(f"<cea.previouspagename></cea.previouspagename>")
    s.append(f"<cea.sitesubsection></cea.sitesubsection>")
    s.append(f"<cea.category></cea.category>")
    s.append(f"<cea.countrycode>be</cea.countrycode>")
    s.append(f"<cea.languagepagesetting>be</cea.languagepagesetting>")
    s.append(f"<cea.customerid></cea.customerid>")
    s.append(f"<cea.loginstatus></cea.loginstatus>")
    s.append(f"<cea.marketingcloudid>xxxxxxxxxxxxxxxxxxxxxxxxxxxx</cea.loginstatus>")
    s.append(f"<cea.profiletype></cea.profiletype>")
    s.append(f"<cea.profileid></cea.profileid>")
    s.append(f"<cea.displaymode></cea.displaymode>")
    s.append(f"<cea.terminalid></cea.terminalid>")
    s.append(f"<cea.languagebrowserdevice>nl-NL</cea.languagebrowserdevice>")
    s.append(f"<cea.branchid>nl-NL</cea.branchid>")
    s.append(f"<cea.offlineclickid>nl-NL</cea.offlineclickid>")
    s.append(f"<cea.partyUUID>xxxxxxxxxxxxxxxxxxxxxxxxxxxx</cea.partyUUID>")
    s.append(f"<cea.experiments></cea.experiments>")
    s.append(f"<cea.transactionid></cea.transactionid>")
    s.append(f"<cea.formtype></cea.formtype>")
    s.append(f"<cea.formname></cea.formname>")
    s.append(f"<cea.formname>unknownpurpose</cea.formname>")
    s.append(f"<cea.formoutcome></cea.formoutcome>")
    s.append(f"<cea.formstatus></cea.formstatus>")
    s.append(f"<cea.formstep>100</cea.formstep>")
    s.append(f"<cea.subproduct></cea.subproduct>")
    s.append(f"<cea.mobilemanufacturer>samsung</cea.mobilemanufacturer>")
    s.append(f"<cea.ossytem>Android</cea.ossytem>")
    s.append(f"<cea.osversion>13</cea.osversion>")
    s.append(f"<cea.mobilecarrier></cea.mobilecarrier>")
    s.append(f"<cea.devicename>SM-G998B</cea.devicename>")
    s.append(f"<cea.mobiledevicetype></cea.mobiledevicetype>")
    s.append(f"<cea.appversion>2023.7.0</cea.appversion>")
    s.append(f"<cea.libraryversion>Android 1.4.2 | CEA 2.7.0-1681720306992</cea.libraryversion>")
    s.append(f"<cea.reference>Iap88vgSjE0Q7hUA</cea.reference>")
    s.append(f"</contextData>")
    s.append(f"</request>")
    s.append(f"\"")
    data = "".join(s)
    sendCommand(tsinteger, url, data)

def sendCommand(tsinteger:int, url:str, data:str) -> None:
    if isinstance(data, str):
        command = f"curl -X POST \"{url}\" -H \"Accept: application/xml\" -H \"Content-Type: application/xml\" -d \"{data}\"" if re.search("^\<\?xml", data) else None
        run = class_subprocess.Subprocess({}).run(command)
        filepath = f"{directory}/{tsinteger}.xml" if re.search("^\<\?xml", data) else None
        if re.search("SUCCESS", run):
            makeDirectory(directory)
            class_files.Files({}).writeFile({"file":filepath, "content":data})     
        
def makeDirectory(directory:str) -> None:
    if isinstance(directory, str) and not os.path.exists(directory):
        os.makedirs(directory)

def getOs():
    pass

if __name__ == '__main__':
    time_start = time.time()
    main()
    #stop timer
    time_finish = time.time()
    start_time = datetime.datetime.fromtimestamp(int(time_start)).strftime('%Y-%m-%d %H:%M:%S')
    finish_time = datetime.datetime.fromtimestamp(int(time_finish)).strftime('%Y-%m-%d %H:%M:%S')
    finish_seconds = round(time_finish - time_start,3)
    t = class_converttime.Converttime(config={}).convert_time({"timestring":finish_seconds}) 
    print(f"Time start: {start_time}")
    print(f"Time finish: {finish_time} | Total time: {t.get('ts')}")


