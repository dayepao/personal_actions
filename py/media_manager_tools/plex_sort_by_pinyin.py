import sys
import time

import httpx
import pypinyin
import xmltodict

"""
pip install httpx
pip install pypinyin
pip install xmltodict
"""

PLEX_TOKEN = ""
PLEX_URL = "http://192.168.1.4:32400"


def get_method(url: str, headers: dict = None, timeout=5, max_retries=5, c: httpx.Client = None):
    """
    timeout: 超时时间,单位秒(s), 默认为 5 秒, 为 `None` 时禁用
    max_retries: 最大尝试次数, 默认为 5 次, 为 0 时禁用
    """
    k = 1
    while (k <= max_retries) or (max_retries == 0):
        try:
            if c is not None:
                res = c.get(url, headers=headers, timeout=timeout)
            else:
                res = httpx.get(url, headers=headers, timeout=timeout)
        except Exception as e:
            k = k + 1
            print(sys._getframe().f_code.co_name + ": " + str(e))
            time.sleep(1)
            continue
        else:
            break
    try:
        return res
    except Exception:
        sys.exit(sys._getframe().f_code.co_name + ": " + "Max retries exceeded")


def put_method(url: str, putdata=None, putparams=None, headers: dict = None, timeout=5, max_retries=5, c: httpx.Client = None):
    """
    timeout: 超时时间, 单位秒(s), 默认为 5 秒, 为 `None` 时禁用
    max_retries: 最大尝试次数, 默认为 5 次, 为 0 时禁用
    """
    k = 1
    while (k <= max_retries) or (max_retries == 0):
        try:
            if c is not None:
                res = c.put(url, data=putdata, params=putparams, headers=headers, timeout=timeout)
            else:
                res = httpx.put(url, data=putdata, params=putparams, headers=headers, timeout=timeout)
        except Exception as e:
            k = k + 1
            print(sys._getframe().f_code.co_name + ": " + str(e))
            time.sleep(1)
            continue
        else:
            break
    try:
        return res
    except Exception:
        sys.exit(sys._getframe().f_code.co_name + ": " + "Max retries exceeded")


def keep_chinese_characters(string):
    return "".join([c for c in string if "\u4e00" <= c <= "\u9fff"])


def get_pinyin(string):
    return "".join(["".join(i) for i in pypinyin.pinyin(keep_chinese_characters(string), style=pypinyin.FIRST_LETTER)])


# 判断字符串第一个字符是否为字母或数字
def start_with_letter_or_number(string):
    return (string[0] >= "\u0041" and string[0] <= "\u005a") or (string[0] >= "\u0061" and string[0] <= "\u007a") or (string[0] >= "\u0030" and string[0] <= "\u0039")


def get_libraries():
    url = "{plex_url}/library/sections".format(plex_url=PLEX_URL)
    headers = {"X-Plex-Token": PLEX_TOKEN}
    res = get_method(url, headers=headers)
    res_dict = xmltodict.parse(res.text)
    libraries = {}
    if type(res_dict["MediaContainer"]["Directory"]) == list:
        for directory in res_dict["MediaContainer"]["Directory"]:
            libraries[directory["@title"]] = directory["@key"]
    else:
        libraries[res_dict["MediaContainer"]["Directory"]["@title"]] = res_dict["MediaContainer"]["Directory"]["@key"]
    return libraries


def get_video_metadata(library_key: str):
    url = "{plex_url}/library/sections/{library_key}/all".format(plex_url=PLEX_URL, library_key=library_key)
    headers = {"X-Plex-Token": PLEX_TOKEN}
    res = get_method(url, headers=headers)
    res_dict = xmltodict.parse(res.text)
    video_list = []
    if "Video" in res_dict["MediaContainer"].keys():
        video_list = res_dict["MediaContainer"]["Video"]
    if "Directory" in res_dict["MediaContainer"].keys():
        video_list = res_dict["MediaContainer"]["Directory"]
    if video_list == []:
        error_msg_list.append("Can't find any video in library: {}".format(res_dict["MediaContainer"]["@title1"]))
    video_metadata = {}
    for video in video_list:
        video_metadata[video["@title"]] = {}
        video_metadata[video["@title"]]["type"] = video["@type"]
        video_metadata[video["@title"]]["ratingKey"] = video["@ratingKey"]
        # video_metadata[video["@title"]]["key"] = video["@key"]
        try:
            video_metadata[video["@title"]]["titleSort"] = video["@titleSort"]
        except KeyError:
            video_metadata[video["@title"]]["titleSort"] = ""
    return video_metadata


def update_video_titleSort(lib_name, video_metadata: dict):
    result = {}
    for title, metadata in video_metadata.items():
        print("正在处理: {lib_name}/{title}".format(lib_name=lib_name, title=title))
        if (titleSort := get_pinyin(title)) != "" and (not start_with_letter_or_number(title)):
            if (metadata["titleSort"] == "") or (titleSort != metadata["titleSort"]):
                url = "{plex_url}/library/metadata/{ratingKey}".format(plex_url=PLEX_URL, ratingKey=metadata["ratingKey"])
                headers = {"X-Plex-Token": PLEX_TOKEN}
                putdata = {"titleSort.value": titleSort, "titleSort.locked": "1"}
                res = put_method(url, putparams=putdata, headers=headers)
                # print(res.status_code, res.text)
                result[title] = (res.status_code, res.text)
    return result


def clear_video_titleSort(lib_name, video_metadata: dict):
    result = {}
    for title, metadata in video_metadata.items():
        print("正在处理: {lib_name}/{title}".format(lib_name=lib_name, title=title))
        if metadata["titleSort"] != "":
            url = "{plex_url}/library/metadata/{ratingKey}".format(plex_url=PLEX_URL, ratingKey=metadata["ratingKey"])
            headers = {"X-Plex-Token": PLEX_TOKEN}
            putdata = {"titleSort.value": "", "titleSort.locked": "0"}
            res = put_method(url, putparams=putdata, headers=headers)
            # print(res.status_code, res.text)
            result[title] = (res.status_code, res.text)
    return result


error_msg_list = []
libraries = get_libraries()
for lib_name, key in libraries.items():
    print("正在处理: {}".format(lib_name))
    video_metadata = get_video_metadata(key)
    update_video_titleSort(lib_name, video_metadata)
    # clear_video_titleSort(lib_name, video_metadata)
for error_msg in error_msg_list:
    print(error_msg)
