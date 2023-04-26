# Digital Analytics tools

## Adobe Analytics Data Insertion, XML

### Linux
```
python3 digital-analytics/adobe_python/jobs/data_insertion.py \
--re '{"url":"https://example.sc.omtrdc.net/b/ss//6", "eventlist":["myfolder/adobe-events/test.xml"]}'
```

### Windows
```
python digital-analytics/adobe_python/jobs/data_insertion.py `
--re '{\"url\":\"https://example.sc.omtrdc.net/b/ss//6\", \"eventlist\":[\"myfolder/adobe-events/test.xml\"]}'
```

## Adobe Experience Cloud > Data Collection > Datastream, json/xdm
### Linux
```
python3 digital-analytics/adobe_python/jobs/data_insertion.py \
--re '{"url":"https://example.sc.omtrdc.net/b/ss//6", "streamid":"xxxxxx", eventlist":["myfolder/adobe-events/test.xml"]}'
```

### Windows
```
python digital-analytics/adobe_python/jobs/data_insertion.py `
--re '{\"url\":\"https://example.sc.omtrdc.net/b/ss//6\", \"streamid\":\"xxxxxx\", "eventlist\":[\"myfolder/adobe-events/test.xml\"]}'
```

## API 2.0 (config.ini, JWT connection)
```
[default]

#Go to https://console.adobe.io -> Select your integration and copy the client credential from "Overview"
#API Key (Client ID)
apiKey=API_KEY

#Technical account ID
technicalAccountId=TECH_ACCT_ID@techacct.adobe.com

#Organization ID
orgId=IMS_ORG_ID

#Client secret
secret=SECRET

#From "JWT" section of the integration
#scopes e.g. ent_analytics_bulk_ingest_sdk from "https://ims-na1.adobelogin.com/s/ent_analytics_bulk_ingest_sdk"
#metascopes=ent_analytics_bulk_ingest_sdk
metascopes=ent_dataservices_sdk

#Path to secret.key file for the certificate uploaded in console.adobe.io integration
key_path=secret.key

#URL Endpoints
imsHost=ims-na1.adobelogin.com
imsExchange=https://ims-na1.adobelogin.com/ims/exchange/jwt
discoveryUrl=https://analytics.adobe.io/discovery/me
analyticsApiUrl=https://analytics.adobe.io/api
```

### Test JWT connection
```
# returns an access token
python3 digital-analytics/adobe_python/tests/test_JWTaccesstoken.py
```



