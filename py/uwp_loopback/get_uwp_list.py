import os
import re
import winreg

# GET-StartApps
# (Get-AppxPackage).packagefamilyname

# CheckNetIsolation LoopbackExempt -?  # 环回免除操作命令


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


def get_reg_uwp_list():
    winreg_hkey = 'HKEY_CURRENT_USER'
    location = "SOFTWARE\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\CurrentVersion\\AppContainer\\Mappings"
    subkeys = read_subkeys(winreg_hkey, location)
    uwp_list = []
    # print(subkeys)
    i = 0
    for i in range(len(subkeys)):
        sublocation = location + '\\' + subkeys[i]
        values = read_value(winreg_hkey, sublocation)
        # print(values)
        DisplayName = read_DisplayName(values)
        uwp_list.append((DisplayName, subkeys[i]))
        i += 1
    return uwp_list


def get_familynames():
    ps = os.popen('powershell (Get-AppxPackage).packagefamilyname')
    familynames = []
    for familyname in ps.readlines():
        familynames.append(str(familyname).replace('\n', ''))
    return familynames


def get_startapps():
    ps = os.popen('powershell (GET-StartApps).name')
    startapp_names = []
    for startapp_name in ps.readlines():
        startapp_names.append(str(startapp_name).replace('\n', ''))
    ps = os.popen('powershell (GET-StartApps).appid')
    startapp_appids = []
    for startapp_appid in ps.readlines():
        startapp_appids.append(str(startapp_appid).replace('\n', ''))
    startapps = list(zip(startapp_names, startapp_appids))
    return startapps


def get_uwp_list():
    '''返回[(DisplayName, name, sid)]'''
    reg_uwp_list = get_reg_uwp_list()
    startapps = get_startapps()
    uwp_list = []
    for DisplayName, sid in reg_uwp_list:
        name_zh_cn = ''
        for name, appid in startapps:
            try:
                if str(re.match(re.compile('.*?\\.(.*?)_.*?'), appid).group(1)) in DisplayName:
                    name_zh_cn = name_zh_cn + name + '/'
                elif str(re.match(re.compile('.*?\\.(.*?)_.*?'), appid).group(1)) == str(DisplayName).replace(' ', ''):
                    name_zh_cn = name_zh_cn + name + '/'
                elif name == DisplayName:
                    name_zh_cn = name_zh_cn + name + '/'
            except Exception:
                pass
        if name_zh_cn != '':
            name_zh_cn = name_zh_cn[:-1]
        uwp_list.append((DisplayName, name_zh_cn, sid))
    return uwp_list


if __name__ == '__main__':
    uwp_list = get_uwp_list()
    for uwp in uwp_list:
        if 'Pay' in str(uwp):
            print(uwp)

# print(len(get_familynames()))
# print(len(get_startapps()))
