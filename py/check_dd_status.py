import datetime
import socket
import sys
import time

import paramiko

from notify_dayepao import send_message

# pip install paramiko


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
        send_message("DD 监控", now + '\nDD 已完成\n密码修改为' + target_password, channels="wecom_app")
    else:
        send_message("DD 监控", now + '\nDD 已完成\n密码修改失败', channels="wecom_app")


if __name__ == '__main__':
    target_ip = input("请输入要监控的服务器IP : ")
    default_password = input("请输入 DD 包默认密码(默认为\"cxthhhhh.com\"): ")
    target_password = input("请输入要修改的密码(为空则不修改): ")

    if default_password == '':
        default_password = "cxthhhhh.com"

    start_time = datetime.datetime.now()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    while True:
        now_time = datetime.datetime.now()
        now = now_time.strftime("%Y-%m-%d %H:%M:%S") + "\n"
        print(now + '  正在监测')
        time.sleep(1)
        try:
            ssh.connect(hostname=target_ip, port=22, username='root', password=default_password)
        except socket.gaierror:
            print('\n\nIP 地址错误')
            sys.exit(0)
        except paramiko.ssh_exception.AuthenticationException:
            send_message("DD 监控", now + '\nDD 已完成\n[错误] 默认密码错误', channels="wecom_app")
            sys.exit(0)
        except Exception:
            delta_time = now_time - start_time
            if delta_time.seconds > 3600:
                send_message("DD 监控", now + '\n' + str(round(delta_time.seconds / 3600, 2)) + "小时后 DD 仍未成功，停止监测", channels="wecom_app")
                sys.exit(0)
            continue
        else:
            if target_password:
                change_password(now, ssh, target_password)
            else:
                send_message("DD 监控", now + '\nDD 已完成', channels="wecom_app")
            break
        finally:
            ssh.close()
