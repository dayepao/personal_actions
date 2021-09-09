import imghdr
import os

import httpx
from bs4 import BeautifulSoup


def download():
    key = input("请输入起始数字:")
    key = int(key)
    key_stop = input("请输入结束数字:")
    key_stop = int(key_stop) + 1
    notice = ""

    while key < key_stop:
        url = "https://tbing.cn/detail/" + str(key)
        filename = "bing\\" + str(key) + ".jpg"
        print("正在下载" + filename)
        if not os.path.exists(filename):
            res = httpx.get(url)
            html = res.text
            if str(html) == "Error":
                key = key + 1
                continue
            soup = BeautifulSoup(html, 'html.parser')
            imgs = soup.find_all('img')
            src = imgs[0].get('src')
            headers = {'referer': 'https://tbing.cn/', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68'}
            imgr = httpx.get(src, headers=headers)
            with open(filename, 'wb') as f:
                f.write(imgr.content)
            if str(imghdr.what(filename)) == "None":
                os.remove(filename)
                notice = notice + "\n" + "已删除" + filename
        key = key + 1

    print(notice)


if os.path.exists('bing'):
    download()
else:
    os.mkdir('bing')
    download()
os.system("pause")
