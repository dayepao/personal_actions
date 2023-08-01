"""
cron: */2 * * * *
new Env('frp 保活');
"""

import os

import httpx

# 从环境变量读取url列表
url_list = os.environ.get("FRP_URL_LIST").split(",")

for url in url_list:
    try:
        response = httpx.get(url)
        print(f"Successfully connected to {url}.")
    except Exception as e:
        print(f"Error occurred while connecting to {url}: {e}")
