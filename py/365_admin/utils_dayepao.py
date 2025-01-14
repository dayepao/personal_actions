import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from queue import Queue
from threading import Thread

import __main__
import chardet
import httpx
from bs4 import BeautifulSoup

"""
pip install httpx
pip install beautifulsoup4
pip install chardet
"""


def http_request(method_name: str, url: str, timeout=5, max_retries=5, c: httpx.Client = None, **kwargs) -> httpx.Response:
    """
    发送 HTTP 请求

    method: 请求方法，如 'get', 'post', 'put', 'delete'等

    url: 请求的URL

    timeout: 超时时间, 单位秒(s), 默认为 5 秒, 为 `None` 时禁用

    max_retries: 最大尝试次数, 默认为 5 次, 为 0 时禁用

    c: httpx.Client 对象

    **kwargs: 其他传递给 httpx 请求方法的参数, 如 headers, data, json, verify 等
    """
    method_name = method_name.lower()  # 先转换为小写

    if not method_name:
        raise ValueError("请求方法不能为空")

    try:
        if c is not None:
            request_method = getattr(c, method_name)
        else:
            request_method = getattr(httpx, method_name)
    except AttributeError:
        raise ValueError(f"不支持的请求方法: '{method_name}'")

    attempt_count = 1
    while (attempt_count <= max_retries) or (max_retries == 0):
        try:
            res = request_method(url=url, timeout=timeout, **kwargs)
        except Exception as e:
            attempt_count = attempt_count + 1
            print(f"{sys._getframe().f_code.co_name} 出错: {str(e)}")
            time.sleep(1)
            continue
        else:
            break
    try:
        return res
    except Exception as e:
        raise RuntimeError(f"{sys._getframe().f_code.co_name} 出错: 已达到最大重试次数") from e


def get_self_dir():
    """获取自身路径

    返回`(self_path, self_dir, self_name)`

    self_path: 当前程序文件完整路径 (包括文件名)
    self_dir: 当前程序文件所在文件夹路径
    self_name: 当前程序文件名
    """
    self_path = Path(__main__.__file__).resolve() if Path(__file__).suffix == ".py" else Path(sys.executable).resolve()
    self_dir, self_name = self_path.parent, self_path.name
    return self_path, self_dir, self_name


def get_resource_path(relative_path):
    base_path = Path(__main__.__file__).resolve().parent
    return base_path.joinpath(relative_path)


def get_file_hash(file_path, name: str = "md5"):
    """获取文件哈希值

    name: 哈希算法, 可选: 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'blake2b', 'blake2s', 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512', 'shake_128', 'shake_256'
    """
    hashstr = hashlib.new(name)
    with open(file_path, "rb") as f:
        while (tempdata := f.read(40960)) != b"":
            hashstr.update(tempdata)
    return str(hashstr.hexdigest())


def download_file(file_path: str, file_url: str, headers: dict = None):
    """下载文件到指定路径"""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    file_content = http_request("get", file_url, headers=headers).content
    with open(file_path, "wb") as f:
        f.write(file_content)


def get_tags_with_certain_attrs(url: str, headers: dict = None, attrs: dict[str, str] = None, max_retries=5, c: httpx.Client = None):
    """获得网页指定属性的标签

    attrs: 标签属性
    max_retries: 最大尝试次数, 默认为 5 次, 为 0 时禁用

    返回`(tags, tags_content)`

    tags: 标签列表
    tags_content: 标签内容列表
    """
    res = http_request("get", url, headers=headers, max_retries=max_retries, c=c)
    soup = BeautifulSoup(res.text, "html.parser")
    temp_tags = list(soup.find_all(attrs=attrs))
    tags = []

    # 去重 && 当attrs为空时, 去除具有包含关系的结果
    i = 0
    for i in range(len(temp_tags)):
        k = 0
        for temp_tag in temp_tags:
            if (temp_tags[i] in temp_tag) and (temp_tags[i] != temp_tag):
                k = 1
        if (k == 0) and (temp_tags[i] not in tags):
            tags.append(temp_tags[i])
        i += 1

    tags_content = []
    for tag in tags:
        search_result = re.search(re.compile(r"^<.+?>(.+)<.+?>$"), str(tag).replace("\r", "").replace("\n", ""))
        if search_result:
            tags_content.append(str(search_result.group(1).strip()))
    return (tags, tags_content)


