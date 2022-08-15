# @lopes(https://gist.github.com/lopes/9bf99ff7cf3d6e8d4c98972bb3262985)

import ctypes
import re
import sys
from sys import argv
from winreg import (HKEY_CURRENT_USER, KEY_ALL_ACCESS, OpenKey, QueryValueEx,
                    SetValueEx)

from utils_dayepao import cmd_dayepao


def set_key(name, value):
    SetValueEx(INTERNET_SETTINGS, name, 0,
               QueryValueEx(INTERNET_SETTINGS, name)[1], value)


def get_gateway(adapter):
    queue = cmd_dayepao(r"ipconfig /all")[0]
    outstr = ""
    while (line := queue.get()) != b"":
        outstr += line
    re_result = re.search(re.compile(adapter + r':.*?默认网关.*?: (.*?)[^\.\d]'), outstr)
    if re_result:
        if "适配器" in re_result.group().replace(adapter, ""):
            return None
        return re_result.group(1).strip()
    return None


if __name__ == '__main__':
    PROXIES = {
        'default': {
            'enable': 1,
            'override': u'localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;192.168.*',
            'server': u'{}:10811'.format(get_gateway("以太网适配器 以太网")),
        },
        'off': {
            'enable': 0,
            'override': u'-',
            'server': u'-',
        },
        'proxyid': {
            'enable': 1,
            'override': u'localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;192.168.*',
            'server': u'{}:10811'.format(get_gateway("以太网适配器 以太网")),
        },
    }

    INTERNET_SETTINGS = OpenKey(HKEY_CURRENT_USER,
                                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                                0, KEY_ALL_ACCESS)

    try:
        proxy = argv[1]
    except IndexError:
        print(f'Enable....: {QueryValueEx(INTERNET_SETTINGS,"ProxyEnable")[0]}')
        print(f'Server....: {QueryValueEx(INTERNET_SETTINGS,"ProxyServer")[0]}')
        print(f'Exceptions: {QueryValueEx(INTERNET_SETTINGS,"ProxyOverride")[0]}')
        sys.exit(0)

    try:
        set_key('ProxyEnable', PROXIES[proxy]['enable'])
        set_key('ProxyOverride', PROXIES[proxy]['override'])
        set_key('ProxyServer', PROXIES[proxy]['server'])

        # granting the system refresh for settings take effect
        internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
        internet_set_option(0, 37, 0, 0)  # refresh
        internet_set_option(0, 39, 0, 0)  # settings changed
    except KeyError:
        print(f'Registered proxies: {PROXIES.keys()}')
        sys.exit(1)
    sys.exit(0)
