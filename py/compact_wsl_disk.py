import ctypes
import os
import subprocess
import sys


PASSWORD = os.environ.get('PASSWORD')


def set_diskpart_command(*args: str):
    ps = '@"\n'
    for arg in args:
        ps = ps + arg + '\n'
    ps = ps + '\"@ | diskpart'
    return ps


def set_ps_command(*args: str):
    ps = ''
    for arg in args:
        ps = ps + arg + ';'
    return ps


def get_disk_paths(disk_file_name: str = 'ext4.vhdx'):
    print("\n开始查找名为 " + disk_file_name + " 的 WSL2 磁盘文件")
    disk_paths = []
    local_path = os.environ.get('LOCALAPPDATA')
    target_path = local_path + r"\Packages"
    ps = "get-childitem -path " + target_path + " -recurse -filter \"" + disk_file_name + "\" -ErrorAction SilentlyContinue | foreach-object {write-output \"$(${PSItem}.FullName)\"}"
    with subprocess.Popen(['powershell', ps], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
        # for line in proc.stdout.readlines():
        while (line := proc.stdout.readline()) != b'':
            disk_paths.append(str(line.decode('gbk').replace('\r\n', '')))
    return disk_paths


def shutdown_wsl():
    print('\n即将终止所有运行的 WSL2 轻型工具虚拟机，请保存好数据')
    input('按回车键继续...')
    print('开始压缩...')
    ps = set_ps_command(
        r'write-output ' + PASSWORD + r' | wsl sudo -S fstrim',
        r'wsl --shutdown',
        r'Start-Sleep -s 5',
        r'wsl --shutdown'
    )
    with subprocess.Popen(['powershell', ps], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW, start_new_session=True) as proc:
        proc.wait()


def get_file_size(target_file: str):
    ps = set_ps_command(
        r'$target_file = $(get-item ' + target_file + r')',
        r'write-output "$($target_file.length/1MB)"'
    )
    with subprocess.Popen(['powershell', ps], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
        size = int(proc.stdout.read().decode('gbk').replace('\r\n', ''))
    if size > 1024:
        size = str(round(size/1024, 2)) + ' GB'
    else:
        size = str(round(size, 2)) + ' MB'
    return size


def compact_wsl2_disk(disk_path):
    # ps = "@\"\n" + "select vdisk file=\"" + disk_path + "\"\n" + "detach vdisk\n" + "attach vdisk readonly\n" + "compact vdisk\n" + "detach vdisk\n" + "exit\n" + "\"@ | diskpart"
    print('\n开始压缩: ' + str(disk_path))
    print('压缩前大小: ' + get_file_size(disk_path))
    ps = set_diskpart_command(
        r'select vdisk file="' + disk_path + r'"',
        r'detach vdisk',
        r'attach vdisk readonly',
        r'compact vdisk',
        r'detach vdisk',
        r'exit'
    )
    with subprocess.Popen(['powershell', ps], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
        status = False
        # for line in iter(proc.stdout.readline, b''):
        while (line := proc.stdout.readline()) != b'':
            line = line.decode('gbk').replace('\r\n', '').strip()
            if '已成功压缩虚拟磁盘文件' in line:
                status = True
    if status:
        print('压缩成功')
        print('压缩后大小: ' + get_file_size(disk_path))
    else:
        print('压缩失败')
    return status


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


if __name__ == '__main__':
    if is_admin():
        disk_file_name = 'ext4.vhdx'
        disk_paths = get_disk_paths(disk_file_name)
        if disk_paths:
            print("\n共找到 " + str(len(disk_paths)) + " 个 WSL2 磁盘文件")
            shutdown_wsl()
            success_num = 0
            for disk_path in disk_paths:
                if compact_wsl2_disk(disk_path):
                    success_num += 1
            print("\n压缩完成: " + str(success_num) + " 个成功, " + str(len(disk_paths)-success_num) + " 个失败")
        else:
            print("\n未找到名为 " + disk_file_name + " 的 WSL2 磁盘文件")
        input('按回车键退出...')
    else:
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        # else:  # in python2.x
            # ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)
