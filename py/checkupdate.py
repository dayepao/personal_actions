import datetime
import os

from bs4 import BeautifulSoup

from utils_dayepao import http_request

GH_ACTOR = os.environ.get('GH_ACTOR')
PUSH_KEY = os.environ.get('PUSH_KEY')
REPOS = ["AutoApiS", "uptime-status"]  # 仓库名称


if __name__ == '__main__':
    pushstr = ""
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    for repo in REPOS:
        url = "https://github.com/" + GH_ACTOR + "/" + repo
        res = http_request("get", url)
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
            http_request("post", pushurl, postjson=pushdata, timeout=10)
    else:
        print(now + "\n\n" + "所有仓库都是最新的")
