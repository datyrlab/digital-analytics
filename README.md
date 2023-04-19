# Dgital Analytics tools

## Adobe Analytics Data Insertion

### Linux
```
python3 myprojects/digital-analytics-python/digital_analytics_python/jobs/data_insertion.py \
--re '{"type":"test", "url":"xxxx", "rsid":"xxxx", "marketingcloudorgid":"xxxx", "eventlist":[{"pageUrl":"https://example.com", "pageName":"Data Insertion API test (POST)"}]}'
```

### Windows
```
python myprojects/digital-analytics-python/digital_analytics_python/jobs/data_insertion.py `
--re '{"type":"test", "url":"xxxx", "rsid":"xxxx", "marketingcloudorgid":"xxxx", "eventlist":[{"pageUrl":"https://example.com", "pageName":"Data Insertion API test (POST)"}]}'
```
