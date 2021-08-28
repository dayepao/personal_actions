import hashlib
import os
import time

import httpx


class bt_panel:
    def __init__(self, panel_url: str = None, panel_api_key: str = None) -> None:
        self.__PANEL_URL = panel_url
        self.__PANEL_API_KEY = panel_api_key

    def __get_md5(self, s: str):
        result = hashlib.md5()
        result.update(s.encode('utf-8'))
        return result.hexdigest()

    def __get_key_data(self):
        request_time = int(time.time())
        request_token = self.__get_md5(str(request_time) + self.__get_md5(self.__PANEL_API_KEY))
        post_data = {
            'request_time': request_time,
            'request_token': request_token
        }
        return post_data

    def get_system_total_SYSTEM(self) -> dict:
        '''获取系统基础统计'''

        # 拼接URL地址
        url = self.__PANEL_URL + '/system?action=GetSystemTotal'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名

        # 请求面板接口
        res = httpx.post(url, data=post_data)

        return res.json()

    def get_disk_info_SYSTEM(self) -> list[dict]:
        '''获取磁盘分区信息'''

        # 拼接URL地址
        url = self.__PANEL_URL + '/system?action=GetDiskInfo'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名

        # 请求面板接口
        res = httpx.post(url, data=post_data)

        return res.json()

    def get_crontab_CRONTAB(self) -> list[dict]:
        '''获取计划任务列表'''

        # 拼接URL地址
        url = self.__PANEL_URL + '/crontab?action=GetCrontab'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名

        # 请求面板接口
        res = httpx.post(url, data=post_data)

        return res.json()

    def get_crond_find_CRONTAB(self, post_id: int = 1) -> dict:
        '''获取指定计划任务详细信息'''

        # 拼接URL地址
        url = self.__PANEL_URL + '/crontab?action=get_crond_find'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名
        post_data['id'] = post_id

        # 请求面板接口
        res = httpx.post(url, data=post_data)

        return res.json()

    def get_data_list_CRONTAB(self, post_type: str = '') -> dict[str, list]:
        '''
        获取计划任务需要的配置信息

        post_type:
            sites: 获取网站列表
            databases: 获取数据库列表
        '''

        # 拼接URL地址
        url = self.__PANEL_URL + '/crontab?action=GetDataList'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名
        post_data['type'] = post_type

        # 请求面板接口
        res = httpx.post(url, data=post_data)

        return res.json()

    def add_crontab_CRONTAB(
        self,
        post_name: str = '',
        post_type: str = 'day',
        post_where1: str = '',
        post_hour: str = '1',
        post_minute: str = '30',
        post_week: str = '',
        post_sType: str = 'toShell',
        post_sBody: str = '',
        post_sName: str = '',
        post_backupTo: str = 'localhost',
        post_save: str = '',
        post_urladdress: str = 'undefined',
        post_save_local: str = 'undefined',
        post_notice: str = 'undefined',
        post_notice_channel: str = 'undefined',
    ) -> dict:
        '''
        添加计划任务

        post_name: 计划任务名称
        post_type: 执行周期类型 [day, week]
        post_where1: pass
        post_hour: 小时
        post_minute: 分钟
        post_week: 周几 [1, 2, 3, 4, 5, 6, 0(周日)]
        post_sType: 任务类型 [toShell, ]
        post_sBody: 脚本内容/排除规则 ``\\n``换行
        post_sName: 备份目录/备份网站/备份数据库
        post_backupTo: 备份位置 [localhost, ]
        post_save: 保留最新备份数
        post_urladdress: pass
        post_save_local: pass
        post_notice: pass
        post_notice_channel: pass
        '''

        # 拼接URL地址
        url = self.__PANEL_URL + '/crontab?action=AddCrontab'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名
        post_data['name'] = post_name
        post_data['type'] = post_type
        post_data['where1'] = post_where1
        post_data['hour'] = post_hour
        post_data['minute'] = post_minute
        post_data['week'] = post_week
        post_data['sType'] = post_sType
        post_data['sBody'] = post_sBody
        post_data['sName'] = post_sName
        post_data['backupTo'] = post_backupTo
        post_data['save'] = post_save
        post_data['urladdress'] = post_urladdress
        post_data['save_local'] = post_save_local
        post_data['notice'] = post_notice
        post_data['notice_channel'] = post_notice_channel

        # 请求面板接口
        res = httpx.post(url, data=post_data)

        return res.json()

    def del_crontab_CRONTAB(self, post_id: int) -> dict:
        '''删除指定计划任务'''

        # 拼接URL地址
        url = self.__PANEL_URL + '/crontab?action=DelCrontab'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名
        post_data['id'] = post_id

        # 请求面板接口
        res = httpx.post(url, data=post_data)

        return res.json()

    def start_task_CRONTAB(self, post_id: int) -> dict:
        '''执行指定计划任务'''

        # 拼接URL地址
        url = self.__PANEL_URL + '/crontab?action=StartTask'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名
        post_data['id'] = post_id

        # 请求面板接口
        res = httpx.post(url, data=post_data)

        return res.json()

    def get_logs_CRONTAB(self, post_id: int) -> dict:
        '''获取指定计划任务日志'''

        # 拼接URL地址
        url = self.__PANEL_URL + '/crontab?action=GetLogs'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名
        post_data['id'] = post_id

        # 请求面板接口
        res = httpx.post(url, data=post_data)

        return res.json()


if __name__ == '__main__':
    PANEL_URL = str(os.environ.get("PANEL_URL"))
    PANEL_API_KEY = str(os.environ.get("PANEL_API_KEY"))
    my_panel = bt_panel(panel_url=PANEL_URL, panel_api_key=PANEL_API_KEY)

    print(my_panel.get_crontab_CRONTAB())
    # print(my_panel.del_crontab_CRONTAB(post_id=16))
