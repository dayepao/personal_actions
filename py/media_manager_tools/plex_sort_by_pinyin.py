"""
cron: 0 */1 * * *
new Env('Plex 媒体库拼音排序');
"""

import os
import sys

import pypinyin
import xmltodict
from utils_dayepao import http_request

"""
pip install pypinyin
pip install xmltodict
"""


class Plex:
    def __init__(self, plex_url: str, plex_token: str):
        if not plex_url.startswith("http"):
            plex_url = f"http://{plex_url}"
        if plex_url.endswith("/"):
            plex_url = plex_url[:-1]
        self.plex_url = plex_url
        self.plex_token = plex_token
        self.libraries = self.get_libraries()
        self.media_count = self.get_media_count()
        self.check_init()

    def check_init(self):
        """检查API初始化是否成功"""
        if not self.libraries:
            sys.exit("Can't find any library")

    def get_libraries(self):
        url = f"{self.plex_url}/library/sections?X-Plex-Token={self.plex_token}"
        res = http_request("get", url)
        res_dict = xmltodict.parse(res.text)
        libraries = []
        if isinstance(res_dict["MediaContainer"]["Directory"], list):
            for directory in res_dict["MediaContainer"]["Directory"]:
                libraries.append({"name": directory["@title"], "id": directory["@key"]})
        if isinstance(res_dict["MediaContainer"]["Directory"], dict):
            libraries.append({"name": res_dict["MediaContainer"]["Directory"]["@title"], "id": res_dict["MediaContainer"]["Directory"]["@key"]})
        for library in libraries:
            library["medias"] = self.get_library_medias(library["id"])
        return libraries

    def get_library_medias(self, library_id):
        url = f"{self.plex_url}/library/sections/{library_id}/all?X-Plex-Token={self.plex_token}"
        res = http_request("get", url)
        res_dict = xmltodict.parse(res.text)
        medias_list = []
        if "Video" in res_dict["MediaContainer"].keys():
            medias_list = res_dict["MediaContainer"]["Video"]
        if "Directory" in res_dict["MediaContainer"].keys():
            medias_list = res_dict["MediaContainer"]["Directory"]
        if medias_list == []:
            sys.exit(f"Can't find any video in library: {res_dict['MediaContainer']['@title1']}")
        library_medias = []
        for media in medias_list:
            media_dict = {}
            media_dict["name"] = media.get("@title")
            media_dict["type"] = media.get("@type")
            media_dict["ratingKey"] = media.get("@ratingKey")
            # media_dict["key"] = media.get("@key")
            media_dict["titleSort"] = media.get("@titleSort")
            library_medias.append(media_dict)
        return library_medias

    def get_media_count(self, libraryName: str | list = None):
        """获取媒体库中的视频数量"""
        if isinstance(libraryName, str):
            libraryName = [libraryName]
        count = 0
        for library in self.libraries:
            if libraryName and library["name"] not in libraryName:
                continue
            count += len(library["medias"])
        return count

    def update_media_details(self, ratingKey, update_data: dict):
        url = f"{self.plex_url}/library/metadata/{ratingKey}?X-Plex-Token={self.plex_token}"
        res = http_request("put", url, params=update_data)
        return res.status_code

    def get_media_locked_items(self, ratingKey):
        url = f"{self.plex_url}/library/metadata/{ratingKey}?X-Plex-Token={self.plex_token}"
        res = http_request("get", url)
        res_dict = xmltodict.parse(res.text)
        locked_items = []
        if "Video" in res_dict["MediaContainer"].keys():
            if "Field" in res_dict["MediaContainer"]["Video"].keys():
                fields = res_dict["MediaContainer"]["Video"]["Field"]
                if not isinstance(fields, list):
                    fields = [fields]
                for field in fields:
                    if field.get("@locked") == "1":
                        locked_items.append(field.get("@name"))
        if "Directory" in res_dict["MediaContainer"].keys():
            if "Field" in res_dict["MediaContainer"]["Directory"].keys():
                fields = res_dict["MediaContainer"]["Directory"]["Field"]
                if not isinstance(fields, list):
                    fields = [fields]
                for field in fields:
                    if field.get("@locked") == "1":
                        locked_items.append(field.get("@name"))
        return locked_items


