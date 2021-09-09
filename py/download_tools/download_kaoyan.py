import os
import random
import time

from bs4 import BeautifulSoup

from utils_dayepao import get_method, make_dir, get_self_dir


def download_kaoyan(url: str, download_dir: str):
    res = get_method(url)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    file_list = soup.find_all('a', attrs={"aria-label": "File"})
    for file in file_list:
        file_name = file['data-name']
        file_path = download_dir + "\\" + str(file_name)
        file_url = file['href'] + "&download=1"
        print("正在下载: " + file_path.replace(py_dir + "\\", ''))
        if not os.path.exists(file_path):
            make_dir(file_path[:file_path.rfind('\\')])
            file_content = get_method(file_url).content
            with open(file_path, 'wb') as f:
                f.write(file_content)
            time.sleep(random.randint(1, 5))
    folder_list = soup.find_all('a', attrs={"aria-label": "Folder"})
    for folder in folder_list:
        folder_name = folder['data-name']
        folder_url = folder['href']
        download_kaoyan(folder_url, download_dir + "\\" + folder_name)


py_dir = get_self_dir()[1]

kaoyan_url = "https://pan.uvooc.com/Learn/Kaoyan?hash=867M0pkv"
download_kaoyan(kaoyan_url, py_dir)
