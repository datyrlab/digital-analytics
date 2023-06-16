#!/usr/bin/python3

import datetime, json, os, platform, re, sys, unittest, time

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)
from adobe_python.classes import class_converttime, class_files, class_subprocess 

class TestTimeStamp(unittest.TestCase):
    
    def test_timeSecondsUnix(self):
        n = datetime.datetime.now()
        s = n.strftime('%s')
        print("seconds unix ===>", s)
    
    def test_getUtcNow(self) -> int:
        s = datetime.datetime.utcnow().isoformat()
        print("getUtcNow ====>", f"{s[:-3]}Z")

    def timestampWindows(self):
        increment  = 300
        now = datetime.datetime.now()
        f = now.timestamp()
        utc_iso = datetime.datetime.utcfromtimestamp(f).isoformat()
        utc_iso_increment = datetime.datetime.utcfromtimestamp(f+increment).isoformat()
        r = {"float":f, "integer":int(f), "utc_iso":f"{utc_iso[:-3]}Z", "utc_iso_increment":f"{utc_iso_increment[:-3]}Z"}
        print(r) 

    def timestampWindows(self):
        increment = 300
        ts = int(time.time())
        dt = datetime.datetime.fromtimestamp(ts)
        date = dt.strftime("%Y%m%d")
        ms = ts * 1000
        utc_iso = datetime.datetime.utcfromtimestamp(ts).isoformat()
        utc_iso_increment = datetime.datetime.utcfromtimestamp(ts+increment).isoformat()
        r = {"date":date, "ms":ms, "utc_iso":f"{utc_iso[:-3]}Z", "utc_iso_increment":f"{utc_iso_increment[:-3]}Z"}
        print(r) 

    def test_timestampWindows(self):
        increment = 300
        ts = class_converttime.Converttime({}).getTimestamp({"increment":300})
        print(ts) 

if __name__ == '__main__':
    unittest.main()

