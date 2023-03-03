import hashlib
import os
import sys
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, QThread, Signal
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow

import hash_ui
import new_method


class get_file_hash_thread_work(QThread):
    signal1 = Signal(str, str)  # 当前hash类型及hash结果
    signal2 = Signal(str, str)  # 当前hash类型及进度

    def __init__(self, filename: str, hash_task: list[str], parent=None) -> None:
        super().__init__(parent=parent)
        self.filename = filename
        self.hash_task = hash_task

    def run(self):
        self.flag = 1
        for key in self.hash_task:
            hashstr = hashlib.new(key)
            size = Path(self.filename).stat().st_size
            hashed = 0
            with open(self.filename, 'rb') as fileobj:
                while (tempdata := fileobj.read(40960)) != b"":
                    if self.flag == 0:
                        return
                    hashstr.update(tempdata)
                    hashed = hashed + 40960
                    rate = round(float(hashed)*100/size, 1)
                    rate = min(rate, 100)
                    rate = str(rate) + "%"
                    self.signal2.emit(key, rate)
            self.signal1.emit(key, str(hashstr.hexdigest()))

    def stop(self):
        self.flag = 0


class mainwindow(QMainWindow, hash_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.open_file)
        self.pushButton_2.clicked.connect(self.check)
        self.pushButton_3.clicked.connect(self.stop_work)
        self.lineEdit.installEventFilter(self)
        self.filename = ""
        self.hash_task = []

    def eventFilter(self, obj: QObject, event: QEvent):
        if obj.objectName() == "lineEdit":
            if event.type() == QEvent.DragEnter:
                new_method.lineEdit_dragEnterEvent(event)
                return True
            if event.type() == QEvent.Drop:
                new_method.lineEdit_dropEvent(self, event)
                return True
        return QObject.eventFilter(self, obj, event)

    def stop_work(self):
        if 'hash_thread' in dir(self):
            self.hash_thread.stop()

    def clear_lineEdit(self):
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.lineEdit_5.clear()
        self.lineEdit_6.clear()
        self.lineEdit_7.clear()

    def open_file(self):
        self.clear_lineEdit()
        self.filename = QFileDialog.getOpenFileName()[0]
        self.lineEdit.setText(str(self.filename))

    def check(self):
        self.clear_lineEdit()
        self.hash_task.clear()
        if self.filename == "":
            self.lineEdit.setText('还没有选择文件')
            return
        if self.checkBox.isChecked():
            self.lineEdit_2.setText('等待中...')
            self.hash_task.append("md5")
        if self.checkBox_2.isChecked():
            self.lineEdit_3.setText('等待中...')
            self.hash_task.append("sha1")
        if self.checkBox_3.isChecked():
            self.lineEdit_4.setText('等待中...')
            self.hash_task.append("sha224")
        if self.checkBox_4.isChecked():
            self.lineEdit_5.setText('等待中...')
            self.hash_task.append("sha256")
        if self.checkBox_5.isChecked():
            self.lineEdit_6.setText('等待中...')
            self.hash_task.append("sha384")
        if self.checkBox_6.isChecked():
            self.lineEdit_7.setText('等待中...')
            self.hash_task.append("sha512")
        self.get_file_hash()

    def disable_all(self):
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.checkBox.setEnabled(False)
        self.checkBox_2.setEnabled(False)
        self.checkBox_3.setEnabled(False)
        self.checkBox_4.setEnabled(False)
        self.checkBox_5.setEnabled(False)
        self.checkBox_6.setEnabled(False)

    def enable_all(self):
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        self.checkBox.setEnabled(True)
        self.checkBox_2.setEnabled(True)
        self.checkBox_3.setEnabled(True)
        self.checkBox_4.setEnabled(True)
        self.checkBox_5.setEnabled(True)
        self.checkBox_6.setEnabled(True)

    def get_file_hash(self):
        self.disable_all()
        self.hash_thread = get_file_hash_thread_work(self.filename, self.hash_task)

        def on_thread_finished():
            self.enable_all()
        self.hash_thread.finished.connect(on_thread_finished)

        def set_lineEdit_num(key):
            if key == 'md5':
                lineEdit_num = self.lineEdit_2
            if key == 'sha1':
                lineEdit_num = self.lineEdit_3
            if key == 'sha224':
                lineEdit_num = self.lineEdit_4
            if key == 'sha256':
                lineEdit_num = self.lineEdit_5
            if key == 'sha384':
                lineEdit_num = self.lineEdit_6
            if key == 'sha512':
                lineEdit_num = self.lineEdit_7
            return lineEdit_num

        def show_hashstr(key, hash_value):
            lineEdit_num = set_lineEdit_num(key)
            lineEdit_num.setText(hash_value)
        self.hash_thread.signal1.connect(show_hashstr)

        def set_rate(key, rate):
            lineEdit_num = set_lineEdit_num(key)
            lineEdit_num.setText('正在处理...' + rate)
        self.hash_thread.signal2.connect(set_rate)
        self.hash_thread.start()
        self.hash_thread.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = mainwindow()
    ui.show()
    sys.exit(app.exec())
