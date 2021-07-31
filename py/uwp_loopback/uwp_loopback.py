import ctypes
import os
import sys
import time
from functools import partial

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QHeaderView,
                             QMainWindow, QWidget)

import uwp_loopback_ui
from get_uwp_list import get_uwp_list

# pyinstall --uac-admin


class handle_loopback_thread_work(QThread):
    signal = pyqtSignal(str)  # 必须放在__init__外

    def __init__(self, work, parent: None = None) -> None:
        super().__init__(parent=parent)
        self.work = work

    def run(self):
        checked_uwp_sids = ui.get_checked_uwp_sid()
        key = 0
        if self.work == 'Enable':
            main = 'powershell CheckNetIsolation LoopbackExempt -a -p='
        elif self.work == 'Disable':
            main = 'powershell CheckNetIsolation LoopbackExempt -d -p='
        elif self.work == 'Disable All':
            os.popen('powershell CheckNetIsolation LoopbackExempt -c')
            return
        else:
            return
        for checked_uwp_sid in checked_uwp_sids:
            os.popen(main + checked_uwp_sid)
            key = key + 1
            rate = key/len(checked_uwp_sids)
            rate = min(rate*100, 100)
            rate = round(rate, 1)
            rate = str(rate) + "%"
            self.signal.emit(rate)
            time.sleep(0.2)


class mainwindow(QMainWindow, uwp_loopback_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        # 设置列宽
        self.tableWidget.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tableWidget.setColumnWidth(0, 10)

        # 显示全选框
        self.set_header_check_box()

        # 显示uwp列表
        self.set_list()

        self.pushButton.clicked.connect(partial(self.handle_loopback, 'Enable'))
        self.pushButton_2.clicked.connect(partial(self.handle_loopback, 'Disable'))
        self.pushButton_3.clicked.connect(partial(self.handle_loopback, 'Disable All'))
        self.tableWidget.horizontalHeader().sectionClicked.connect(self.header_check_box_clicked)

    def set_header_check_box(self):
        self.checked_img = resource_path(os.path.join('img', 'checked.png'))
        self.unchecked_img = resource_path(os.path.join('img', 'unchecked.png'))
        # self.tableWidget.horizontalHeaderItem(0).setIcon(QIcon(QPixmap(self.checked_img)))
        # self.checked_cachekey = self.tableWidget.horizontalHeaderItem(0).icon().cacheKey()
        self.tableWidget.horizontalHeaderItem(0).setIcon(QIcon(QPixmap(self.unchecked_img)))
        self.unchecked_cachekey = self.tableWidget.horizontalHeaderItem(0).icon().cacheKey()

    def set_list(self):
        uwp_list = get_uwp_list()
        i = 0
        for DisplayName, name, sid in uwp_list:
            self.tableWidget.insertRow(i)
            j = 0
            for j in range(self.tableWidget.columnCount()):
                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(Qt.ItemFlag.ItemIsEditable)
                # item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable) # 使flag生效
                self.tableWidget.setItem(i, j, item)
                j += 1
            self.set_item_data(i, DisplayName, name, sid)
            i += 1

    def on_thread_start(self):
        '''子线程开始前禁用所有按键'''
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)

    def set_rate(self, rate):
        self.lineEdit.setText('正在处理' + rate)

    def on_thread_finished(self, work):
        '''子线程结束后启用所有按键'''
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        self.lineEdit.setText(work + '操作 已完成')

    def handle_loopback(self, work: str = ''):
        '''与pushButton (Enable/Disable/Disable All)连接'''
        self.on_thread_start()

        if work not in ('Enable', 'Disable', 'Disable All'):
            return

        self.handle_loopback_thread = handle_loopback_thread_work(work)
        self.handle_loopback_thread.finished.connect(partial(self.on_thread_finished, work))

        self.handle_loopback_thread.signal.connect(self.set_rate)

        self.handle_loopback_thread.start()
        self.handle_loopback_thread.exec()

    def get_checked_uwp_sid(self):
        i = 0
        checked_uwp_sid = []
        for i in range(self.tableWidget.rowCount()):
            if self.tableWidget.cellWidget(i, 0).findChild(QCheckBox, 'check_box_' + str(i)).isChecked():
                checked_uwp_sid.append(str(self.tableWidget.item(i, 3).data(Qt.ItemDataRole.DisplayRole)))
            i += 1
        return checked_uwp_sid

    def header_check_box_clicked(self, col):
        '''由表头中的全选框触发'''
        if col == 0:
            if self.tableWidget.horizontalHeaderItem(0).icon().cacheKey() == self.unchecked_cachekey:
                self.tableWidget.horizontalHeaderItem(0).setIcon(QIcon(QPixmap(self.checked_img)))
                self.select_all()
            else:
                self.tableWidget.horizontalHeaderItem(0).setIcon(QIcon(QPixmap(self.unchecked_img)))
                self.unchecked_cachekey = self.tableWidget.horizontalHeaderItem(0).icon().cacheKey()
                # unchecked_cachekey会变化
                self.unselect_all()

    def select_all(self):
        i = 0
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.cellWidget(i, 0).findChild(QCheckBox, 'check_box_' + str(i)).setCheckState(Qt.CheckState.Checked)
            i += 1

    def unselect_all(self):
        i = 0
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.cellWidget(i, 0).findChild(QCheckBox, 'check_box_' + str(i)).setCheckState(Qt.CheckState.Unchecked)
            i += 1

    def set_item_data(self, i, DisplayName, name, sid):
        check_box_layout = QHBoxLayout()
        check_box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        check_box = QCheckBox()
        check_box.setObjectName('check_box_' + str(i))
        check_box_layout.addWidget(check_box)
        check_box_layout.setContentsMargins(0, 0, 0, 0)
        check_box_widget = QWidget()
        check_box_widget.setLayout(check_box_layout)
        self.tableWidget.item(i, 1).setText(DisplayName)
        self.tableWidget.item(i, 2).setText(name)
        self.tableWidget.item(i, 3).setText(sid)
        self.tableWidget.setCellWidget(i, 0, check_box_widget)


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


if __name__ == '__main__':
    if is_admin():
        app = QApplication(sys.argv)
        ui = mainwindow()
        ui.show()
        sys.exit(app.exec())
    else:
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        # else:  # in python2.x
            # ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(__file__), None, 1)
