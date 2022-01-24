import datetime
import os
import time

from apscheduler.events import (EVENT_JOB_ERROR, EVENT_JOB_MISSED,
                                JobExecutionEvent)
from apscheduler.schedulers.background import BackgroundScheduler

from utils_dayepao import dayepao_push, get_tags_with_certain_attrs

# pip install apscheduler

PUSH_KEY = os.environ.get("PUSH_KEY")
STREAMERS = {"楚河": "998"}  # {"主播名称（随意）": "房间号"}


def generate_list(STREAMERS: dict) -> list[dict]:
    streamers_list = []
    for key, value in STREAMERS.items():
        streamers_list.append({"name": key, "id": value, "status": get_status(value)})
    return streamers_list


def get_status(streamer_id: str):
    status = "未在直播"
    url = "https://www.huya.com/" + streamer_id
    if not get_tags_with_certain_attrs(url=url, headers=headers, attrs={"class": "host-prevStartTime"}, max_retries=0)[0]:
        time.sleep(10)
        if not get_tags_with_certain_attrs(url=url, headers=headers, attrs={"class": "host-prevStartTime"}, max_retries=0)[0]:
            status = "正在直播"
    return status


def check_job(streamer_dict_list):
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    pushstr = ""
    for streamer_dict in streamer_dict_list:
        if (status := get_status(streamer_dict["id"])) == "正在直播":
            if streamer_dict["status"] == "未在直播":
                pushstr += streamer_dict["name"] + " 正在直播\n"
            streamer_dict["status"] = status
        else:
            if streamer_dict["status"] == "正在直播":
                pushstr += streamer_dict["name"] + " 下播了\n"
            streamer_dict["status"] = status

    if pushstr:
        pushstr = now + "\n\n" + pushstr
        print(dayepao_push(pushstr, PUSH_KEY))

    streamers_status = {}
    for streamer_dict in streamer_dict_list:
        streamers_status[streamer_dict["name"]] = streamer_dict["status"]

    print(now + " " + str(streamers_status))


def apscheduler_event_handler(event: JobExecutionEvent):
    if event.exception:
        pushstr = "开播监控出现异常\nTraceback (most recent call last):\n{}\n{}".format(str(event.traceback), str(event.exception))
    else:
        pushstr = "开播监控出现异常\n任务被跳过\n原定执行时间: {}".format(str(event.scheduled_run_time))

    print(dayepao_push(pushstr, PUSH_KEY))


if __name__ == '__main__':
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68', 'X-Forwarded-For': '121.238.47.136'}
    print("正在初始化...")
    streamer_dict_list = generate_list(STREAMERS)
    print("正在监控" + str(list(STREAMERS.keys())) + "是否开播")

    sched = BackgroundScheduler()

    sched.add_job(check_job, "cron", args=[streamer_dict_list], second="*/30", timezone="Asia/Shanghai")
    sched.add_listener(apscheduler_event_handler, EVENT_JOB_ERROR | EVENT_JOB_MISSED)

    sched.start()

    while True:
        time.sleep(5)
