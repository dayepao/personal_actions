import time

from utils_dayepao import creat_apscheduler


def test(a, b=1):
    print(a)
    print(2*a)
    time.sleep(30)
    print(b)
    print(2*b)


var1 = 3
var2 = 30
job_list = [
    {"func": test, "trigger": "cron", "args": [var1], "kwargs": {}, "second": "*/1", "max_instances": 25, "name": "测试"},
    {"func": test, "trigger": "date", "args": [var2], "kwargs": {}, "name": "测试2", "max_instances": 1, "run_date": "2022-01-28 15:10:00", "misfire_grace_time": 1}
]

push_option = {
    "pushkey": "",
}

sched = creat_apscheduler(job_list, push_option)
sched.start()

while True:
    time.sleep(15)
    # sched.pause()
    print("*"*60)
