import sys
import time
from pathlib import Path

import httpx
import pypinyin

"""
pip install httpx
pip install pypinyin
"""


class jellyfin:
    def __init__(self, jellyfin_url: str, api_key: str):
        self.jellyfin_url = jellyfin_url
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
        url = f"{self.jellyfin_url}/System/Info?api_key={self.api_key}"
        res = get_method(url)
        return res.json()

    def get_admin_user(self):
        """获取管理员用户"""
        url = f"{self.jellyfin_url}/Users?api_key={self.api_key}"
        res = get_method(url)
        users = res.json()
        for user in users:
            if user.get("Policy", {}).get("IsAdministrator", False):
                if (server_id := self.server_info.get("Id")) and (user.get("ServerId") == server_id):
                    return user
        return None

    def get_libraries(self, libraryName=None):
        """获取指定媒体库"""
        if isinstance(libraryName, str):
            libraryName = [
                libraryName,
            ]
        if not (userId := self.admin_user.get("Id")):
            return None
        libraries = []
        url = f"{self.jellyfin_url}/Users/{userId}/Views?api_key={self.api_key}"
        res = get_method(url)
        for library in res.json().get("Items", []):
            # 跳过非目录
            # if library.get("IsFolder") and (library.get("CollectionType") in ["movies", "tvshows"]):
            if library.get("IsFolder") and (not libraryName or (library.get("Name") in libraryName)):
                libraries.append(library)
        # print(json.dumps(libraries, indent=4, ensure_ascii=False))
        return libraries

    def get_item_count(self):
        """获取项目数量"""
        url = f"{self.jellyfin_url}/Items/Counts?api_key={self.api_key}"
        res = get_method(url)
        # print(json.dumps(res.json(), indent=4, ensure_ascii=False))
        return res.json()

    def get_subItems(self, libraryId: str):
        """获取指定目录下的所有子项"""
        url = f"{self.jellyfin_url}/Users/{self.admin_user.get('Id')}/Items?api_key={self.api_key}&ParentId={libraryId}"
        # print(url)
        res = get_method(url)
        return res.json()

    def get_item_info(self, itemId: str):
        """获取指定子项的信息"""
        url = f"{self.jellyfin_url}/Users/{self.admin_user.get('Id')}/Items/{itemId}?api_key={self.api_key}"
        # print(url)
        res = get_method(url)
        return res.json()

    def update_item_info(self, itemId: str, newjson: dict):
        """更新指定子项的信息"""
        url = f"{self.jellyfin_url}/Items/{itemId}?api_key={self.api_key}"
        postjson = self.get_item_info(itemId)
        postjson.update(newjson)
        res = post_method(url, postjson=postjson)
        return res.status_code


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


def post_method(url: str, postdata=None, postjson=None, headers: dict = None, timeout=5, verify: bool = True, max_retries=5, c: httpx.Client = None):
    """
    timeout: 超时时间, 单位秒(s), 默认为 5 秒, 为 `None` 时禁用
    max_retries: 最大尝试次数, 默认为 5 次, 为 0 时禁用
    """
    k = 1
    while (k <= max_retries) or (max_retries == 0):
        try:
            if c is not None:
                res = c.post(url, data=postdata, json=postjson, headers=headers, timeout=timeout, verify=verify)
            else:
                res = httpx.post(url, data=postdata, json=postjson, headers=headers, timeout=timeout, verify=verify)
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


def preprocess_string(string):
    """仅保留中文、字母和数字"""
    return "".join([i for i in string if ("\u4e00" <= i <= "\u9fa5") or ("\u0041" <= i <= "\u005a") or ("\u0061" <= i <= "\u007a") or ("\u0030" <= i <= "\u0039")])


def get_pinyin(string):
    """获取字符串的拼音首字母"""
    return "".join(pypinyin.lazy_pinyin(preprocess_string(string), style=pypinyin.FIRST_LETTER))


