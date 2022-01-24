import json

from utils_dayepao import get_method

# 6开头：上证，1
# 0或3开头：深证，0
# 4或8开头：北证，0


def get_info(code: str):
    info = {}
    if code[0] == "6":
        key = "1"
    else:
        key = "0"
    url = "http://push2.eastmoney.com/api/qt/stock/get?secid={}.{}&fltt=2&fields=f43,f57,f58,f169,f170".format(key, code)
    res = json.loads(get_method(url).text)["data"]
    info["name"] = str(res["f58"])
    info["code"] = str(res["f57"])
    info["price"] = str(res["f43"])
    info["change"] = str(res["f169"])
    info["changePercent"] = str(res["f170"]) + "%"
    return info


stock_info = get_info("600157")
print(stock_info)
