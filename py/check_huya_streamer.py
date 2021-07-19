import datetime
import sys
import time

import requests
from bs4 import BeautifulSoup


# pip install -U requests[security]
def check_status(streamer_id):
    url = "https://www.huya.com/" + streamer_id
    while True:
        try:
            res = requests.get(url, headers=headers, timeout=5)
        except Exception as e:
            print(sys._getframe().f_code.co_name + ": " + str(e))
            continue
        else:
            break
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all(class_='host-prevStartTime')
    if not items:
        status = '正在直播'
    else:
        status = "未在直播"
    return status


def mainblock():
    streamers_status = {}
    print("正在监控" + str(list(streamers.keys())) + "是否开播")

    for streamer_name, streamer_id in streamers.items():
        streamers_status[streamer_name] = check_status(streamer_id)

    while True:
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        pushstr = ""
        for streamer_name, streamer_id in streamers.items():
            status = check_status(streamer_id)
            if status == "正在直播":
                if streamers_status[streamer_name] == "未在直播":
                    pushstr += streamer_name + " 正在直播\n"
                streamers_status[streamer_name] = '正在直播'
            else:
                if streamers_status[streamer_name] == "正在直播":
                    pushstr += streamer_name + " 下播了\n"
                streamers_status[streamer_name] = "未在直播"

        if pushstr:
            pushstr = now + "\n\n" + pushstr
            print(pushstr)
            pushurl = "https://push.dayepao.com/?pushkey=" + "push_key"
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
            while True:
                try:
                    requests.post(pushurl, json=pushdata, timeout=5)
                except Exception as e:
                    print(sys._getframe().f_code.co_name + ": " + str(e))
                    continue
                else:
                    break
        print(now + " " + str(streamers_status))
        time.sleep(30)


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68', 'X-Forwarded-For': '121.238.47.136'}
streamers = {"楚河": "998"}  # "主播名称（随意）" : "房间号"
while True:
    try:
        mainblock()
    except Exception:
        continue
