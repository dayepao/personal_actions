import os
import random
import re
import time

from bs4 import BeautifulSoup

from utils_dayepao import get_method, get_self_dir, make_dir

CET4_url = "https://pan.uvooc.com/Learn/CET/CET4?hash=867M0pkv"
CET6_url = "https://pan.uvooc.com/Learn/CET/CET6?hash=867M0pkv"


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
                file_path = py_dir + "\\" + CETX + "\\" + str(folder_name) + '\\' + str(file_name)
                file_url = file['href'] + "&download=1"
                print("正在下载: " + CETX + "\\" + folder_name + "\\" + file_name)
                make_dir(file_path[:file_path.rfind('\\')])
                if not os.path.exists(file_path):
                    file_content = get_method(file_url).content
                    with open(file_path, 'wb') as f:
                        f.write(file_content)
                    time.sleep(random.randint(1, 5))


py_dir = get_self_dir()[1]
download_CET(CET_url=CET4_url, py_dir=py_dir)
download_CET(CET_url=CET6_url, py_dir=py_dir)
