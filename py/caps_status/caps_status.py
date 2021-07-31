import ctypes
import os
import sys
import time

from pykeyboard import PyKeyboard
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

# pip install pywin32
# pip install PyUserInput


class check_caps_status_work(QThread):
    signal = pyqtSignal(str)

    def CAPSLOCK_STATE(self):
        hllDll = ctypes.WinDLL("User32.dll")
        VK_CAPITAL = 0x14
        return hllDll.GetKeyState(VK_CAPITAL)

    def run(self):
        self.flag = 1
        while True:
            if self.flag == 0:
                return
            CAPSLOCK = self.CAPSLOCK_STATE()
            if ((CAPSLOCK) & 0xffff) != 0:
                self.signal.emit('caps')
            else:
                self.signal.emit('small')
            time.sleep(0.05)

    def stop(self):
        self.flag = 0


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.caps_ico = resource_path(os.path.join('ico', 'caps.ico'))
        self.small_ico = resource_path(os.path.join('ico', 'small.ico'))
        self.setIcon(QIcon(self.small_ico))
        self.showMenu()
        self.activated.connect(self.iconClied)
        self.check_caps_status()

    def showMenu(self):
        self.menu = QMenu()
        self.quitAction = QAction("退出", self, triggered=self.quit)

        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

    def check_caps_status(self):
        self.check_thread = check_caps_status_work()

        def set_icon(status):
            if status == 'caps':
                self.setIcon(QIcon(self.caps_ico))
                self.setToolTip('大写')
            else:
                self.setIcon(QIcon(self.small_ico))
                self.setToolTip('小写')
        self.check_thread.signal.connect(set_icon)
        self.check_thread.start()

    def iconClied(self, reason):
        "鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击"
        k = PyKeyboard()
        if reason.value in (2, 3):
            k.tap_key(k.caps_lock_key)

    def quit(self):
        self.setVisible(False)
        if 'check_thread' in dir(self):
            self.check_thread.stop()
        QApplication.quit()
        sys.exit()


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ti = TrayIcon()
    ti.show()
    sys.exit(app.exec())
