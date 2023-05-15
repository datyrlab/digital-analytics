# Digital Analytics tools

## Data Insertion

```
python3 digital-analytics/adobe_python/jobs/data_insertion.py \
-re '{"url":"https://example.sc.omtrdc.net/b/ss//6", "eventlist":["myfolder/adobe-events/test.xml"]}'
```

Windows
```
python digital-analytics/adobe_python/jobs/data_insertion.py `
-re '{\"url\":\"https://example.sc.omtrdc.net/b/ss//6\", \"eventlist\":[\"myfolder/adobe-events/test.xml\"]}'
```

## ID service (get/ refresh visitor ECID) 
```
python3 digital-analytics/adobe_python/tests/test_ecid.py
```

## Datastream

## Config.ini, JWT connection
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

json file includes identityMap
```
python3 digital-analytics/adobe_python/jobs/data_insertion.py \
--re '{"streamid":"xxxxxx", "eventlist":["adobe_python/json/test-identitymap.json"]}'
```

command includes identityMap
```
python3 digital-analytics/adobe_python/jobs/data_insertion.py \
--re '{"streamid":"xxxxxx", "identityMap":{"Email_LC_SHA256": [{"id":"4ffccd7323a0085c7785c81c668f6f3507c21d999255e454d7f9bc68c1f82ac8", "primary": true}]}, "eventlist":["adobe_python/json/test.json"]}'
```

get a random identityMap from file
```
python3 digital-analytics/adobe_python/jobs/data_insertion.py \
--re '{"streamid":"xxxxxx", "identityMap":"adobe_python/json/profilelist.json", "delay":true, "eventlist":["adobe_python/json/test-identitymap.json", "adobe_python/json/test.json"]}'
```

Windows
```
python digital-analytics/adobe_python/jobs/data_insertion.py `
-re '{\"streamid\":\"xxxxxx\", "eventlist\":[\"adobe_python/json/test.json\"]}'
```

## api

Windows
```
python digital-analytics/adobe_python/jobs/api_admin.py `
-re '{\"get\":\"https://platform.adobe.io/data/foundation/schemaregistry/stats\", \"sandbox\":\"prod\", \"save\":\"admin\"}'
```

# data warehouse api 1.4
```
python digital-analytics/adobe_python/jobs/api_admin.py `
--re '{"post":"https://api.omniture.com/admin/1.4/rest/?method=DataSources.Get", "postdata":
{ \"reportDescription\": {
    \"reportSuiteID\": \"xxxx\",
    \"dateFrom\": \"2023-01-13 00:00:00\",
    \"dateTo\": \"2023-01-13 12:00:00\",
    \"fuzzyDates\": false, \"metrics\": [{\"id\": \"visits\"}],
    \"elements\": [{\"id\": \"page\"}],
    \"source\": \"warehouse\"
  }
}
}'
```



