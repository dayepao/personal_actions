# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'hash_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.1.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(373, 440)
        MainWindow.setAcceptDrops(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setEnabled(True)
        self.lineEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 2)

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 0, 2, 1, 1)

        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout.addWidget(self.pushButton_2, 1, 0, 1, 1)

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.gridLayout.addWidget(self.pushButton_3, 1, 2, 1, 1)

        self.checkBox = QCheckBox(self.centralwidget)
        self.checkBox.setObjectName(u"checkBox")

        self.gridLayout.addWidget(self.checkBox, 2, 0, 1, 1)

        self.lineEdit_2 = QLineEdit(self.centralwidget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_2, 2, 1, 1, 2)

        self.checkBox_2 = QCheckBox(self.centralwidget)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.gridLayout.addWidget(self.checkBox_2, 3, 0, 1, 1)

        self.lineEdit_3 = QLineEdit(self.centralwidget)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_3, 3, 1, 1, 2)

        self.checkBox_3 = QCheckBox(self.centralwidget)
        self.checkBox_3.setObjectName(u"checkBox_3")

        self.gridLayout.addWidget(self.checkBox_3, 4, 0, 1, 1)

        self.lineEdit_4 = QLineEdit(self.centralwidget)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        self.lineEdit_4.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_4, 4, 1, 1, 2)

        self.checkBox_4 = QCheckBox(self.centralwidget)
        self.checkBox_4.setObjectName(u"checkBox_4")

        self.gridLayout.addWidget(self.checkBox_4, 5, 0, 1, 1)

        self.lineEdit_5 = QLineEdit(self.centralwidget)
        self.lineEdit_5.setObjectName(u"lineEdit_5")
        self.lineEdit_5.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_5, 5, 1, 1, 2)

        self.checkBox_5 = QCheckBox(self.centralwidget)
        self.checkBox_5.setObjectName(u"checkBox_5")

        self.gridLayout.addWidget(self.checkBox_5, 6, 0, 1, 1)

        self.lineEdit_6 = QLineEdit(self.centralwidget)
        self.lineEdit_6.setObjectName(u"lineEdit_6")
        self.lineEdit_6.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_6, 6, 1, 1, 2)

        self.checkBox_6 = QCheckBox(self.centralwidget)
        self.checkBox_6.setObjectName(u"checkBox_6")

        self.gridLayout.addWidget(self.checkBox_6, 7, 0, 1, 1)

        self.lineEdit_7 = QLineEdit(self.centralwidget)
        self.lineEdit_7.setObjectName(u"lineEdit_7")
        self.lineEdit_7.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_7, 7, 1, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 373, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"hash_lyh", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u9009\u62e9\u6587\u4ef6", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\u6d4f\u89c8", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u8fd0\u884c", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"\u53d6\u6d88", None))
        self.checkBox.setText(QCoreApplication.translate("MainWindow", u"MD5", None))
        self.checkBox_2.setText(QCoreApplication.translate("MainWindow", u"SHA1", None))
        self.checkBox_3.setText(QCoreApplication.translate("MainWindow", u"SHA224", None))
        self.checkBox_4.setText(QCoreApplication.translate("MainWindow", u"SHA256", None))
        self.checkBox_5.setText(QCoreApplication.translate("MainWindow", u"SHA384", None))
        self.checkBox_6.setText(QCoreApplication.translate("MainWindow", u"SHA512", None))
    # retranslateUi

