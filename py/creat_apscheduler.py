import datetime
import time
from functools import partial

import apscheduler.job
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED, JobExecutionEvent
from apscheduler.schedulers.background import BackgroundScheduler

from notify import send_message
from utils_dayepao import get_self_dir

"""
pip install apscheduler
"""


def creat_apscheduler(sched_job_list: list[dict], push_channel: list, timezone: str = "Asia/Shanghai"):
    """sched_job_list: [sched_job1, sched_job2, ...]

    push_channel: [push_channel1, push_channel2, ...]

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
        if push_channel:
            print(send_message("定时任务", pushstr, push_channel))

    sched = BackgroundScheduler(timezone=timezone)
    err_count = [0, time.time()]

    # 添加定时任务
    for sched_job in sched_job_list:
        sched.add_job(**sched_job)
    sched.add_listener(partial(job_event_handler, sched, err_count), EVENT_JOB_ERROR | EVENT_JOB_MISSED)
    return sched
