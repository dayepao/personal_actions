import hashlib
import os
import re
import subprocess
import sys
import time
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


def get_method(url, headers: dict = None, timeout=5, max_retries=5, c: httpx.Client = None):
    """
    timeout: 超时时间，单位秒(s)，默认为 5 秒，为 `None` 时禁用
    max_retries: 最大尝试次数，默认为 5 次，为 0 时禁用
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


def post_method(url, postdata=None, postjson=None, headers: dict = None, timeout=5, max_retries=5, c: httpx.Client = None):
    """
    timeout: 超时时间，单位秒(s)，默认为 5 秒，为 `None` 时禁用
    max_retries: 最大尝试次数，默认为 5 次，为 0 时禁用
    """
    k = 1
    while (k <= max_retries) or (max_retries == 0):
        try:
            if c is not None:
                res = c.post(url, data=postdata, json=postjson, headers=headers, timeout=timeout)
            else:
                res = httpx.post(url, data=postdata, json=postjson, headers=headers, timeout=timeout)
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


def dayepao_push(pushstr, pushkey=""):
    pushurl = "https://push.dayepao.com/?pushkey=" + (os.environ.get("PUSH_KEY") if os.environ.get("PUSH_KEY") else pushkey)
    pushdata = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": 1000002,
        "text": {
            "content": pushstr
        },
        "safe": 0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 0
    }
    return post_method(pushurl, postjson=pushdata, timeout=10).text


def make_dir(path):
    """创建路径

    `make_dir(file_path[:file_path.rfind('\\')])`

    file_path: 文件完整路径 (包括文件名)
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_self_dir():
    """获取自身路径

    返回`(py_path, py_dir)`

    py_path: 当前.py文件完整路径 (包括文件名)
    py_dir: 当前.py文件所在文件夹路径
    """
    py_path = __main__.__file__
    py_dir = py_path[:py_path.rfind('\\')]
    return py_path, py_dir


def get_file_hash(file_path, name: str = "md5"):
    """获取文件哈希值

    name: 哈希算法，可选: 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'blake2b', 'blake2s', 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512', 'shake_128', 'shake_256'
    """
    hashstr = hashlib.new(name)
    with open(file_path, "rb") as f:
        while (tempdata := f.read(40960)) != b'':
            hashstr.update(tempdata)
    return str(hashstr.hexdigest())


def download_file(file_path: str, file_url: str, headers: dict = None):
    """下载文件到指定路径
    """
    make_dir(file_path[:file_path.rfind('\\')])
    file_content = get_method(file_url, headers=headers).content
    with open(file_path, "wb") as f:
        f.write(file_content)


def get_tags_with_certain_attrs(url: str, headers: dict = None, attrs: dict[str, str] = None, c: httpx.Client = None):
    """获得网页指定属性的标签

    返回`(tags, tags_content)`

    tags: 标签列表
    tags_content: 标签内容列表
    attrs: 标签属性
    """
    res = get_method(url, headers, c=c)
    soup = BeautifulSoup(res.text, 'html.parser')
    temp_tags = list(soup.find_all(attrs=attrs))
    tags = []

    # 去重 && 当attrs为空时，去除具有包含关系的结果
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
        search_result = re.search(re.compile(r'^<.+?>(.+)<.+?>$'), str(tag).replace("\r", "").replace("\n", ""))
        if search_result:
            tags_content.append(str(search_result.group(1).strip()))
    return (tags, tags_content)


def search_in_website(url: str, content: str, headers: dict = None, attrs: dict[str, str] = None, c: httpx.Client = None):
    """搜索网页中是否有指定内容，返回布尔值

    attrs: 标签属性
    """
    tags_content = get_tags_with_certain_attrs(url, headers=headers, attrs=attrs, c=c)[1]
    return bool(content in " / ".join(tags_content))


def get_content_in_website(url, r_e: str, headers: dict = None, attrs: dict[str, str] = None, c: httpx.Client = None):
    """搜索网页中匹配指定正则表达式的内容

    r_e: 正则表达式，例如`r'^<.+?>(.+)<.+?>$'`
    attrs: 标签属性
    """
    tags_content = get_tags_with_certain_attrs(url, headers=headers, attrs=attrs, c=c)[1]
    search_result = re.findall(re.compile(r_e), " / ".join(tags_content))
    return search_result


def set_powershell_cmd(*args: str):
    if (powershell_cmd := ";".join(args)).strip() == "":
        raise ValueError("命令为空，请检查传入参数")
    return powershell_cmd


def cmd_dayepao(cmd: str | list, encoding: str = None):
    """
    cmd: "命令" 或 ["powershell", "命令"]
    """
    class cmd_thread_work(Thread):
        def __init__(self, queue: Queue, cmd: str | list, encoding: str) -> None:
            super().__init__()
            self.queue = queue
            self.cmd = cmd
            self.encoding = encoding

        def run(self):
            with subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
                # for line in proc.stdout.readlines():
                while (line := proc.stdout.readline()) != b'':
                    chardet_result = chardet.detect(line)
                    encoding = self.encoding or (chardet_result["encoding"] if chardet_result["confidence"] >= 0.8 else None) or "gb18030"
                    self.queue.put(line.decode(encoding, "ignore").replace("\r\n", ""))
            self.queue.put(b'')

    queue = Queue()
    cmd_thread = cmd_thread_work(queue=queue, cmd=cmd, encoding=encoding)
    cmd_thread.setDaemon(True)
    cmd_thread.start()
    return queue


def update_self():
    self_path, self_dir = get_self_dir()
    for filename in os.listdir(self_dir):
        if (os.path.isdir(os.path.join(self_dir, filename))) and (os.path.exists(old_path := os.path.join(self_dir, filename, "utils_dayepao.py"))) and (get_file_hash(self_path) != get_file_hash(old_path)):
            with open(self_path, "rb") as f:
                new_content = f.read()
            with open(old_path, "wb") as f:
                f.write(new_content)


if __name__ == "__main__":
    update_self()