def search_in_website(url: str, content: str, headers: dict = None, attrs: dict[str, str] = None, c: httpx.Client = None):
    """搜索网页中是否有指定内容, 返回布尔值

    attrs: 标签属性
    """
    tags_content = get_tags_with_certain_attrs(url, headers=headers, attrs=attrs, c=c)[1]
    return bool(content in " / ".join(tags_content))


def get_content_in_website(url, r_e: str, headers: dict = None, attrs: dict[str, str] = None, c: httpx.Client = None):
    """搜索网页中匹配指定正则表达式的内容

    r_e: 正则表达式, 例如`r'^<.+?>(.+)<.+?>$'`
    attrs: 标签属性
    """
    tags_content = get_tags_with_certain_attrs(url, headers=headers, attrs=attrs, c=c)[1]
    search_result = re.findall(re.compile(r_e), " / ".join(tags_content))
    return search_result


def set_powershell_cmd(*args: str):
    if (powershell_cmd := ";".join(args)).strip() == "":
        raise ValueError("命令为空, 请检查传入参数")
    return powershell_cmd


def cmd_dayepao(cmd: str | list, encoding: str = None):
    """执行终端命令
    cmd: "命令" 或 ["powershell", "命令"]

    返回 (out_queue, err_queue)
    """

    class cmd_thread_work(Thread):
        def __init__(self, queue_list: list[Queue], cmd: str | list, encoding: str) -> None:
            super().__init__()
            self.out_queue, self.err_queue, self.returncode_queue = queue_list
            self.cmd = cmd
            self.encoding = encoding
            self.shell = bool(isinstance(cmd, str))

        def run(self):
            with subprocess.Popen(self.cmd, shell=self.shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
                # for line in proc.stdout.readlines():
                while (line := proc.stdout.readline()) != b"":
                    chardet_result = chardet.detect(line)
                    encoding = self.encoding or (chardet_result["encoding"] if chardet_result["confidence"] >= 0.8 else None) or "gb18030"
                    self.out_queue.put(line.decode(encoding, "ignore").replace("\r\n", ""))
                self.out_queue.put(b"")
                while (line := proc.stderr.readline()) != b"":
                    chardet_result = chardet.detect(line)
                    encoding = self.encoding or (chardet_result["encoding"] if chardet_result["confidence"] >= 0.8 else None) or "gb18030"
                    self.err_queue.put(line.decode(encoding, "ignore").replace("\r\n", ""))
                self.err_queue.put(b"")
                proc.wait()
                self.returncode_queue.put(proc.returncode)

    out_queue = Queue()
    err_queue = Queue()
    returncode_queue = Queue()
    cmd_thread = cmd_thread_work(queue_list=[out_queue, err_queue, returncode_queue], cmd=cmd, encoding=encoding)
    cmd_thread.setDaemon(True)
    cmd_thread.start()
    return out_queue, err_queue, returncode_queue


def update_self():
    self_path, self_dir, _ = get_self_dir()
    for root, _, files in os.walk(self_dir):
        for file in files:
            if file == "utils_dayepao.py":
                old_path = Path(root, file)
                if get_file_hash(self_path) != get_file_hash(old_path):
                    shutil.copy(self_path, old_path)
                    print(f"更新 {old_path} 成功")


def update_notify():
    self_path, self_dir, _ = get_self_dir()
    new_path = Path(self_path).parent / "notify_dayepao.py"
    for root, _, files in os.walk(self_dir):
        for file in files:
            if file == "notify_dayepao.py":
                old_path = Path(root, file)
                if get_file_hash(new_path) != get_file_hash(old_path):
                    shutil.copy(new_path, old_path)
                    print(f"更新 {old_path} 成功")


def update_creat_apscheduler():
    self_path, self_dir, _ = get_self_dir()
    new_path = Path(self_path).parent / "creat_apscheduler.py"
    for root, _, files in os.walk(self_dir):
        for file in files:
            if file == "creat_apscheduler.py":
                old_path = Path(root, file)
                if get_file_hash(new_path) != get_file_hash(old_path):
                    shutil.copy(new_path, old_path)
                    print(f"更新 {old_path} 成功")


if __name__ == "__main__":
    update_self()
    update_notify()
    update_creat_apscheduler()
