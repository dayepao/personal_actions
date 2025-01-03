import os
import sys
from pathlib import Path

import pypinyin

from utils_dayepao import http_request

"""
pip install httpx
pip install pypinyin
"""


class emby:
    def __init__(self, emby_url: str, api_key: str):
        self.emby_url = emby_url
        self.api_key = api_key
        self.server_info = self.get_server_info()
        self.admin_user = self.get_admin_user()
        self.item_count = self.get_item_count()
        # self.libraries = self.get_libraries(["电影", "剧集", "杂项"])
        self.check_init()

    def check_init(self):
        """检查API初始化是否成功"""
        if not self.server_info:
            sys.exit("Can't find server id")
        if not self.admin_user:
            sys.exit("Can't find admin user")
        if not self.item_count:
            sys.exit("Can't find item count")

    def get_server_info(self):
        """获取服务器信息"""
        url = f"{self.emby_url}/System/Info?api_key={self.api_key}"
        res = http_request("get", url)
        return res.json()

    def get_admin_user(self):
        """获取管理员用户"""
        url = f"{self.emby_url}/Users?api_key={self.api_key}"
        res = http_request("get", url)
        users = res.json()
        for user in users:
            if user.get("Policy", {}).get("IsAdministrator", False):
                if (server_id := self.server_info.get("Id")) and (user.get("ServerId") == server_id):
                    return user
        return None

    def get_libraries(self, libraryName=None):
        """获取指定媒体库"""
        if isinstance(libraryName, str):
            libraryName = [libraryName]
        if not (userId := self.admin_user.get("Id")):
            return None
        libraries = []
        url = f"{self.emby_url}/Users/{userId}/Views?api_key={self.api_key}"
        res = http_request("get", url)
        for library in res.json().get("Items", []):
            # 跳过非目录
            # if library.get("IsFolder") and (library.get("CollectionType") in ["movies", "tvshows"]):
            if library.get("IsFolder") and (not libraryName or (library.get("Name") in libraryName)):
                libraries.append(library)
        # print(json.dumps(libraries, indent=4, ensure_ascii=False))
        return libraries

    def get_item_count(self):
        """获取项目数量"""
        url = f"{self.emby_url}/Items/Counts?api_key={self.api_key}"
        res = http_request("get", url)
        # print(json.dumps(res.json(), indent=4, ensure_ascii=False))
        return res.json()

    def get_subItems(self, libraryId: str):
        """获取指定目录下的所有子项"""
        url = f"{self.emby_url}/Users/{self.admin_user.get('Id')}/Items?api_key={self.api_key}&ParentId={libraryId}"
        # print(url)
        res = http_request("get", url)
        return res.json()

    def get_item_info(self, itemId: str):
        """获取指定子项的信息"""
        url = f"{self.emby_url}/Users/{self.admin_user.get('Id')}/Items/{itemId}?api_key={self.api_key}"
        # print(url)
        res = http_request("get", url)
        return res.json()

    def update_item_info(self, itemId: str, newjson: dict):
        """更新指定子项的信息"""
        url = f"{self.emby_url}/Items/{itemId}?api_key={self.api_key}"
        postjson = self.get_item_info(itemId)
        postjson.update(newjson)
        res = http_request("post", url, json=postjson)
        return res.status_code


def preprocess_string(string):
    """仅保留中文、字母和数字"""
    return "".join([i for i in string if ("\u4e00" <= i <= "\u9fa5") or ("\u0041" <= i <= "\u005a") or ("\u0061" <= i <= "\u007a") or ("\u0030" <= i <= "\u0039")])


def get_pinyin(string):
    """获取字符串的拼音首字母"""
    return "".join(pypinyin.lazy_pinyin(preprocess_string(string), style=pypinyin.FIRST_LETTER))


def get_item_emby_path(emby_api: emby, itemId: str):
    """获取指定子项在emby中的路径"""
    emby_path = Path()
    while True:
        item = emby_api.get_item_info(itemId)
        itemId = item.get("ParentId")
        if itemId:
            emby_path = Path(item.get("Name")) / emby_path
        else:
            break
    return str(emby_path.as_posix())


