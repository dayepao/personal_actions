import json
import os
import random
import sys
import time

import httpx

from utils_dayepao import get_content_in_website, get_method, search_in_website


# 获取当前ip地址
def get_ip():
    api_url = "https://api.ipify.org/"
    res = get_method(api_url)
    res.raise_for_status()
    return res.text


# 登录
def login(username, password) -> httpx.Client:
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31",
        "origin": "https://hostloc.com",
        "referer": "https://hostloc.com/",
    }
    login_url = "https://hostloc.com/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1"
    login_data = {
        "fastloginfield": "username",
        "username": username,
        "password": password,
        "quickforward": "yes",
        "handlekey": "ls",
    }
    c = httpx.Client()
    c.headers.update(headers)
    res = c.post(url=login_url, data=login_data)
    res.raise_for_status()
    return c


# 检查登陆状态
def check_login_status(c: httpx.Client, i) -> bool:
    test_url = "https://hostloc.com/home.php?mod=spacecp"
    if search_in_website(test_url, "您需要先登录才能继续本操作", c=c):
        print("❌第{num}个账号登陆失败，请检查账号信息是否正确！".format(num=str(i)))
        return False
    print("✔️第{num}个账号登陆成功！".format(num=str(i)))
    return True


# 获取当前积分
def get_current_points(c: httpx.Client) -> list:
    url = "https://hostloc.com/forum.php"
    r_e = r"积分: (\d+)"
    points = get_content_in_website(url, r_e, c=c)
    return points


# 随机生成用户空间链接
def generate_random_space_url() -> list:
    url_list = []
    while len(url_list) < 12:  # 访问小黑屋用户空间不会获得积分、生成的随机数可能会重复，这里多生成两个链接用作冗余
        url_list.append("https://hostloc.com/space-uid-{uid}.html".format(uid=random.randint(10000, 50000)))
    return url_list


# 依次访问随机生成的用户空间链接获取积分
def get_points(c: httpx.Client):
    print("账号当前积分为: " + str(get_current_points(c)[0]))
    url_list = generate_random_space_url()
    for url in url_list:
        time.sleep(5)
        res = get_method(url, c=c)
        try:
            res.raise_for_status()
            print("第{i}个用户空间访问成功".format(i=str(url_list.index(url)+1)))
        except Exception as e:
            print("第{i}个用户空间访问失败: {e}".format(i=str(url_list.index(url)+1), e=str(e).replace("\n", "  ")))
            continue
    print("账号当前积分为: " + str(get_current_points(c)[0]))


if __name__ == "__main__":
    account = os.environ.get('HOSTLOC')  # {"username1": "password1", "username2": "password2"}
    if not account:
        print("未检测到hostloc账号，请检查环境变量是否设置正确！")
        sys.exit(0)
    account: dict = json.loads(account)

    print("当前IP: " + get_ip())
    print("共检测到{num}个账号，开始获取积分".format(num=str(len(account))))

    i = 1
    for username, password in account.items():
        print("*" * 60)
        c = login(username, password)
        if check_login_status(c, i):
            get_points(c)
        i += 1

    print("*" * 60)
    print("程序执行完毕，获取积分过程结束")
