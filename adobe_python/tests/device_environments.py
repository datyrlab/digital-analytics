#!/usr/bin/python3

ipaddress = "157.97.122.50"

def desktop() -> dict:
    return {"environment":{
        "ipV4":ipaddress,
        "browserDetails":{
            "acceptLanguage": "en",
            "cookiesEnabled": True,
            "javaScriptEnabled": True,
            "javaScriptVersion": "1.8.5",
            "javaEnabled": True,
            "javaVersion": "Java SE 8",
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
            "viewportHeight":937,
            "viewportWidth":835
        },
        "colorDepth": 24,
        "language": "en",
        "operatingSystem": "IOS",
        "operatingSystemVersion": "16.5"
    }}

def mobileBrowser() -> dict:
    return {"environment":{
        "ipV4":ipaddress,
        "browserDetails":{
            "acceptLanguage": "en",
            "cookiesEnabled": True,
            "javaScriptEnabled": True,
            "javaScriptVersion": "1.8.5",
            "javaEnabled": True,
            "javaVersion": "Java SE 8",
            "userAgent":"Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36",
            "viewportHeight":1024,
            "viewportWidth":700,
            "userAgentClientHints":{
                "mobile": True
            }
        },

        "carrier":"vodaphone",
        "device":{
            "colorDepth": 24,
            "connectionType": "mobile",
            "manufacturer": "Samsung",
            "model": "SM-S906N",
            "screenHeight": 1536,
            "screenWidth": 722,
            "screenOrientation": "Portrait",
            "type":"browser"
        },
        "language": "en",
        "operatingSystem": "Android",
        "operatingSystemVersion": "12"
    }}


def mobileApp() -> dict:
    return {"environment":{
        "ipV4":ipaddress,
        "device":{
            "colorDepth": 24,
            "connectionType": "mobile",
            "manufacturer": "Samsung",
            "model": "SM-S906N",
            "screenHeight": 1536,
            "screenWidth": 722,
            "screenOrientation": "Portrait",
            "type":"application"
        },
        "language": "en",
        "operatingSystem": "Android",
        "operatingSystemVersion": "12"
    }}



