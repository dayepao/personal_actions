import re
import subprocess
import winreg

# GET-StartApps
# (Get-AppxPackage).packagefamilyname

# CheckNetIsolation LoopbackExempt -?  # 环回免除操作命令

# 两种读取subprocess.Popen输出的方法
# startapp_names.append(str(io.TextIOWrapper(proc.stdout).readlines()).replace('\\n', ''))
# startapp_names.append(str(line.decode('gbk')).replace('\r\n', ''))


def read_subkeys(winreg_hkey, location):
    key = winreg.OpenKey(getattr(winreg, winreg_hkey), location)
    subkeys = []
    i = 0
    while True:
        try:
            subkeys.append(winreg.EnumKey(key, i))
            i += 1
        except Exception:
            # 一定要关闭这个键
            winreg.CloseKey(key)
            break
    return subkeys


def read_value(winreg_hkey, location):
    key = winreg.OpenKey(getattr(winreg, winreg_hkey), location)
    values = []
    i = 0
    while True:
        try:
            # 获取注册表对应位置的键和值
            values.append(winreg.EnumValue(key, i))
            i += 1
        except Exception:
            # 一定要关闭这个键
            winreg.CloseKey(key)
            break
    return values


def read_DisplayName(values):
    i = 0
    for i in range(len(values)):
        if values[i][0] == 'DisplayName':
            DisplayName = values[i][1]
        i += 1
    return DisplayName


def get_reg_uwp_dict():
    winreg_hkey = 'HKEY_CURRENT_USER'
    location = "SOFTWARE\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\CurrentVersion\\AppContainer\\Mappings"
    subkeys = read_subkeys(winreg_hkey, location)
    reg_uwp_dict = {}
    # print(subkeys)
    i = 0
    for i in range(len(subkeys)):
        sublocation = location + '\\' + subkeys[i]
        values = read_value(winreg_hkey, sublocation)
        # print(values)
        DisplayName = read_DisplayName(values)
        reg_uwp_dict[str(DisplayName)] = str(subkeys[i])
        i += 1
    return reg_uwp_dict


def get_startapps():
    startapps = {}
    ps = 'GET-StartApps'
    with subprocess.Popen(['powershell', ps], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
        for line in proc.stdout.readlines()[3:]:
            search_result = re.search(re.compile('(.+) +(.+)'), str(line.decode('gbk')).strip())
            if search_result:
                startapps[str(search_result.group(2).strip())] = str(search_result.group(1).strip())
    return startapps


def get_enabled_sid_list():
    enabled_sid_list = []
    cmd = 'CheckNetIsolation LoopbackExempt -s'
    with subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
        for line in proc.stdout.readlines():
            search_result = re.search(re.compile(' *SID:  (.+) *'), str(line.decode('gbk')).replace('\r\n', ''))
            if search_result:
                enabled_sid_list.append(str(search_result.group(1)))
    return enabled_sid_list


def get_uwp_list():
    '''返回[(DisplayName, name, sid)]'''
    reg_uwp_dict = get_reg_uwp_dict()
    startapps = get_startapps()
    uwp_list = []
    for DisplayName, sid in reg_uwp_dict.items():
        name_zh_cn = ''
        if not re.search(re.compile('[@{\\.\\?!]'), DisplayName):
            name_zh_cn = name_zh_cn + DisplayName + '/'
        for appid, name in startapps.items():
            try:
                if str(re.match(re.compile('.*?\\.(.*?)_.*?'), appid).group(1)) in DisplayName:
                    name_zh_cn = name_zh_cn + name + '/'
                elif str(re.match(re.compile('.*?\\.(.*?)_.*?'), appid).group(1)) == str(DisplayName).replace(' ', ''):
                    name_zh_cn = name + '/'
                elif name == DisplayName:
                    name_zh_cn = name + '/'
            except Exception:
                pass
        if name_zh_cn != '':
            name_zh_cn = name_zh_cn[:-1]
        uwp_list.append((DisplayName, name_zh_cn, sid))
    return uwp_list


if __name__ == '__main__':
    uwp_list = get_uwp_list()
    for uwp in uwp_list:
        if 'Realtek' in str(uwp):
            print(uwp)

# print(len(get_familynames()))
# print(len(get_startapps()))
# print(get_startapps())
# print(get_enabled_sid_list())
