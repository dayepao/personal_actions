import sys
import time

from PySide6.QtCore import QEvent, QObject, QThread, Signal
from PySide6.QtGui import QColor, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFileDialog,
                               QHeaderView, QLineEdit, QMainWindow,
                               QTableWidget, QTableWidgetItem, QToolTip)

import watermark_ui


class add_watermark_thread_work(QThread):
    signal = Signal(tuple)

    def __init__(self, supported_files: list[tuple], parent: None = None) -> None:
        super().__init__(parent=parent)
        self.supported_files = supported_files

    def get_file_list(self):
        pass

    def run(self):
        print(self.supported_files)
        time.sleep(5)
        print(1)


class mainwindow(QMainWindow, watermark_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.tableWidget: QTableWidget
        self.lineEdit: QLineEdit

        # 设置列宽和表格属性
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidget.installEventFilter(self)
        self.tableWidget.itemClicked.connect(self.click_item_slot)
        self.tableWidget.itemEntered.connect(self.enter_item_slot)
        self.tooltip = (time.time(), None)

        # 设置文本框属性和事件处理
        self.lineEdit.setText("拖入文件")
        self.lineEdit.installEventFilter(self)

        # 设置按键事件
        self.pushButton.clicked.connect(self.open_file)
        self.pushButton_2.clicked.connect(self.add_watermark)

    def click_item_slot(self, item: QTableWidgetItem):
        # 点击表格项目
        self.tooltip = (time.time(), item.text())

    def enter_item_slot(self, item: QTableWidgetItem):
        # 鼠标移入表格项目
        self.tooltip = (time.time(), item.text())

    def eventFilter(self, obj: QObject, event: QEvent):
        # 关于lineEdit的事件处理
        if obj.objectName() == "lineEdit":
            if event.type() == QEvent.DragEnter:
                self.lineEdit_dragEnterEvent(event)
                return True
            if event.type() == QEvent.Drop:
                self.lineEdit_dropEvent(event)
                return True
        # 关于tableWidget的事件处理
        if obj.objectName() == "tableWidget":
            if (event.type() == QEvent.ToolTip) and (self.tooltip[1] is not None) and (time.time() - self.tooltip[0] > 1):
                QToolTip.showText(event.globalPos(), self.tooltip[1])
                self.tooltip = (time.time(), None)
                return True
        return QObject.eventFilter(self, obj, event)

    def lineEdit_dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def lineEdit_dropEvent(self, event: QDropEvent):
        # 拖入文件
        file_urls = []
        for file_qurl in event.mimeData().urls():
            file_urls.append(file_qurl.toLocalFile())
        self.set_tableWidget(file_urls)

    def open_file(self):
        # 打开文件
        self.set_tableWidget(QFileDialog.getOpenFileNames()[0])

    def clear_tableWidget(self):
        # 清空表格
        i = 0
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(0)
            i += 1

    def set_tableWidget(self, file_urls):
        # 设置表格内容
        self.clear_tableWidget()
        self.supported_files = []
        i = 0
        for file_url in file_urls:
            self.tableWidget.insertRow(i)
            if self.file_extension_check(file_url):
                self.tableWidget.setItem(i, 0, QTableWidgetItem("待处理"))
                self.tableWidget.item(i, 0).setBackground(QColor(0, 0, 255, 100))
                self.supported_files.append((i, file_url))
            else:
                self.tableWidget.setItem(i, 0, QTableWidgetItem("不支持"))
                self.tableWidget.item(i, 0).setBackground(QColor(255, 0, 0, 127))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(file_url))
            i += 1
        self.lineEdit.setText("输入水印内容后点击处理")

    def file_extension_check(self, file_url):
        # 检查文件后缀是否支持
        supported_file_types = ["png", "jpg", "jpeg", "pdf"]
        file_extension = file_url.split(".")[-1]
        if file_extension not in supported_file_types:
            return False
        return True

    def disable_ui(self):
        # 禁止控件
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.lineEdit.setAcceptDrops(False)
        self.lineEdit_2.setAcceptDrops(False)

    def enable_ui(self):
        # 启用控件
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        self.lineEdit.setAcceptDrops(True)
        self.lineEdit_2.setAcceptDrops(True)

    def add_watermark(self):
        # 处理文件
        self.disable_ui()
        self.add_watermark_thread = add_watermark_thread_work(self.supported_files)
        self.lineEdit.setText("正在处理...")
        self.add_watermark_thread.start()

        def on_thread_finished():
            self.lineEdit.setText("处理完成")
            self.enable_ui()

        self.add_watermark_thread.finished.connect(on_thread_finished)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = mainwindow()
    ui.show()
    sys.exit(app.exec())