def get_item_jellyfin_path(jellyfin_api: jellyfin, itemId: str):
    """获取指定子项在Jellyfin中的路径"""
    jellyfin_path = Path()
    while True:
        item = jellyfin_api.get_item_info(itemId)
        itemId = item.get("ParentId")
        if itemId:
            jellyfin_path = Path(item.get("Name")) / jellyfin_path
        else:
            break
    return str(jellyfin_path.as_posix())


def preprocess_folder(jellyfin_api: jellyfin, folder: dict):
    """预处理文件夹"""
    folders = []
    subItems = jellyfin_api.get_subItems(folder.get("Id"))  # 获取文件夹下的子项，并获取子项的数量
    count = subItems.get("TotalRecordCount", 0)
    for item in subItems.get("Items", []):
        if item.get("Type") == "Folder":
            item_info = jellyfin_api.get_item_info(item.get("Id"))
            # 递归处理文件夹
            temp_folders, temp_count = preprocess_folder(jellyfin_api, item_info)
            folders = [*temp_folders, item_info, *folders]
            count += temp_count
    return folders, count


def preprocess_libraries(jellyfin_api: jellyfin, libraryName=None):
    """预处理媒体库，将杂项中的文件夹视为媒体库"""
    print(f"{'='*80} 正在预处理媒体库 {'='*80}")
    total_count = 0
    temp_libraries = jellyfin_api.get_libraries(libraryName)
    libraries = []
    if not temp_libraries:
        sys.exit("Can't find any library")
    for library in temp_libraries:
        folders, count = preprocess_folder(jellyfin_api, library)
        libraries.extend(folders)
        total_count += count
    libraries.extend(temp_libraries)
    return libraries, total_count


def update_libraries_ForcedSortName(jellyfin_api: jellyfin, libraryName=None):
    """更新指定媒体库的排序名称"""
    libraries, total_count = preprocess_libraries(jellyfin_api, libraryName)
    processed_count = 0
    for library in libraries:
        jellyfin_path = get_item_jellyfin_path(jellyfin_api, library["Id"])
        print(f"{'='*80} 正在处理: {jellyfin_path} {'='*80}")
        subItems = jellyfin_api.get_subItems(library.get("Id")).get("Items", [])
        for item in subItems:
            item_info = jellyfin_api.get_item_info(item["Id"])
            processed_count += 1
            if (SortName := get_pinyin(item_info["Name"])) != item_info.get("ForcedSortName"):
                print(f"{processed_count}/{total_count}  正在处理:    {jellyfin_path}/{item_info['Name']}")
                jellyfin_api.update_item_info(item["Id"], {"ForcedSortName": SortName})
            else:
                print(f"{processed_count}/{total_count}  已处理，跳过:    {jellyfin_path}/{item_info['Name']}")


def clear_libraries_ForcedSortName(jellyfin_api: jellyfin, libraryName=None):
    """清除指定媒体库的排序名称"""
    libraries, total_count = preprocess_libraries(jellyfin_api, libraryName)
    processed_count = 0
    for library in libraries:
        jellyfin_path = get_item_jellyfin_path(jellyfin_api, library["Id"])
        print(f"{'='*80} 正在处理: {jellyfin_path} {'='*80}")
        subItems = jellyfin_api.get_subItems(library.get("Id")).get("Items", [])
        for item in subItems:
            item_info = jellyfin_api.get_item_info(item["Id"])
            processed_count += 1
            if item_info.get("ForcedSortName"):
                print(f"{processed_count}/{total_count}  正在处理:    {jellyfin_path}/{item_info['Name']}")
                jellyfin_api.update_item_info(item["Id"], {"ForcedSortName": ""})
            else:
                print(f"{processed_count}/{total_count}  已处理，跳过:    {jellyfin_path}/{item_info['Name']}")


if __name__ == "__main__":
    JELLYFIN_URL = "http://192.168.1.4:8096"
    JELLYFIN_API_KEY = ""

    jellyfin_api = jellyfin(JELLYFIN_URL, JELLYFIN_API_KEY)
    error_msg_list = []

    update_libraries_ForcedSortName(jellyfin_api)
    # clear_libraries_ForcedSortName(jellyfin_api)

    for error_msg in error_msg_list:
        print(error_msg)
