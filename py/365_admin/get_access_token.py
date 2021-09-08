import json
from urllib import parse

import httpx


def set_scope(*args: str):
    return " ".join(args)


def get_access_token(client_id, client_secret, tenant_id):
    url = "https://login.microsoftonline.com/" + tenant_id + "/oauth2/v2.0/token"
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    postdata = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': set_scope(
            'https://graph.microsoft.com/.default'
        ),
        'grant_type': 'client_credentials'
    }
    res = httpx.post(url, data=postdata, headers=headers)
    if res.status_code == 200:
        jsonstr = json.loads(res.text)
        result = json.dumps(jsonstr, sort_keys=False, indent=4, separators=(',', ':'))
    else:
        result = "错误"
    return result


if __name__ == "__main__":
    client_id = input("请输入client_id: ")
    client_secret = input("请输入client_secret: ")
    tenant_id = input("请输入租户ID: ")
    redirect_uri = input("请输入redirect_uri(默认为 http://localhost): ")
    if redirect_uri == '':
        redirect_uri = 'http://localhost'
    request_url = "https://login.microsoftonline.com/" + tenant_id + "/adminconsent?client_id=" + client_id + "&redirect_uri=" + redirect_uri
    print("请在浏览器中打开此地址并进行授权: ")
    print(request_url)
    input_url = input("然后请输入浏览器地址栏重定向的地址: ")
    print("\n")

    if input_url == '':
        print("请输入重定向的地址")
    else:
        params = parse.parse_qs(parse.urlparse(input_url).query)
        params_json = {}
        if "error" in params.keys():
            if "error_description" in params.keys():
                result = "错误: " + "".join(params['error']) + "\n错误描述: " + "".join(params["error_description"])
            else:
                result = "错误: " + "".join(params['error']) + "\n错误描述: 未知"
        else:
            for key, value in params.items():
                params_json[key] = "".join(value)

            if ("admin_consent" not in params_json.keys()) or (params_json["admin_consent"] != "True"):
                result = "未知错误"
            else:
                result = get_access_token(client_id, client_secret, tenant_id)
        print(result)
