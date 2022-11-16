import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QKeyEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit

# apt install libegl1-mesa
# apt install libqt5gui5


class mainwindow(QMainWindow):
    def __init__(self, screen_num: int = 0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("resource_monitor by @dayepao")
        self.screen = QGuiApplication.screens()[screen_num]
        self.setGeometry(self.screen.geometry())  # 设置窗口大小为屏幕大小
        self.TextEdit = QTextEdit(self)
        self.TextEdit.setGeometry(self.screen.geometry())
        self.TextEdit.setReadOnly(True)

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Q:
                self.close()


if __name__ == '__main__':
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.Round)
    app = QApplication(sys.argv)
    ui = mainwindow(screen_num=0)
    ui.showFullScreen()
    sys.exit(app.exec())
