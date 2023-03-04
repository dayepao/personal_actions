import ctypes
import subprocess
import sys
from functools import partial
from pathlib import Path

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox,
                               QHBoxLayout, QHeaderView, QMainWindow, QWidget)

import uwp_loopback_ui
from get_uwp_list import get_enabled_sid_list, get_uwp_list

# pyinstaller --uac-admin


class handle_loopback_thread_work(QThread):
    signal = Signal(str)  # 必须放在__init__外

    def __init__(self, work, parent: None = None) -> None:
        super().__init__(parent=parent)
        self.work = work

    def get_rate(self, key, key_all) -> str:
        rate = key/key_all
        rate = min(rate*100, 100.0)
        rate = round(rate, 1)
        rate = str(rate) + "%"
        return rate

    def set_checked_uwp_sids_ps(self) -> tuple[str, int]:
        checked_uwp_sids = ui.get_checked_uwp_sid()
        key_all = len(checked_uwp_sids)
        checked_uwp_sids_ps = "@("
        for checked_uwp_sid in checked_uwp_sids:
            checked_uwp_sids_ps = checked_uwp_sids_ps + "\"" + checked_uwp_sid + "\","
        if checked_uwp_sids_ps == "@(":
            checked_uwp_sids_ps = checked_uwp_sids_ps + ")"
        else:
            checked_uwp_sids_ps = checked_uwp_sids_ps[:-1] + ")"
        return checked_uwp_sids_ps, key_all

    def handle_Enable_or_Disable(self, ps, key_all):
        key = 0
        self.signal.emit('0.0%')
        with subprocess.Popen(['powershell', ps], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
            # while True:
            while proc.stdout.readline() != b'':
                # if proc.stdout.readline():
                key = key + 1
                rate = self.get_rate(key, key_all)
                self.signal.emit(rate)
                # else:
                # break

    def handle_Disable_All(self):
        self.signal.emit('0.0%')
        cmd = 'CheckNetIsolation LoopbackExempt -c'
        with subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
            proc.stdout.readlines()

    def run(self):
        checked_uwp_sids_ps, key_all = self.set_checked_uwp_sids_ps()

        if self.work == 'Enable':
            ps = '$checked_uwp_sids=' + checked_uwp_sids_ps + ' ; foreach ($checked_uwp_sid in $checked_uwp_sids) {CheckNetIsolation LoopbackExempt -a -p="$checked_uwp_sid"}'
            self.handle_Enable_or_Disable(ps, key_all)
        elif self.work == 'Disable':
            ps = '$checked_uwp_sids=' + checked_uwp_sids_ps + ' ; foreach ($checked_uwp_sid in $checked_uwp_sids) {CheckNetIsolation LoopbackExempt -d -p="$checked_uwp_sid"}'
            self.handle_Enable_or_Disable(ps, key_all)
        elif self.work == 'Disable All':
            self.handle_Disable_All()


class set_status_thread_work(QThread):
    def __init__(self, parent: None = None) -> None:
        super().__init__(parent=parent)

    def run(self):
        enabled_sid_list = get_enabled_sid_list()
        for i in range(ui.tableWidget.rowCount()):
            status = '未解锁'
            if str(ui.tableWidget.item(i, 4).data(Qt.ItemDataRole.DisplayRole)) in enabled_sid_list:
                status = '已解锁'
            ui.tableWidget.item(i, 1).setText(status)

            if status == '已解锁':
                ui.tableWidget.item(i, 1).setBackground(QColor(0, 255, 0, 127))
            else:
                ui.tableWidget.item(i, 1).setBackground(QColor(255, 0, 0, 127))


class set_list_thread_work(QThread):
    signal = Signal(list)

    def __init__(self, parent: None = None) -> None:
        super().__init__(parent=parent)

    def run(self):
        uwp_list = get_uwp_list()
        self.signal.emit(uwp_list)


class mainwindow(QMainWindow, uwp_loopback_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # 禁用按键
        self.disable_button()

        # 设置列宽
        self.tableWidget.horizontalHeader().setDefaultSectionSize(300)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tableWidget.setColumnWidth(0, 10)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tableWidget.setColumnWidth(1, 50)

        # 显示全选框
        self.set_header_check_box()

        # 配置按键函数&表格属性
        self.pushButton.clicked.connect(partial(self.handle_loopback, 'Enable'))
        self.pushButton_2.clicked.connect(partial(self.handle_loopback, 'Disable'))
        self.pushButton_3.clicked.connect(partial(self.handle_loopback, 'Disable All'))
        self.pushButton_4.clicked.connect(self.refresh)
        self.tableWidget.horizontalHeader().sectionClicked.connect(self.header_check_box_clicked)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # 显示uwp列表
        self.set_list('初始化')

    def set_header_check_box(self):
        self.checked_img = get_resource_path(Path('img', 'checked.png'))
        self.unchecked_img = get_resource_path(Path('img', 'unchecked.png'))
        # self.tableWidget.horizontalHeaderItem(0).setIcon(QIcon(QPixmap(self.checked_img)))
        # self.checked_cachekey = self.tableWidget.horizontalHeaderItem(0).icon().cacheKey()
        self.tableWidget.horizontalHeaderItem(0).setIcon(QIcon(QPixmap(self.unchecked_img)))
        self.unchecked_cachekey = self.tableWidget.horizontalHeaderItem(0).icon().cacheKey()

    def set_list(self, work):
        self.set_list_thread = set_list_thread_work(self)
        self.set_list_thread.start()
        self.lineEdit.setText('正在读取列表...')

        def set_list_integral(uwp_list):
            i = 0
            for DisplayName, name, sid in uwp_list:
                self.tableWidget.insertRow(i)
                j = 0
                for j in range(self.tableWidget.columnCount()):
                    item = QtWidgets.QTableWidgetItem()
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    # item.setFlags(Qt.ItemFlag.ItemIsEditable)
                    # item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable) # 使flag生效
                    self.tableWidget.setItem(i, j, item)
                    j += 1
                self.set_item_data(i, DisplayName, name, sid)
                i += 1
            self.set_status(work)
        self.set_list_thread.signal.connect(set_list_integral)

    def set_status(self, work):
        self.set_status_thread = set_status_thread_work()
        self.set_status_thread.start()
        self.lineEdit.setText('正在刷新状态...')

        def on_thread_finished():
            self.enable_button()
            self.tableWidget.horizontalHeaderItem(0).setIcon(QIcon(QPixmap(self.unchecked_img)))
            self.unchecked_cachekey = self.tableWidget.horizontalHeaderItem(0).icon().cacheKey()
            self.unselect_all()
            self.lineEdit.setText(work + '操作 已完成')
        self.set_status_thread.finished.connect(on_thread_finished)

    def disable_button(self):
        '''子线程开始前禁用所有按键'''
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(False)

    def enable_button(self):
        '''子线程结束后启用所有按键'''
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        self.pushButton_4.setEnabled(True)

    def set_rate(self, rate):
        self.lineEdit.setText('正在处理...' + rate)

    def refresh(self):
        self.disable_button()
        i = 0
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(0)
            i += 1
        self.set_list('Refresh')

    def handle_loopback(self, work: str = ''):
        '''与pushButton (Enable/Disable/Disable All)连接'''
        self.disable_button()

        if work not in ('Enable', 'Disable', 'Disable All'):
            return

        self.handle_loopback_thread = handle_loopback_thread_work(work)

        # handle子线程结束后刷新状态
        self.handle_loopback_thread.finished.connect(partial(self.set_status, work))

        self.handle_loopback_thread.signal.connect(self.set_rate)

        self.handle_loopback_thread.start()
        self.handle_loopback_thread.exec()

    def get_checked_uwp_sid(self) -> list[str]:
        i = 0
        checked_uwp_sid = []
        for i in range(self.tableWidget.rowCount()):
            if self.tableWidget.cellWidget(i, 0).findChild(QCheckBox, 'check_box_' + str(i)).isChecked():
                checked_uwp_sid.append(str(self.tableWidget.item(i, 4).data(Qt.ItemDataRole.DisplayRole)))
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
        self.tableWidget.item(i, 2).setText(DisplayName)
        self.tableWidget.item(i, 3).setText(name)
        self.tableWidget.item(i, 4).setText(sid)
        self.tableWidget.setCellWidget(i, 0, check_box_widget)


def get_resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)
    return Path(base_path, relative_path)


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
