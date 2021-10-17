import ctypes
import sys
from functools import partial

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout,
                               QHeaderView, QMainWindow, QPushButton, QWidget)

from ui import HyperV_controller_ui
import popup_vm
from HyperV_controller_ps import get_vms


class set_list_thread_work(QThread):
    signal_1 = Signal(dict)

    def __init__(self) -> None:
        super().__init__()

    def run(self):
        vms_dict = get_vms()
        self.signal_1.emit(vms_dict)


class mainwindow(QMainWindow, HyperV_controller_ui.Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        # 设置列宽
        self.tableWidget.horizontalHeader().setDefaultSectionSize(300)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tableWidget.setColumnWidth(2, 50)

        # 读取列表
        self.set_list("初始化")

        # 配置按钮函数&表格属性
        self.pushButton.clicked.connect(partial(self.set_list, "刷新"))
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # 美化
        self.tableWidget.setStyleSheet("QTableWidget {border: none; color: #000}")
        self.tableWidget_2.setStyleSheet("QTableWidget {border: none; color: #000}")

    def disable_button(self):
        '''禁用所有按键'''
        self.pushButton.setEnabled(False)

    def enable_button(self):
        '''启用所有按键'''
        self.pushButton.setEnabled(True)

    # 读取列表
    def set_list(self, work):
        self.disable_button()
        self.tableWidget.setRowCount(0)
        self.set_list_thread = set_list_thread_work()
        self.set_list_thread.start()
        self.lineEdit.setText("正在读取列表...")

        # 配置虚拟机表格行列数
        def set_list_item_vms(vms_dict: dict):
            i = 0
            for key, value in vms_dict.items():
                self.tableWidget.insertRow(i)
                j = 0
                for j in range(self.tableWidget.columnCount()):
                    item = QtWidgets.QTableWidgetItem()
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if j in (0, 1, 2):
                        item.setFlags(Qt.ItemFlag.ItemIsSelectable)
                    self.tableWidget.setItem(i, j, item)
                    j += 1
                set_item_data_vm(i, key, value)
                i += 1

        # 填充虚拟机表格内容
        def set_item_data_vm(i, vm_name, vm_state):
            # 显示虚拟机名称、状态
            self.tableWidget.item(i, 0).setText(vm_name)
            self.tableWidget.item(i, 1).setText(vm_state)
            if vm_state == "Off":
                self.tableWidget.item(i, 1).setBackground(QColor(0, 255, 0, 127))
            elif vm_state == "Running":
                self.tableWidget.item(i, 1).setBackground(QColor(255, 0, 0, 127))
            else:
                self.tableWidget.item(i, 1).setBackground(QColor(255, 255, 0, 127))

            # 显示选择按钮
            pushbutton = QPushButton()
            pushbutton.setObjectName("pushButton_1_{}".format(i))
            pushbutton.setText("选择")
            pushbutton.clicked.connect(partial(self.popup_vm, i))
            if vm_state == "Running":
                pushbutton.setEnabled(False)
            pushbutton.setCursor(Qt.CursorShape.PointingHandCursor)
            pushbutton.setStyleSheet("QPushButton {border: 50px solid transparent}")
            pushbutton_layout = QHBoxLayout()
            pushbutton_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pushbutton_layout.setContentsMargins(0, 0, 0, 0)
            pushbutton_layout.addWidget(pushbutton)
            pushbutton_widget = QWidget()
            pushbutton_widget.setLayout(pushbutton_layout)
            self.tableWidget.setCellWidget(i, 2, pushbutton_widget)

        self.set_list_thread.signal_1.connect(set_list_item_vms)
        self.set_list_thread.finished.connect(partial(self.notice, work))

    # 显示完成提示
    def notice(self, work):
        self.lineEdit.setText("{work} 已完成".format(work=work))
        self.enable_button()

    # 弹出虚拟机详细信息
    def popup_vm(self, i):
        vm_name = self.tableWidget.item(i, 0).text()
        ui_vm = popup_vm.dialog(vm_name)
        ui_vm.exec()
        self.set_list("刷新")


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
