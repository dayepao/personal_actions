import ast
import datetime
import json
import os
import re

import requests
from bs4 import BeautifulSoup


def download():
    url = "https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=2&nc=1610239683659&pid=hp&uhd=1&uhdwidth=3840&uhdheight=2160"
    headers = {'X-Forwarded-For': '106.112.196.1'}
    res = requests.get(url, headers=headers)
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
        filename = finalpath + "\\" + (''.join(re.findall('[，\u4e00-\u9fa5]', image['copyright'])) or image['enddate']) + ".jpg"
        imgr = requests.get(imgurl)
        print("正在下载 " + filename)
        para.pushstr = para.pushstr + "正在下载" + filename + "\n\n"
        with open(filename, 'wb') as f:
            f.write(imgr.content)
        key = key + 1


def num():
    finalfiles = os.listdir(finalpath)
    num_img = len(finalfiles)
    return num_img


class para:
    pushstr = ""


finalpath = 'bingHD'

now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d %H:%M:%S")
para.pushstr = now + "\n\n" + "当前bingHD文件数：" + str(num()) + "\n\n"

download()

para.pushstr = para.pushstr + "当前bingHD文件数：" + str(num()) + "\n\n"

pushurl = "https://push.dayepao.com/?pushkey=" + "Your_Push_Key"
pushdata = {
    "touser": "@all",
    "msgtype": "text",
    "agentid": 1000002,
    "text": {
        "content": para.pushstr
    },
    "safe": 0,
    "enable_id_trans": 0,
    "enable_duplicate_check": 0,
    "duplicate_check_interval": 0
}
requests.post(pushurl, json=pushdata)
