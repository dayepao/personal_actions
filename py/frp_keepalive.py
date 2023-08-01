"""
cron: */2 * * * *
new Env('frp 保活');
"""

import os
import re
import sys

import httpx

# 从环境变量读取url列表
url_list = os.environ.get("FRP_URL_LIST")

if not url_list:
    print("未发现有效的 FRP_URL_LIST 环境变量,退出程序!")
    sys.exit()

url_list = re.split("[;,]", url_list)

for url in url_list:
    try:
        response = httpx.get(url)
        print(f"Successfully connected to {url}.")
    except Exception as e:
        print(f"Error occurred while connecting to {url}: {e}")
