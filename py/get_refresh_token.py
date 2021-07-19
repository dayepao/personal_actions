import json
from urllib import parse

import requests


def get_refresh_token():
    url1 = para.url + "/authorize?client_id=" + para.client_id + "&scope=" + "Files.Read.All Files.ReadWrite.All offline_access" + "&response_type=" + "code" + "&redirect_uri=" + para.redirect_uri
    print("请在浏览器中打开此地址进行登录和授权:" + url1)
    input_url = input("然后请输入浏览器地址栏重定向的地址:")
    params = parse.parse_qs(parse.urlparse(input_url).query)
    if 'code' not in params.keys():
        print("重定向的地址中找不到参数\"code\"，请检查")
        return
    code = "".join(params['code'])
    postdata = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': para.client_id,
        'client_secret': para.client_secret,
        'redirect_uri': para.redirect_uri
    }
    res = requests.post(para.url + "/token", data=postdata, headers=para.headers)
    if res.status_code == 200:
        jsonstr = json.loads(res.text)
        print(json.dumps(jsonstr, sort_keys=False, indent=4, separators=(',', ':')))
    else:
        print("错误")


def refresh_refresh_token():
    para.refresh_token = input("请输入refresh_token:")
    postdata = {
        'grant_type': 'refresh_token',
        'refresh_token': para.refresh_token,
        'client_id': para.client_id,
        'client_secret': para.client_secret,
        'redirect_uri': para.redirect_uri
    }
    res = requests.post(para.url + "/token", data=postdata, headers=para.headers)
    if res.status_code == 200:
        jsonstr = json.loads(res.text)
        print(json.dumps(jsonstr, sort_keys=False, indent=4, separators=(',', ':')))
    else:
        print("错误")


class para:
    url = "https://login.microsoftonline.com/common/oauth2/v2.0"
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }


para.client_id = input("请输入client_id:")
para.client_secret = input("请输入client_secret:")
para.redirect_uri = input("请输入redirect_uri(默认为 http://localhost):")
if para.redirect_uri == '':
    para.redirect_uri = 'http://localhost'
print("\n功能列表：\n1.获取refresh_token\n2.刷新refresh_token")
while True:
    key = input("请选择:")
    if key == "1":
        get_refresh_token()
        break
    if key == "2":
        refresh_refresh_token()
        break
    print("[错误]请重新输入")
