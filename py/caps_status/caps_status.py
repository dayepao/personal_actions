import ctypes
import sys
from pathlib import Path

from pynput import keyboard
from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

# pip install pynput

# ~~pip install pywin32~~
# ~~pip install PyUserInput~~


class CapsLockChecker(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.caps_ico = str(get_resource_path(Path('ico', 'caps.ico')))
        self.small_ico = str(get_resource_path(Path('ico', 'small.ico')))
        self.setIcon(QIcon(self.small_ico))
        self.setToolTip('小写')
        self.showMenu()
        self.activated.connect(self.iconClied)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_caps_status)
        self.timer.start(50)

    def showMenu(self):
        self.menu = QMenu()
        self.quitAction = QAction("退出", self, triggered=self.quit)

        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

    def get_caps_status(self):
        return ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 0x01

    def check_caps_status(self):
        if self.get_caps_status():
            self.setIcon(QIcon(self.caps_ico))
            self.setToolTip('大写')
        else:
            self.setIcon(QIcon(self.small_ico))
            self.setToolTip('小写')

    def iconClied(self, reason):
        k = keyboard.Controller()
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            k.press(keyboard.Key.caps_lock)
            k.release(keyboard.Key.caps_lock)

    def quit(self):
        self.setVisible(False)
        QApplication.quit()
        sys.exit()


def get_resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)
    return Path(base_path, relative_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    caps_lock_checker = CapsLockChecker()
    caps_lock_checker.show()
    sys.exit(app.exec())
