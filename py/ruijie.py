import sys

import httpx

# 替换为用户名
userId = ""

# 替换为密码
password = ""


# 这里判断是否已经属于登录状态 如果是则退出脚本
response = httpx.get("http://www.google.cn/generate_204", follow_redirects=True, timeout=10)
if response.status_code == 204:
    print('You are already online!')
    sys.exit(0)

# ip地址替换为锐捷认证的ip，例如：192.0.1.128
loginURL = 'http://192.168.2.135/eportal/InterFace.do?method=login'

if len(sys.argv) <= 1:
    print("参数错误")
    sys.exit(0)
elif sys.argv[1] == "xyw":
    # service是运营商中文经过两次UrlEncode编码的结果,
    # 提供编码网址为https://tool.chinaz.com/tools/urlencode.aspx
    service = 'internet'
elif sys.argv[1] == "dx":
    # service是运营商中文经过两次UrlEncode编码的结果,
    # 提供编码网址为https://tool.chinaz.com/tools/urlencode.aspx
    # 例如：电信出口 这四个中文字符经过两次UrlEncode得到如下结果，如果使用其他运营商请自行修改
    service = "%E7%94%B5%E4%BF%A1%E5%87%BA%E5%8F%A3"
else:
    print("参数错误")
    sys.exit(0)

# 此处参数已混淆，需要使用chrome浏览器F12打开控制台
# 复制你成功登录的queryString进行替换即可
# 要是登录太快来不及复制就Network把网络请求速度调至最低的1kb/s
queryString = "wlanuserip%3D"
# queryString = queryString.replace("&", "%2526").replace("=", "%253D")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60",
    "Referer": loginURL,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

cookies = {
    "EPORTAL_COOKIE_USERNAME": "",
    "EPORTAL_COOKIE_PASSWORD": "",
    "EPORTAL_COOKIE_SERVER": "",
    "EPORTAL_COOKIE_SERVER_NAME": "",
    "EPORTAL_AUTO_LAND": "",
    "EPORTAL_USER_GROUP": "",
    "EPORTAL_COOKIE_OPERATORPWD": ""
}

data = {
    "userId": userId,
    "password": password,
    "service": service,
    "queryString": queryString,
    "operatorPwd": "",
    "operatorUserId": "",
    "validcode": "",
    "passwordEncrypt": "false"
}

auth = httpx.post(loginURL, headers=headers, cookies=cookies, data=data)
print(auth.text)
