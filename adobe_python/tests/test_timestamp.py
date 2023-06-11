#!/usr/bin/python3

import datetime, json, os, platform, re, sys, unittest, time

package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = os.path.dirname(package_dir)
sys.path.insert(0, project_dir)

class TestTimeStamp(unittest.TestCase):
    
    def test_timeSecondsUnix(self):
        n = datetime.datetime.now()
        s = n.strftime('%s')
        print("seconds unix ===>", s)
    
    def test_getUtcNow(self) -> int:
        s = datetime.datetime.utcnow().isoformat()
        print("getUtcNow ====>", f"{s[:-3]}Z")

    def test_timestampWindows(self):
        increment  = 300
        now = datetime.datetime.now()
        f = now.timestamp()
        utc_iso = datetime.datetime.utcfromtimestamp(f).isoformat()
        utc_iso_increment = datetime.datetime.utcfromtimestamp(f+increment).isoformat()
        r = {"float":f, "integer":int(f), "utc_iso":f"{utc_iso[:-3]}Z", "utc_iso_increment":f"{utc_iso_increment[:-3]}Z"}
        print(r) 

if __name__ == '__main__':
    unittest.main()

