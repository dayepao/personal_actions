import datetime
import os
import sys
import time

import httpx
import paramiko

# pip install paramiko
PUSH_KEY = os.environ.get("PUSH_KEY")


def post_method(url, postdata=None, postjson=None, headers=None):
    while True:
        try:
            res = httpx.post(url, data=postdata, json=postjson, headers=headers)
        except Exception as e:
            print(sys._getframe().f_code.co_name + ": " + str(e))
            time.sleep(1)
            continue
        else:
            break
    return res


def notice(pushstr):
    print('\n\n' + pushstr)
    pushurl = "https://push.dayepao.com/?pushkey=" + PUSH_KEY
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
    post_method(pushurl, postjson=pushdata)


def change_password(now, ssh: paramiko.SSHClient, target_password: str):
    print('开始修改密码...')
    stdin, stdout, stderr = ssh.exec_command('passwd')
    time.sleep(1)
    stdin.write(target_password + "\n")
    time.sleep(1)
    stdin.write(target_password + "\n")
    stdin.flush()
    res, err = stdout.read(), stderr.read()
    result = res if res else err
    if 'password updated successfully' in result.decode():
        notice(now + '\nDD 已完成\n密码修改为' + target_password)
    else:
        notice(now + '\nDD 已完成\n密码修改失败')


if __name__ == '__main__':
    target_ip = input("请输入要监控的 IP : ")
    default_password = input("请输入 DD 包默认密码(默认为\"cxthhhhh.com\"): ")
    target_password = input("请输入要修改的密码(为空则不修改): ")

    start_time = datetime.datetime.now()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    while True:
        now_time = datetime.datetime.now()
        now = now_time.strftime("%Y-%m-%d %H:%M:%S")
        print(now + '  正在监测')
        time.sleep(1)
        try:
            ssh.connect(hostname=target_ip, port=22, username='root', password=default_password)
        except paramiko.ssh_exception.AuthenticationException:
            notice(now + '\nDD 已完成\n[错误] 默认密码错误')
            sys.exit(0)
        except Exception:
            delta_time = now_time - start_time
            if delta_time.seconds > 3600:
                notice(now + '\n' + str(round(delta_time.seconds / 3600, 2)) + "小时后 DD 仍未成功，停止监测")
                sys.exit(0)
            continue
        else:
            if target_password:
                change_password(now, ssh, target_password)
            else:
                notice(now + '\nDD 已完成')
            break
        finally:
            ssh.close()
