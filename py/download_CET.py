import os
import random
import re
import sys
import time

import httpx
from bs4 import BeautifulSoup

CET4_url = "https://pan.uvooc.com/Learn/CET/CET4?hash=867M0pkv"
CET6_url = "https://pan.uvooc.com/Learn/CET/CET6?hash=867M0pkv"


def get_method(url, headers=None, timeout=5, max_retries=5):
    k = 1
    while k <= max_retries:
        try:
            res = httpx.get(url, headers=headers, timeout=timeout)
        except Exception as e:
            k = k + 1
            print(sys._getframe().f_code.co_name + ": " + str(e))
            time.sleep(1)
            continue
        else:
            break
    try:
        return res
    except Exception:
        sys.exit(sys._getframe().f_code.co_name + ": " + "Max retries exceeded")


def post_method(url, postdata=None, postjson=None, headers=None, timeout=5, max_retries=5):
    k = 1
    while k <= max_retries:
        try:
            res = httpx.post(url, data=postdata, json=postjson, headers=headers, timeout=timeout)
        except Exception as e:
            k = k + 1
            print(sys._getframe().f_code.co_name + ": " + str(e))
            time.sleep(1)
            continue
        else:
            break
    try:
        return res
    except Exception:
        sys.exit(sys._getframe().f_code.co_name + ": " + "Max retries exceeded")


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def download_CET(CET_url, py_dir: str):
    if re.search(re.compile('CET4'), CET_url):
        CETX = 'CET4'
    elif re.search(re.compile('CET6'), CET_url):
        CETX = 'CET6'
    else:
        CETX = 'unknown'
    res = get_method(CET_url)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    folder_list = soup.find_all('a', attrs={"aria-label": "Folder"})
    for folder in folder_list:
        folder_name = folder['data-name']
        folder_url = folder['href']
        if re.search(re.compile(r'.+?级真题'), folder_name):
            res = get_method(folder_url)
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            file_list = soup.find_all('a', attrs={"aria-label": "File"})
            for file in file_list:
                file_name = file['data-name']
                file_path = py_dir + "\\" + CETX + "\\" + str(folder_name) + '\\' + str(file['data-name'])
                file_url = file['href'] + "&download=1"
                print("正在下载: " + CETX + "\\" + folder_name + "\\" + file_name)
                make_dir(file_path[:file_path.rfind('\\')])
                if not os.path.exists(file_path):
                    file_content = get_method(file_url).content
                    with open(file_path, 'wb') as f:
                        f.write(file_content)
                    time.sleep(random.randint(1, 5))


py_path = __file__
py_dir = py_path[:py_path.rfind('\\')]
download_CET(CET_url=CET4_url, py_dir=py_dir)
download_CET(CET_url=CET6_url, py_dir=py_dir)
