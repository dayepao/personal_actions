import datetime
import os

from bs4 import BeautifulSoup

from notify_dayepao import send_message
from utils_dayepao import http_request

GH_ACTOR = os.environ.get('GH_ACTOR')
REPOS = ["CF-Workers-docker.io", "CF-Workers-SUB"]  # 仓库名称


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
        send_message("GitHub 仓库更新提醒", pushstr)
    else:
        print(now + "\n\n" + "所有仓库都是最新的")
