import datetime
import json
import os
import sys
import time

from utils_dayepao import creat_apscheduler, dayepao_push, get_method

# 6开头：上证，1
# 0或3开头：深证，0
# 4或8开头：北证，0

PUSH_KEY = os.environ.get("PUSH_KEY")
CODE_LIST = ["600157"]
CODE_CERTAINPRICE_DICT = {
    "600157": "1.80",
}


def get_info(code: str):
    res = {
        "f43": "-",
        "f57": "-",
        "f58": "-",
        "f60": "-",
        "f169": "-",
        "f170": "-",
    }
    info = {}

    if code[0] == "6":
        key = "1"
    else:
        key = "0"
    url = "http://push2.eastmoney.com/api/qt/stock/get?secid={}.{}&fltt=2&fields=f43,f57,f58,f60,f169,f170".format(key, code)

    try:
        res.update(json.loads(get_method(url).text)["data"] or {})
    except Exception as e:
        print(sys._getframe().f_code.co_name + ": " + str(e))

    info["name"] = str(res["f58"])
    info["code"] = str(res["f57"]) if str(res["f57"]) != "-" else code
    info["price"] = str(res["f43"])
    info["yesterday_price"] = str(res["f60"])
    info["change"] = str(res["f169"])
    info["changePercent"] = str(res["f170"]) + "%"
    return info


def daily_push(code_list: list[str]):
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    pushstr = ""

    count = 1
    for code in code_list:
        if count == 1:
            pushstr = now + "\n"
        info = get_info(code)
        pushstr += \
            "\n第{}支股票:\n".format(str(count)) + \
            "名称: {}\n".format(str(info["name"])) + \
            "代码: {}\n".format(str(info["code"])) + \
            "当前价格: {}\n".format(str(info["price"])) + \
            "昨日收盘价格: {}\n".format(str(info["yesterday_price"])) + \
            "较昨收变化: {}\n".format(str(info["change"])) + \
            "较昨收变化百分比: {}\n".format(str(info["changePercent"]))
        count += 1

    if pushstr:
        print(pushstr)
        print(dayepao_push(pushstr, PUSH_KEY))


def certain_price_push(code_certainPrice_dict: dict):
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    pushstr = ""

    count = 1
    for code, certainPrice in code_certainPrice_dict.items():
        info = get_info(code)
        try:
            if float(info["price"]) >= float(certainPrice):
                if count == 1:
                    pushstr = now + "\n\n有股票达到预定价格\n"
                pushstr += \
                    "\n第{}支股票:\n".format(str(count)) + \
                    "名称: {}\n".format(str(info["name"])) + \
                    "代码: {}\n".format(str(info["code"])) + \
                    "当前价格: {}\n".format(str(info["price"])) + \
                    "预定价格: {}\n".format(str(certainPrice))
                count += 1
        except Exception as e:
            print(sys._getframe().f_code.co_name + ": " + str(e))

    if pushstr:
        print(pushstr)
        print(dayepao_push(pushstr, PUSH_KEY))
    else:
        print(now + " 没有股票达到预定价格")


if __name__ == '__main__':
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.69', 'X-Forwarded-For': '121.238.47.136'}
    print("开始股价监控...")

    sched_job_list = [
        {
            "func": daily_push,
            "trigger": "cron",
            "args": [CODE_LIST],
            "kwargs": {},
            "name": "每日股价监控",
            "max_instances": 1,
            "hour": "10",
        },
        {
            "func": certain_price_push,
            "trigger": "cron",
            "args": [CODE_CERTAINPRICE_DICT],
            "kwargs": {},
            "name": "特定股价监控",
            "max_instances": 1,
            "hour": "9-11, 13-15",
            "minute": "*/10",
        },
    ]

    sched = creat_apscheduler(sched_job_list, PUSH_KEY)
    sched.start()

    while True:
        time.sleep(5)
