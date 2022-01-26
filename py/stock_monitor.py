import datetime
import json
import os

from utils_dayepao import dayepao_push, get_method

# 6开头：上证，1
# 0或3开头：深证，0
# 4或8开头：北证，0

PUSH_KEY = os.environ.get("PUSH_KEY") or ""


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

    res.update(json.loads(get_method(url).text)["data"] or {})

    info["name"] = str(res["f58"])
    info["code"] = str(res["f57"])
    info["price"] = str(res["f43"])
    info["yesterday_price"] = str(res["f60"])
    info["change"] = str(res["f169"])
    info["changePercent"] = str(res["f170"]) + "%"
    return info


def daily_push(code_list: list[str]):
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    pushstr = now + "\n"

    count = 1
    for code in code_list:
        info = get_info(code)
        pushstr = pushstr + \
            "\n第{}支股票:\n".format(str(count)) + \
            "名称: {}\n".format(str(info["name"])) + \
            "代码: {}\n".format(str(info["code"])) + \
            "当前价格: {}\n".format(str(info["price"])) + \
            "昨日收盘价格: {}\n".format(str(info["yesterday_price"])) + \
            "较昨收变化: {}\n".format(str(info["change"])) + \
            "较昨收变化百分比: {}\n".format(str(info["changePercent"]))
        count += 1

    print(pushstr)
    print(dayepao_push(pushstr, PUSH_KEY))


code_list = ["600157", "300157"]
daily_push(code_list)
