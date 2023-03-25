import re
import subprocess
import time
from pathlib import Path

import psutil
import win32con
import win32gui

# pip install pywin32
# pip install psutil


def find_windows_by_regex(pattern):
    """使用正则表达式匹配窗口标题"""
    # 枚举所有窗口，查找匹配的窗口
    def enum_windows_callback(hwnd, windows_hwnd):
        window_text = win32gui.GetWindowText(hwnd)
        if re.search(pattern, window_text, re.IGNORECASE):
            windows_hwnd.append(hwnd)
    # 调用EnumWindows函数
    windows_hwnd = []
    win32gui.EnumWindows(enum_windows_callback, windows_hwnd)
    return windows_hwnd


def get_running_process(pattern):
    """使用正则表达式匹配进程名称"""
    processes = []
    for process in psutil.process_iter():
        try:
            if re.search(pattern, process.name(), re.IGNORECASE):
                processes.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes


if __name__ == "__main__":
    start_time = time.time()
    while True:
        # 启动 Spotify
        if not get_running_process(r"^\bSpotify.exe\b$"):
            with subprocess.Popen(["powershell", str(Path.home() / "AppData" / "Roaming" / "Spotify" / "Spotify.exe")], creationflags=subprocess.CREATE_NO_WINDOW) as proc:
                proc.wait()

        # 使用正则表达式查找并关闭 Spotify 窗口
        spotify_windows_hwnd = find_windows_by_regex(r"^\bSpotify(?: Premium)?\b$")
        if len(spotify_windows_hwnd) == 1 and (hwnd := spotify_windows_hwnd[0]) != 0:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

        # 判断 Spotify 是否已经启动并且窗口已经关闭或者程序超时
        if len(spotify_windows_hwnd) == 1 and (hwnd := spotify_windows_hwnd[0]) != 0:
            if (get_running_process(r"^\bSpotify.exe\b$") and not win32gui.IsWindowVisible(hwnd)):
                break
        if time.time() - start_time >= 120:
            break

        time.sleep(1)
