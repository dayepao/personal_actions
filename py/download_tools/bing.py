import imghdr
import os
import time
from pathlib import Path

from bs4 import BeautifulSoup

from utils_dayepao import download_file, get_method, get_self_dir


def download():
    key = input("请输入起始数字:")
    key = int(key)
    key_stop = input("请输入结束数字:")
    key_stop = int(key_stop) + 1
    notice = ""

    while key < key_stop:
        url = "https://tbing.cn/detail/" + str(key)
        filename = get_self_dir()[1] + "\\bing\\" + str(key) + ".jpg"
        print("正在下载: " + filename)
        if not Path(filename).exists():
            res = get_method(url)
            html = res.text
            if str(html) == "Error":
                key = key + 1
                continue
            soup = BeautifulSoup(html, 'html.parser')
            imgs = soup.find_all('img')
            src = imgs[0].get('src')
            headers = {'referer': 'https://tbing.cn/',
                       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68'}
            download_file(file_path=filename, file_url=src, headers=headers)
            if str(imghdr.what(filename)) == "None":
                os.remove(filename)
                notice = notice + "\n" + "已删除" + filename
        key = key + 1
        time.sleep(1)

    print(notice)


if __name__ == "__main__":
    download()
    os.system("pause")
