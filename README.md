# Digital Analytics tools

## Adobe Analytics Data Insertion

### Linux
```
python3 digital-analytics/adobe_python/jobs/data_insertion.py \
--re '{"url":"https://example.sc.omtrdc.net/b/ss//6", "eventlist":["myfolder/adobe-events/test.xml"]}'
```

### Windows
```
python3 digital-analytics/adobe_python/jobs/data_insertion.py `
--re '{\"url\":\"https://example.sc.omtrdc.net/b/ss//6\", \"eventlist\":[\"myfolder/adobe-events/test.xml\"]}'
```
