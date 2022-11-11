import datetime
import hashlib
import os
import re
import subprocess
import sys
import time
from functools import partial
from queue import Queue
from threading import Thread

import __main__
import apscheduler.job
import chardet
import httpx
from apscheduler.events import (EVENT_JOB_ERROR, EVENT_JOB_MISSED,
                                JobExecutionEvent)
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup

"""
pip install httpx
pip install beautifulsoup4
pip install chardet
pip install apscheduler
"""


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


def post_method(url: str, postdata=None, postjson=None, headers: dict = None, timeout=5, max_retries=5, c: httpx.Client = None):
    """
    timeout: 超时时间, 单位秒(s), 默认为 5 秒, 为 `None` 时禁用
    max_retries: 最大尝试次数, 默认为 5 次, 为 0 时禁用
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


def dayepao_push(
    pushstr: str,
    pushkey: str,
    pushurl: str = "https://push.dayepao.com/",
    agentid: str = "1000002",
    touser: str = "@all",
):
    try:
        pushurl = "{}?pushkey={}".format(pushurl, pushkey)
    except Exception as e:
        print(sys._getframe().f_code.co_name + ": " + str(e))
        pushurl = "https://push.dayepao.com/?pushkey="
    pushdata = {
        "touser": touser,
        "msgtype": "text",
        "agentid": agentid,
        "text": {
            "content": pushstr
        },
        "safe": 0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 0
    }
    return post_method(pushurl, postjson=pushdata, timeout=10).text


def make_dir(path: str):
    """创建路径

    `make_dir(file_path[:file_path.rfind('\\')])`

    file_path: 文件完整路径 (包括文件名)
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_self_dir():
    """获取自身路径

    返回`(py_path, py_dir, py_name)`

    py_path: 当前.py文件完整路径 (包括文件名)
    py_dir: 当前.py文件所在文件夹路径
    py_name: 当前.py文件名
    """
    py_path = os.path.realpath(__main__.__file__)
    py_dir, py_name = os.path.split(py_path)
    if os.path.splitext(__file__)[1] != ".py":
        py_path = os.path.realpath(sys.executable)
        py_dir, py_name = os.path.split(py_path)
    return py_path, py_dir, py_name


def get_file_hash(file_path: str, name: str = "md5"):
    """获取文件哈希值

    name: 哈希算法, 可选: 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'blake2b', 'blake2s', 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512', 'shake_128', 'shake_256'
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


def get_tags_with_certain_attrs(url: str, headers: dict = None, attrs: dict[str, str] = None, max_retries=5, c: httpx.Client = None):
    """获得网页指定属性的标签

    attrs: 标签属性
    max_retries: 最大尝试次数, 默认为 5 次, 为 0 时禁用

    返回`(tags, tags_content)`

    tags: 标签列表
    tags_content: 标签内容列表
    """
    res = get_method(url, headers, max_retries=max_retries, c=c)
    soup = BeautifulSoup(res.text, 'html.parser')
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
        search_result = re.search(re.compile(r'^<.+?>(.+)<.+?>$'), str(tag).replace("\r", "").replace("\n", ""))
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
        def __init__(self, out_queue: Queue, err_queue: Queue, cmd: str | list, encoding: str) -> None:
            super().__init__()
            self.out_queue = out_queue
            self.err_queue = err_queue
            self.cmd = cmd
            self.encoding = encoding

        def run(self):
            with subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
                # for line in proc.stdout.readlines():
                while (line := proc.stdout.readline()) != b'':
                    chardet_result = chardet.detect(line)
                    encoding = self.encoding or (chardet_result["encoding"] if chardet_result["confidence"] >= 0.8 else None) or "gb18030"
                    self.out_queue.put(line.decode(encoding, "ignore").replace("\r\n", ""))
                self.out_queue.put(b'')
                while (line := proc.stderr.readline()) != b'':
                    chardet_result = chardet.detect(line)
                    encoding = self.encoding or (chardet_result["encoding"] if chardet_result["confidence"] >= 0.8 else None) or "gb18030"
                    self.err_queue.put(line.decode(encoding, "ignore").replace("\r\n", ""))
                self.err_queue.put(b'')

    out_queue = Queue()
    err_queue = Queue()
    cmd_thread = cmd_thread_work(out_queue=out_queue, err_queue=err_queue, cmd=cmd, encoding=encoding)
    cmd_thread.setDaemon(True)
    cmd_thread.start()
    return out_queue, err_queue


def creat_apscheduler(sched_job_list: list[dict], push_option: dict = {}, timezone: str = "Asia/Shanghai"):
    """sched_job_list: [sched_job1, sched_job2, ...]

    push_option: 错误推送参数

    {"pushkey": "", "pushurl": "https://push.dayepao.com/", "agentid": "1000002"}

    sched_job: 计划任务示例

    {"name": "name", "id": "", "func": func, "args": [], "kwargs": {}, "trigger": "date | interval | cron", "second": "*/30", "next_run_time": datetime.datetime.now() + datetime.timedelta(seconds=5), "max_instances": 1, "timezone": "Asia/Shanghai"}
    """

    # 定时任务事件处理
    def job_event_handler(sched: BackgroundScheduler, err_count: list[int | float], event: JobExecutionEvent):
        if (time.time() - err_count[1]) > 60:
            err_count[0] = 0

        err_count[0] += 1
        err_count[1] = time.time()

        job: apscheduler.job.Job = sched.get_job(event.job_id)
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")

        try:
            if event.exception:
                pushstr = "{}\n{}\n第{}次出现异常\n异常任务: {}\nTraceback (most recent call last):\n{}\n{}\n".format(
                    str(now),
                    str(get_self_dir()[2]),
                    str(err_count[0]),
                    str(job.name),
                    str(event.traceback),
                    str(event.exception),
                )
            else:
                pushstr = "{}\n{}\n第{}次出现异常\n异常任务: {}\n任务被跳过\n原定执行时间: \n{}\n".format(
                    str(now),
                    str(get_self_dir()[2]),
                    str(err_count[0]),
                    str(job.name),
                    str(event.scheduled_run_time),
                )
        except Exception:
            pushstr = "{}\n{}\n第{}次出现异常\n异常任务: 未知\n原定执行时间: \n{}\n".format(
                str(now),
                str(get_self_dir()[2]),
                str(err_count[0]),
                str(event.scheduled_run_time),
            )

        if err_count[0] >= 3:
            sched.pause()
            pushstr += "短时间内出现3次异常, 定时任务已暂停"

        print(pushstr)
        if "pushkey" in push_option:
            print(dayepao_push(pushstr, **push_option))

    sched = BackgroundScheduler(timezone=timezone)
    err_count = [0, time.time()]

    # 添加定时任务
    for sched_job in sched_job_list:
        sched.add_job(**sched_job)
    sched.add_listener(partial(job_event_handler, sched, err_count), EVENT_JOB_ERROR | EVENT_JOB_MISSED)
    return sched


def update_self():
    self_path, self_dir = get_self_dir()[0:2]
    for filename in os.listdir(self_dir):
        if (os.path.isdir(os.path.join(self_dir, filename))) and (os.path.exists(old_path := os.path.join(self_dir, filename, "utils_dayepao.py"))) and (get_file_hash(self_path) != get_file_hash(old_path)):
            with open(self_path, "rb") as f:
                new_content = f.read()
            with open(old_path, "wb") as f:
                f.write(new_content)


if __name__ == "__main__":
    update_self()