def preprocess_string(string):
    """仅保留中文、字母和数字"""
    return "".join([i for i in string if ("\u4e00" <= i <= "\u9fa5") or ("\u0041" <= i <= "\u005a") or ("\u0061" <= i <= "\u007a") or ("\u0030" <= i <= "\u0039")])


def get_pinyin(string):
    """获取字符串的拼音首字母"""
    return "".join(pypinyin.lazy_pinyin(preprocess_string(string), style=pypinyin.FIRST_LETTER))


def update_libraries_titleSort(plex_api: Plex, libraryName: str | list = None):
    """更新指定媒体库的排序名称"""
    if isinstance(libraryName, str):
        libraryName = [libraryName]
    processed_count = 0
    total_count = plex_api.get_media_count(libraryName)
    for library in plex_api.get_libraries():
        if libraryName and library["name"] not in libraryName:
            continue
        for media in library["medias"]:
            processed_count += 1
            titleSort = get_pinyin(media["name"])
            if titleSort and (titleSort != media.get("titleSort")) and (titleSort != media.get("name")):
                if "titleSort" in plex_api.get_media_locked_items(media["ratingKey"]):
                    print(f"{processed_count}/{total_count}  已锁定，跳过:    {library['name']}/{media['name']}")
                    continue
                print(f"{processed_count}/{total_count}  正在处理:    {library['name']}/{media['name']}")
                plex_api.update_media_details(media["ratingKey"], {"titleSort.value": titleSort, "titleSort.locked": "1"})
            else:
                print(f"{processed_count}/{total_count}  已处理，跳过:    {library['name']}/{media['name']}")


def clear_libraries_titleSort(plex_api: Plex, libraryName: str | list = None):
    """清除指定媒体库的排序名称"""
    if isinstance(libraryName, str):
        libraryName = [libraryName]
    processed_count = 0
    total_count = plex_api.get_media_count(libraryName)
    for library in plex_api.get_libraries():
        if libraryName and library["name"] not in libraryName:
            continue
        for media in library["medias"]:
            processed_count += 1
            if media.get("titleSort"):
                print(f"{processed_count}/{total_count}  正在处理:    {library['name']}/{media['name']}")
                plex_api.update_media_details(media["ratingKey"], {"titleSort.value": "", "titleSort.locked": "0"})
            else:
                print(f"{processed_count}/{total_count}  已处理，跳过:    {library['name']}/{media['name']}")


def get_medias_with_locked_items(plex_api: Plex, libraryName: str | list = None):
    """获取包含锁定字段的媒体"""
    if isinstance(libraryName, str):
        libraryName = [libraryName]
    processed_count = 0
    total_count = plex_api.get_media_count(libraryName)
    for library in plex_api.get_libraries():
        if libraryName and library["name"] not in libraryName:
            continue
        for media in library["medias"]:
            processed_count += 1
            if locked_items := plex_api.get_media_locked_items(media["ratingKey"]):
                print(f"{processed_count}/{total_count}  {library['name']}/{media['name']} 包含锁定字段: {locked_items}\033[K")
            else:
                print(f"{processed_count}/{total_count}  {library['name']}/{media['name']} 不包含锁定字段\033[K", end="\r")


if __name__ == "__main__":
    PLEX_URL = os.environ.get("PLEX_URL")
    PLEX_TOKEN = os.environ.get("PLEX_TOKEN")

    plex_api = Plex(PLEX_URL, PLEX_TOKEN)

    update_libraries_titleSort(plex_api)
    # clear_libraries_titleSort(plex_api)
