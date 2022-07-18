import json

from utils_dayepao import post_method

endpoint = "https://graph.microsoft.com/v1.0"
access_token = input("请输入access_token: ")
duixiang_id = input("请输入对象ID: ")
password_name = input("请输入密码名称: ")


def add_password():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token,
    }
    postjson = {
        "passwordCredential": {
            "displayName": password_name,
            "endDateTime": "2299-12-31T00:00:00Z"
        }
    }
    res = post_method(endpoint + "/applications/" + duixiang_id + "/addPassword", postjson=postjson, headers=headers, timeout=None, max_retries=1)
    print(json.dumps(res.json(), sort_keys=False, indent=4, separators=(',', ':')))


add_password()