def preprocess_folder(emby_api: emby, folder: dict):
    """预处理文件夹"""
    folders = []
    subItems = emby_api.get_subItems(folder.get("Id"))  # 获取文件夹下的子项，并获取子项的数量
    count = subItems.get("TotalRecordCount", 0)
    for item in subItems.get("Items", []):
        if item.get("Type") == "Folder":
            item_info = emby_api.get_item_info(item.get("Id"))
            # 递归处理文件夹
            temp_folders, temp_count = preprocess_folder(emby_api, item_info)
            folders = [*temp_folders, item_info, *folders]
            count += temp_count
    return folders, count


def preprocess_libraries(emby_api: emby, libraryName=None):
    """预处理媒体库，将文件夹视为媒体库"""
    print("正在预处理媒体库")
    total_count = 0
    temp_libraries = emby_api.get_libraries(libraryName)
    libraries = []
    if not temp_libraries:
        sys.exit("Can't find any library")
    for library in temp_libraries:
        folders, count = preprocess_folder(emby_api, library)
        libraries.extend(folders)
        total_count += count
    libraries.extend(temp_libraries)
    return libraries, total_count


def update_libraries_ForcedSortName(emby_api: emby, libraryName=None):
    """更新指定媒体库的排序名称"""
    libraries, total_count = preprocess_libraries(emby_api, libraryName)
    processed_count = 0
    for library in libraries:
        emby_path = get_item_emby_path(emby_api, library["Id"])
        subItems = emby_api.get_subItems(library.get("Id")).get("Items", [])
        for item in subItems:
            item_info = emby_api.get_item_info(item["Id"])
            LockedFields = item_info.get("LockedFields", [])
            if "SortName" not in LockedFields:
                LockedFields.append("SortName")
            processed_count += 1
            if (SortName := get_pinyin(item_info["Name"])) != item_info.get("ForcedSortName"):
                print(f"{processed_count}/{total_count}  正在处理:    {emby_path}/{item_info['Name']}")
                emby_api.update_item_info(
                    item["Id"],
                    {
                        "LockedFields": LockedFields,
                        "ForcedSortName": SortName
                    }
                )
            else:
                print(f"{processed_count}/{total_count}  已处理，跳过:    {emby_path}/{item_info['Name']}")


def clear_libraries_ForcedSortName(emby_api: emby, libraryName=None):
    """清除指定媒体库的排序名称"""
    libraries, total_count = preprocess_libraries(emby_api, libraryName)
    processed_count = 0
    for library in libraries:
        emby_path = get_item_emby_path(emby_api, library["Id"])
        subItems = emby_api.get_subItems(library.get("Id")).get("Items", [])
        for item in subItems:
            item_info = emby_api.get_item_info(item["Id"])
            LockedFields = item_info.get("LockedFields", [])
            if "SortName" in LockedFields:
                LockedFields.remove("SortName")
            processed_count += 1
            if item_info.get("ForcedSortName") != item_info.get("Name"):
                print(f"{processed_count}/{total_count}  正在处理:    {emby_path}/{item_info['Name']}")
                emby_api.update_item_info(
                    item["Id"],
                    {
                        "LockedFields": LockedFields,
                        "ForcedSortName": ""
                    }
                )
            else:
                print(f"{processed_count}/{total_count}  已处理，跳过:    {emby_path}/{item_info['Name']}")


if __name__ == "__main__":
    EMBY_URL = os.environ.get("EMBY_URL")
    EMBY_API_KEY = os.environ.get("EMBY_API_KEY")

    emby_api = emby(EMBY_URL, EMBY_API_KEY)
    error_msg_list = []

    update_libraries_ForcedSortName(emby_api)
    # clear_libraries_ForcedSortName(emby_api)

    for error_msg in error_msg_list:
        print(error_msg)
