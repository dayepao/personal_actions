import datetime
import os
import time

from utils_dayepao import (creat_apscheduler, dayepao_push,
                           get_tags_with_certain_attrs)

PUSH_KEY = os.environ.get("PUSH_KEY")
STREAMERS = {"楚河": "998"}  # {"主播名称（随意）": "房间号"}
MAX_PUSH_COUNT = 5  # 每个主播每天最多推送次数，0点清零


def generate_list(STREAMERS: dict) -> list[dict]:
    streamers_list = []
    for key, value in STREAMERS.items():
        streamers_list.append({"name": key, "id": value, "status": get_status(value), "counter": 0})
    return streamers_list


def get_status(streamer_id: str):
    status = "未在直播"
    url = "https://www.huya.com/" + streamer_id
    if not get_tags_with_certain_attrs(url=url, headers=headers, attrs={"class": "host-prevStartTime"}, max_retries=0)[0]:
        status = "正在直播"
    return status


def check_job(streamer_dict_list: list[dict]):
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    pushstr = ""
    for streamer_dict in streamer_dict_list:
        if (status := get_status(streamer_dict["id"])) == "正在直播":
            if streamer_dict["status"] == "未在直播":
                if streamer_dict["counter"] < MAX_PUSH_COUNT:
                    pushstr += streamer_dict["name"] + " 正在直播\n"
                    streamer_dict["counter"] += 1  # 每推送一次开播，计数器加1
                    if streamer_dict["counter"] == MAX_PUSH_COUNT:
                        pushstr += streamer_dict["name"] + " 已达到今日开播推送次数上限({MAX_PUSH_COUNT}次)\n".format(MAX_PUSH_COUNT=MAX_PUSH_COUNT)
            streamer_dict["status"] = status
        else:
            if streamer_dict["status"] == "正在直播":
                if streamer_dict["counter"] <= MAX_PUSH_COUNT:
                    pushstr += streamer_dict["name"] + " 下播了\n"
                    if streamer_dict["counter"] == MAX_PUSH_COUNT:
                        streamer_dict["counter"] += 1  # 计数器加1，避免重复推送下播通知
            streamer_dict["status"] = status

    if pushstr:
        pushstr = now + "\n\n" + pushstr
        print(dayepao_push(pushstr, PUSH_KEY))

    streamers_status = {}
    for streamer_dict in streamer_dict_list:
        streamers_status[streamer_dict["name"]] = streamer_dict["status"]

    print("{now} {streamers_status}".format(now=now, streamers_status=streamers_status))


def reset_counter(streamer_dict_list: list[dict]):
    for streamer_dict in streamer_dict_list:
        streamer_dict["counter"] = 0


if __name__ == '__main__':
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.69', 'X-Forwarded-For': '121.238.47.136'}
    print("正在初始化...")
    streamer_dict_list = generate_list(STREAMERS)
    print(streamer_dict_list)
    print("正在监控" + str(list(STREAMERS.keys())) + "是否开播")

    sched_job_list = [
        {
            "name": "开播监控",
            "func": check_job,
            "args": [streamer_dict_list],
            "trigger": "cron",
            "minute": "*/5",
            "next_run_time": datetime.datetime.now() + datetime.timedelta(seconds=10),
            "max_instances": 1,
        },
        {
            "name": "重置计数器",
            "func": reset_counter,
            "args": [streamer_dict_list],
            "trigger": "cron",
            "hour": "0",
            "max_instances": 1,
        },
    ]

    push_option = {
        "pushkey": PUSH_KEY,
    }

    sched = creat_apscheduler(sched_job_list, push_option)
    sched.start()

    while True:
        time.sleep(5)
