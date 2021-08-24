import datetime
import os
import sys
import time

import httpx
from bs4 import BeautifulSoup

# pip install -U requests[security]


GH_ACTOR = os.environ.get('GH_ACTOR')
PUSH_KEY = os.environ.get('PUSH_KEY')
REPOS = ["AutoApiS", "uptime-status", "onedrive-cf-index"]  # 仓库名称


def get_method(url, headers=None, timeout=5):
    k = 1
    while k < 6:
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


def post_method(url, postdata=None, postjson=None, headers=None, timeout=5):
    k = 1
    while k < 6:
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


if __name__ == '__main__':
    pushstr = ""
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    for repo in REPOS:
        url = "https://github.com/" + GH_ACTOR + "/" + repo
        res = get_method(url)
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all(class_='d-flex flex-auto')
        for item in items:
            if "behind" in str(item):
                pushstr = pushstr + repo + "有更新" + "\n\n"
    if pushstr:
        pushstr = now + "\n\n" + pushstr
        print(pushstr)
        if PUSH_KEY is not None:
            pushurl = "https://push.dayepao.com/?pushkey=" + PUSH_KEY
            pushdata = {
                "touser": "@all",
                "msgtype": "text",
                "agentid": 1000002,
                "text": {
                    "content": pushstr
                },
                "safe": 0,
                "enable_id_trans": 0,
                "enable_duplicate_check": 0,
                "duplicate_check_interval": 0
            }
            post_method(pushurl, postjson=pushdata, timeout=10)
    else:
        print(now + "\n\n" + "所有仓库都是最新的")
