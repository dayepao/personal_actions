"""
cron: */2 * * * *
new Env('frp 保活');
"""

import os
import re
import sys

import httpx

# 从环境变量读取url列表
frp_urls = os.environ.get("FRP_URLS")

if not frp_urls:
    print("未发现有效的 FRP_URL_LIST 环境变量,退出程序!")
    sys.exit()

frp_urls = re.split("[;,]", frp_urls)

for frp_url in frp_urls:
    try:
        response = httpx.get(frp_url)
        print(f"成功访问 {frp_url}.")
    except Exception as e:
        print(f"访问 {frp_url} 时遇到错误: {e}")
