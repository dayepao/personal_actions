"""
cron: */5 * * * *
new Env('虎牙开播监控');
"""
import json
import os
from datetime import datetime

from notify import send_message
from qinglong_api import qinglong
from utils_dayepao import get_tags_with_certain_attrs

PUSH_KEY = os.environ.get("PUSH_KEY")
MAX_PUSH_COUNT = 5  # 每个主播每天最多推送次数，0点清零

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def init_from_env():
    """
    - 确保符合要求的环境变量不经过修改直接返回

    - 确保不符合要求的环境变量经过修改后符合要求并返回
    """
    messages = []
    base_streamer = {"name": "", "id": "", "status": "", "counter": 0, "update_time": ""}
    streamers: list[dict] = json.loads(os.environ.get("HUYA_STREAMERS"))

    current_time = datetime.now()
    formatted_current_time = current_time.strftime(DATETIME_FORMAT)

    for index, streamer in enumerate(streamers):
        if not streamer.get("name") or not streamer.get("id"):
            error_message = f"第{index+1}个虎牙主播配置错误: 缺少 name 或 id"
            messages.append(error_message)
            raise ValueError(error_message)
        streamer = base_streamer | streamer

        last_update_time = current_time if not streamer.get("update_time") else datetime.strptime(streamer["update_time"], DATETIME_FORMAT)
        if last_update_time == current_time:
            messages.append(f"{streamer['name']} 缺少更新时间，更新状态并重置计数器")
            streamer["status"] = get_status(streamer["id"])
            streamer["counter"] = 0
            streamer["update_time"] = formatted_current_time
        if (current_time.date() - last_update_time.date()).days >= 1:
            streamer["counter"] = 0
        if (not streamer.get("status")) or ((current_time-last_update_time).total_seconds() >= 600):
            messages.append(f"{streamer['name']} 缺少状态或距离上次更新时间超过10分钟，将更新状态")
            streamer["status"] = get_status(streamer["id"])
            streamer["update_time"] = formatted_current_time
        streamers[index] = streamer

    if messages:
        messages.insert(0, formatted_current_time)
        send_message("初始化虎牙监控", "\n".join(messages))
    return streamers


def get_status(streamer_id: str):
    status = "未在直播"
    url = "https://www.huya.com/" + streamer_id
    if not get_tags_with_certain_attrs(url=url, headers=headers, attrs={"class": "host-prevStartTime"}, max_retries=0)[0]:
        status = "正在直播"
    return status


def check(streamers: list[dict]):
    current_time = datetime.now()
    formatted_current_time = current_time.strftime(DATETIME_FORMAT)
    messages = []
    for streamer in streamers:
        if (status := get_status(streamer["id"])) == "正在直播":
            if streamer["status"] == "未在直播":
                if streamer["counter"] < MAX_PUSH_COUNT:
                    messages.append(f"{streamer['name']} 正在直播")
                    streamer["counter"] += 1  # 每推送一次开播，计数器加1
                    if streamer["counter"] == MAX_PUSH_COUNT:
                        messages.append(f"{streamer['name']} 已达到今日开播推送次数上限({MAX_PUSH_COUNT}次)")
            streamer["status"] = status
            streamer["update_time"] = formatted_current_time
        else:
            if streamer["status"] == "正在直播":
                if streamer["counter"] <= MAX_PUSH_COUNT:
                    messages.append(f"{streamer['name']} 下播了\n")
                    if streamer["counter"] == MAX_PUSH_COUNT:
                        streamer["counter"] += 1  # 计数器加1，避免重复推送下播通知
            streamer["status"] = status
            streamer["update_time"] = formatted_current_time
    # 更新环境变量
    qinglong(os.getenv("QL_PANEL_URL"), os.getenv("QL_CLIENT_ID"), os.getenv("QL_CLIENT_SECRET")).update_env("HUYA_STREAMERS", json.dumps(streamers, ensure_ascii=False))

    if messages:
        messages.insert(0, formatted_current_time)
        send_message("虎牙监控", "\n".join(messages))

    send_message(formatted_current_time, json.dumps(streamers, indent=4, ensure_ascii=False), "console")


if __name__ == "__main__":
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203", "X-Forwarded-For": "121.238.47.136"}
    print("正在初始化...")
    HUYA_STREAMERS = init_from_env()
    # print(HUYA_STREAMERS)
    check(HUYA_STREAMERS)
