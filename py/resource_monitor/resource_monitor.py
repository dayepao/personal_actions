import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication, QKeyEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit
from sub_thread import resource_monitor

# pip install PySide6
# pip install psutil


# apt install libegl1-mesa
# apt install libqt5gui5
# export DISPLAY=:0


class mainwindow(QMainWindow):
    def __init__(self, screen_num: int = 0, parent=None):
        super().__init__(parent)
        # self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)  # 设置窗口置顶
        self.setWindowTitle("resource_monitor by @dayepao")
        try:
            self.screen = QGuiApplication.screens()[screen_num]
        except IndexError as e:
            print(e)
            self.screen = QGuiApplication.primaryScreen()
        self.setGeometry(self.screen.geometry())  # 设置窗口大小为屏幕大小
        self.TextEdit = QTextEdit(self)
        self.TextEdit.setGeometry(0, 0, self.geometry().width()/3, self.geometry().height()/3)
        self.TextEdit.setReadOnly(True)
        self.run()

    def run(self):
        self.resource_monitor_thread = resource_monitor()

        def on_thread_finished():
            self.TextEdit.setText("监控主线程已停止，正在尝试重启...")
            timer = QTimer()
            timer.singleShot(3000, self.resource_monitor_thread.start)
        self.resource_monitor_thread.finished.connect(on_thread_finished)

        def update_ui(resource: dict):
            self.TextEdit.setText(self.get_system_utilization_text(resource))
        self.resource_monitor_thread.signal.connect(update_ui)

        self.resource_monitor_thread.start()

    def stop(self):
        if 'resource_monitor_thread' in dir(self):
            self.resource_monitor_thread.quit()
            self.resource_monitor_thread.wait()
        self.close()

    def get_system_utilization_text(self, resource: dict):
        if type(resource["system_utilization"]) == str:
            system_utilization_text = resource["system_utilization"]
        else:
            system_utilization_text = ""
            system_utilization_text += "cpu_utilization: {}%\n".format(resource["system_utilization"]['cpu_utilization'])
            system_utilization_text += "per_cpu_utilization: {}\n".format(resource["system_utilization"]['per_cpu_utilization'])
            system_utilization_text += "cpu_freq: {}\n".format(resource["system_utilization"]['cpu_freq'])
            system_utilization_text += "per_cpu_freq: {}\n".format(resource["system_utilization"]['per_cpu_freq'])
            system_utilization_text += "memory_utilization: {}%\n".format(resource["system_utilization"]['memory_utilization'])
        return system_utilization_text

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Q:
                self.stop()
            # if event.key() == Qt.Key.Key_L:
            #     self.resource_monitor_thread.get_system_utilization_thread.quit()
                # self.resource_monitor_thread.quit()


if __name__ == '__main__':
    screen_num = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.Round)
    app = QApplication(sys.argv)
    ui = mainwindow(screen_num)
    ui.showFullScreen()
    sys.exit(app.exec())
