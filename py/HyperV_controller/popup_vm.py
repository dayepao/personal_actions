import sys
from functools import partial

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog,
                               QHBoxLayout, QHeaderView, QLineEdit, QWidget)

from ui import popup_vm_ui
from HyperV_controller_ps import get_vmprocessor, set_vmprocessor


class set_fun_thread_work(QThread):
    signal = Signal(list)

    def __init__(self, vm_name: str, vmprocessor_changes: dict) -> None:
        super().__init__()
        self.vm_name = vm_name
        self.vmprocessor_changes = vmprocessor_changes

    def run(self):
        err = []
        result = set_vmprocessor(self.vm_name, self.vmprocessor_changes)
        if not result[0]:
            err.extend(result[1])
        self.signal.emit(err)


class set_list_thread_work(QThread):
    signal = Signal(dict)

    def __init__(self, vm_name) -> None:
        super().__init__()
        self.vm_name = vm_name

    def run(self):
        fun_dict = {}
        fun_dict.update(get_vmprocessor(self.vm_name))
        self.signal.emit(fun_dict)


class dialog(QDialog, popup_vm_ui.Ui_Dialog):
    def __init__(self, vm_name) -> None:
        super().__init__()
        self.vm_name = vm_name
        self.setupUi(self)
        self.setWindowTitle(self.vm_name)
        # 功能对应说明
        self.fun_explain = {
            "Count": "虚拟处理器数量",
            "ExposeVirtualizationExtensions": "嵌套虚拟化",
        }

        # 可修改功能列表
        self.fun_modifiable = {
            "Count": "VMProcessor",
            "ExposeVirtualizationExtensions": "VMProcessor",
        }

        # 设置列宽
        self.tableWidget.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # 读取列表
        self.set_list("初始化")

        # 配置按钮函数&表格属性
        self.pushButton.clicked.connect(partial(self.set_list, "刷新"))
        self.pushButton_2.clicked.connect(self.process_changes)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # 美化
        self.tableWidget.setStyleSheet("QTableWidget {border: none; color: #000}")

    # 处理更改
    def process_changes(self):
        vmprocessor_changes = {}
        for lineedit in self.lineedit_list:
            if change := lineedit.text():
                i = int(lineedit.objectName().replace("lineEdit_1_", ""))
                if self.fun_modifiable[(fun := self.tableWidget.item(i, 0).text())] == "VMProcessor":
                    vmprocessor_changes[fun] = change

        self.disable_button()
        self.set_fun_thread = set_fun_thread_work(vm_name=self.vm_name, vmprocessor_changes=vmprocessor_changes)
        self.set_fun_thread.start()
        self.textEdit.setText("{vm_name}: 正在修改...".format(vm_name=self.vm_name))
        self.set_fun_thread.signal.connect(partial(self.set_list, "修改"))

    def disable_button(self):
        '''禁用所有按键'''
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)

    def enable_button(self):
        '''启用所有按键'''
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(True)

    def set_list(self, work: str, err: list = None):
        self.disable_button()
        self.tableWidget.setRowCount(0)
        self.lineedit_list: list[QLineEdit] = []
        self.set_list_thread = set_list_thread_work(self.vm_name)
        self.set_list_thread.start()
        self.textEdit.setText("{vm_name}: 正在读取列表...".format(vm_name=self.vm_name))

        # 配置虚拟机表格行列数
        def set_list_item(fun_dict: dict):
            i = 0
            for key, value in fun_dict.items():
                self.tableWidget.insertRow(i)
                j = 0
                for j in range(self.tableWidget.columnCount()):
                    item = QtWidgets.QTableWidgetItem()
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if j in (0, 1, 2, 3):
                        item.setFlags(Qt.ItemFlag.ItemIsSelectable)
                    self.tableWidget.setItem(i, j, item)
                    j += 1
                set_item_data(i, key, value)
                i += 1

        # 填充虚拟机表格内容
        def set_item_data(i, fun_name, fun_content):
            # 显示虚拟机名称、状态
            self.tableWidget.item(i, 0).setText(fun_name)
            if fun_name in self.fun_explain:
                self.tableWidget.item(i, 1).setText(self.fun_explain[fun_name])
            self.tableWidget.item(i, 2).setText(fun_content)

            # 显示修改框
            if fun_name in self.fun_modifiable:
                lineedit = QLineEdit()
                lineedit.setObjectName("lineEdit_1_{}".format(i))
                lineedit.setPlaceholderText("请输入修改值")
                lineedit.setStyleSheet("QLineEdit {border: none;}")
                self.lineedit_list.append(lineedit)  # 存储lineedit
                lineedit_layout = QHBoxLayout()
                lineedit_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lineedit_layout.setContentsMargins(0, 0, 0, 0)
                lineedit_layout.addWidget(lineedit)
                lineedit_widget = QWidget()
                lineedit_widget.setLayout(lineedit_layout)
                self.tableWidget.setCellWidget(i, 3, lineedit_widget)

        self.set_list_thread.signal.connect(set_list_item)
        self.set_list_thread.finished.connect(partial(self.notice, work, err))

    # 显示完成提示
    def notice(self, work: str, err: list = None):
        self.textEdit.setText("{vm_name}: {work} 已完成\n{err}".format(vm_name=self.vm_name, work=work, err="\n".join(err) if err else ""))
        self.enable_button()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = dialog("杂项")
    ui.show()
    sys.exit(app.exec())
