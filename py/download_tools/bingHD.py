"""
cron: 30 2 * * *
new Env('Bing 每日壁纸下载');
"""

import ast
import datetime
import json
import os
import platform
import re

from bs4 import BeautifulSoup

from notify_dayepao import send_message
from utils_dayepao import http_request


def download():
    url = "https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=2&nc=1610239683659&pid=hp&uhd=1&uhdwidth=3840&uhdheight=2160"
    headers = {
        "X-Forwarded-For": "106.112.196.1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
    }
    res = http_request("get", url, headers=headers)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    jsonstr = json.loads(soup.text)
    images = str(jsonstr['images'])
    images = images[1:-2]
    images = images.split('}, ')
    key = 0
    while key < len(images):
        image = ast.literal_eval(images[key] + "}")
        imgurl = "https://cn.bing.com" + image['url']
        if platform.system() == 'Windows':
            filename = finalpath + "\\" + (''.join(re.findall('[，\u4e00-\u9fa5]', image['copyright'])) or image['enddate']) + ".jpg"
        else:
            filename = finalpath + "/" + (''.join(re.findall('[，\u4e00-\u9fa5]', image['copyright'])) or image['enddate']) + ".jpg"
        imgr = http_request("get", imgurl)
        print("正在下载 " + filename)
        para.messages.append(f"正在下载 {filename}")
        with open(filename, 'wb') as f:
            f.write(imgr.content)
        key = key + 1


def num():
    finalfiles = os.listdir(finalpath)
    num_img = len(finalfiles)
    return num_img


class para:
    messages = []


if __name__ == "__main__":
    finalpath = os.getenv("BINGHD_PATH")
    if not finalpath:
        print("未配置 BINGHD_PATH")
        os._exit(0)

    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    para.messages.append(f"{now}\n")
    para.messages.append(f"当前bingHD文件数：{str(num())}\n")

    download()

    para.messages.append(f"\n当前bingHD文件数：{str(num())}")

    send_message("Bing 每日壁纸下载", "\n".join(para.messages), ["console", "wecom_app"])
