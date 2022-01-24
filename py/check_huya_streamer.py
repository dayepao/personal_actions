import datetime
import os
import time

from utils_dayepao import dayepao_push, get_tags_with_certain_attrs

PUSH_KEY = os.environ.get("PUSH_KEY")
STREAMERS = {"楚河": "998"}  # {"主播名称（随意）": "房间号"}


def generate_list(STREAMERS: dict) -> list[dict]:
    streamers_list = []
    for key, value in STREAMERS.items():
        streamers_list.append({"name": key, "id": value, "status": check_status(value)})
    return streamers_list


def check_status(streamer_id: str):
    status = "未在直播"
    url = "https://www.huya.com/" + streamer_id
    if not get_tags_with_certain_attrs(url=url, headers=headers, attrs={"class": "host-prevStartTime"}, max_retries=0)[0]:
        time.sleep(10)
        if not get_tags_with_certain_attrs(url=url, headers=headers, attrs={"class": "host-prevStartTime"}, max_retries=0)[0]:
            status = "正在直播"
    return status


def mainblock():
    print("正在初始化...")
    streamer_dict_list = generate_list(STREAMERS)
    print(streamer_dict_list)
    print("正在监控" + str(list(STREAMERS.keys())) + "是否开播")

    while True:
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        pushstr = ""
        for streamer_dict in streamer_dict_list:
            if (status := check_status(streamer_dict["id"])) == "正在直播":
                if streamer_dict["status"] == "未在直播":
                    pushstr += streamer_dict["name"] + " 正在直播\n"
                streamer_dict["status"] = status
            else:
                if streamer_dict["status"] == "正在直播":
                    pushstr += streamer_dict["name"] + " 下播了\n"
                streamer_dict["status"] = status

        if pushstr:
            pushstr = now + "\n\n" + pushstr
            print(pushstr)
            print(dayepao_push(pushstr, PUSH_KEY))

        streamers_status = {}
        for streamer_dict in streamer_dict_list:
            streamers_status[streamer_dict["name"]] = streamer_dict["status"]

        print(now + " " + str(streamers_status))
        time.sleep(30)


if __name__ == '__main__':
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68', 'X-Forwarded-For': '121.238.47.136'}
    while True:
        try:
            mainblock()
        except Exception:
            continue
