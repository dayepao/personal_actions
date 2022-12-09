"""
Wake up the specified host through preset trigger conditions
"""
# import ipaddress

import ipaddress
import json
import os
import socket
import struct
import sys

import __main__
# import psutil
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class WOL_Dayepao(toga.App):
    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box(style=Pack(direction=COLUMN))

        # 创建 MAC 地址输入框
        mac_address_label = toga.Label("MAC 地址: ", style=Pack(padding=(0, 5), alignment="center"))
        self.mac_address_input = toga.TextInput(placeholder="00:00:00:00:00:00", style=Pack(flex=1))
        mac_address_box = toga.Box(style=Pack(direction=ROW, padding=5))
        mac_address_box.add(mac_address_label)
        mac_address_box.add(self.mac_address_input)
        # 创建广播地址输入框
        broadcast_address_label = toga.Label("广播地址: ", style=Pack(padding=(0, 5)))
        self.broadcast_address_input = toga.TextInput(placeholder=self.get_broadcast_address(), style=Pack(flex=1))
        broadcast_address_box = toga.Box(style=Pack(direction=ROW, padding=5))
        broadcast_address_box.add(broadcast_address_label)
        broadcast_address_box.add(self.broadcast_address_input)
        # 创建端口输入框
        port_label = toga.Label("端口: ", style=Pack(padding=(0, 5)))
        self.port_input = toga.TextInput(placeholder="9", style=Pack(flex=1))
        port_box = toga.Box(style=Pack(direction=ROW, padding=5))
        port_box.add(port_label)
        port_box.add(self.port_input)
        # 创建IP地址输入框
        ip_address_label = toga.Label("IP 地址: ", style=Pack(padding=(0, 5)))
        self.ip_address_input = toga.TextInput(placeholder="可选", style=Pack(flex=1))
        ip_address_box = toga.Box(style=Pack(direction=ROW, padding=5))
        ip_address_box.add(ip_address_label)
        ip_address_box.add(self.ip_address_input)
        # 创建保存和清除配置按钮
        save_button = toga.Button("保存配置", on_press=self.save_button_action, style=Pack(flex=1))
        clear_button = toga.Button("恢复默认配置", on_press=self.clear_button_action, style=Pack(flex=1))
        config_button_box = toga.Box(style=Pack(direction=ROW))
        config_button_box.add(save_button)
        config_button_box.add(clear_button)
        # 创建启动和停止按钮
        self.start_button = toga.Button("启动", on_press=self.start, style=Pack(flex=1))
        self.stop_button = toga.Button("停止", on_press=self.stop, style=Pack(flex=1))
        control_button_box = toga.Box(style=Pack(direction=ROW))
        control_button_box.add(self.start_button)
        control_button_box.add(self.stop_button)

        main_box.add(mac_address_box)
        main_box.add(broadcast_address_box)
        main_box.add(port_box)
        main_box.add(ip_address_box)
        main_box.add(config_button_box)
        main_box.add(control_button_box)

        self.config_path = os.path.join(self.get_self_dir()[1], "config.json")
        self.initialize_config()
        self.read_config()
        self.set_ui()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def initialize_config(self):
        self.config_dict = {
            "mac_address": "",
            "broadcast_address": self.get_broadcast_address(),
            "port": "9",
            "ip_address": "",
        }

    # 读取配置文件
    def read_config(self):
        config_dict = {}
        try:
            with open(self.config_path, "r") as f:
                config_dict: dict = json.load(f)
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            os.remove(self.config_path)
            pass
        self.config_dict.update(config_dict)

    def set_ui(self):
        """
        设置界面
        """
        self.mac_address_input.value = self.config_dict.get("mac_address", "")
        self.broadcast_address_input.value = self.config_dict.get("broadcast_address", self.get_broadcast_address())
        self.port_input.value = str(self.config_dict.get("port", "9"))
        self.ip_address_input.value = self.config_dict.get("ip_address", "")

    def save_button_action(self, widget):
        """
        保存配置按钮事件
        """
        self.save_config(widget)
        self.main_window.info_dialog("提示", "保存成功")

    def save_config(self, widget):
        self.config_dict = {
            "mac_address": self.mac_address_input.value,
            "broadcast_address": self.broadcast_address_input.value,
            "port": self.port_input.value,
            "ip_address": self.ip_address_input.value
        }
        with open(self.config_path, "w+") as f:
            json.dump(self.config_dict, indent=4, fp=f)
        # print(f"MAC 地址: {self.mac_address_input.value}")
        # print(f"广播地址: {self.broadcast_address_input.value}")
        # print(f"端口: {self.port_input.value}")
        # print(f"IP 地址: {self.ip_address_input.value}")

    def clear_button_action(self, widget):
        """
        恢复默认配置按钮事件
        """
        self.clear_config(widget)

    def clear_config(self, widget):
        self.initialize_config()
        self.set_ui()

    def get_broadcast_address(self):
        """
        获取广播地址
        """
        broadcast_address = ""
        # 等待 psutil 支持 Android
        # for interface, snics in psutil.net_if_addrs().items():
        #     for snic in snics:
        #         if snic.family == 2 and snic.netmask == "255.255.255.0":
        #             broadcast_address = ipaddress.IPv4Interface(f"{snic.address}/{snic.netmask}").network.broadcast_address
        #             break
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            broadcast_address = ip_address.rsplit(".", 1)[0] + ".255"

        # print(f"广播地址: {broadcast_address}")
        return broadcast_address if broadcast_address else "192.168.1.255"

    def check_config(self):
        """
        检查配置是否合法
        """
        # 检查输入的 MAC 地址是否合法
        try:
            mac_address = self.config_dict["mac_address"]
            if not mac_address:
                raise ValueError("MAC 地址不能为空")
            mac_address = mac_address.replace(":", "")
            if "：" in mac_address:
                raise ValueError("MAC 地址中不能包含中文冒号")
            if len(mac_address) != 12:
                raise ValueError("MAC 地址长度不正确")
            int(mac_address, 16)
        except ValueError as e:
            self.main_window.error_dialog("错误", str(e))
            return False
        # 检查输入的广播地址是否合法
        try:
            broadcast_address = self.config_dict["broadcast_address"]
            if not broadcast_address:
                raise ValueError("广播地址不能为空")
            ipaddress.ip_address(broadcast_address)
        except ValueError as e:
            self.main_window.error_dialog("错误", str(e))
            return False
        # 检查输入的端口是否合法
        try:
            port = self.config_dict["port"]
            if not port:
                raise ValueError("端口不能为空")
            port = int(port)
            if not 0 < port < 65536:
                raise ValueError("端口不在有效范围内")
        except ValueError as e:
            self.main_window.error_dialog("错误", str(e))
            return False
        # 如果IP地址不为空，检查输入的IP地址是否合法
        ip_address = self.config_dict["ip_address"]
        if ip_address:
            try:
                ipaddress.ip_address(ip_address)
            except ValueError as e:
                self.main_window.error_dialog("错误", str(e))
                return False
        return True

    def start(self, widget):
        self.save_config(widget)
        if not self.check_config():
            return
        self.wake_on_lan(self.config_dict["mac_address"], self.config_dict["broadcast_address"], int(self.config_dict["port"]))

    def stop(self, widget):
        print("stop")

    def get_checksum(self, data: bytes):
        """
        计算校验和
        """
        checksum = 0
        count_to = (len(data) // 2) * 2
        count = 0
        while count < count_to:
            this_val = data[count + 1] * 256 + data[count]
            checksum += this_val
            checksum &= 0xffffffff
            count += 2
        if count_to < len(data):
            checksum += data[len(data) - 1]
            checksum &= 0xffffffff
        checksum = (checksum >> 16) + (checksum & 0xffff)
        checksum += (checksum >> 16)
        answer = ~checksum
        answer &= 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer

    def ping_to_ip_address(self, ip_address: str, timeout: int = 5):
        """
        ping IP 地址
        """
        # 构造 ICMP 包
        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        icmp_socket.settimeout(timeout)
        icmp_socket.bind(("", 0))
        icmp_id = (os.getpid() & 0xFFFF) | 0x8000
        icmp_sequence = 1
        icmp_checksum = 0
        icmp_header = struct.pack("!BBHHH", 8, 0, icmp_checksum, icmp_id, icmp_sequence)
        icmp_data = bytes("abcdefghijklmnopqrstuvwabcdefghi", "utf-8")
        icmp_checksum = self.get_checksum(icmp_header + icmp_data)
        icmp_header = struct.pack("!BBHHH", 8, 0, icmp_checksum, icmp_id, icmp_sequence)
        icmp_packet = icmp_header + icmp_data
        # 发送 ICMP 包
        icmp_socket.sendto(icmp_packet, 0, (ip_address, 80))
        # 接收 ICMP 包
        try:
            icmp_socket.recvfrom(1024)
        except socket.timeout:
            return False
        return True

    # wake on lan
    def wake_on_lan(self, mac_address: str, broadcast_address, port, secure_on_password: str = None):
        """
        唤醒远程电脑
        """
        # 构造 Magic Packet
        mac_address = mac_address.replace(":", "")
        magic_packet = "F" * 12 + mac_address * 16
        if secure_on_password:
            magic_packet += secure_on_password.replace(":", "")
        magic_packet = bytes.fromhex(magic_packet)
        # 发送 Magic Packet
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(magic_packet, (broadcast_address, port))

    def get_self_dir(self):
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


def main():
    return WOL_Dayepao()
