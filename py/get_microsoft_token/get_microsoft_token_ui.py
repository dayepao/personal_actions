# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'get_microsoft_token_ui.ui'
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
        MainWindow.resize(734, 666)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.lineEdit_2 = QLineEdit(self.centralwidget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)

        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 6, 0, 1, 1)

        self.textBrowser = QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName(u"textBrowser")

        self.gridLayout.addWidget(self.textBrowser, 7, 0, 1, 2)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 5, 0, 1, 2)

        self.lineEdit_3 = QLineEdit(self.centralwidget)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setStyleSheet(u"")
        self.lineEdit_3.setClearButtonEnabled(False)

        self.gridLayout.addWidget(self.lineEdit_3, 2, 1, 1, 1)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_2 = QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_4 = QLabel(self.tab)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 3)

        self.lineEdit_4 = QLineEdit(self.tab)
        self.lineEdit_4.setObjectName(u"lineEdit_4")

        self.gridLayout_2.addWidget(self.lineEdit_4, 4, 0, 2, 4)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout_3 = QGridLayout(self.tab_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_6 = QLabel(self.tab_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_3.addWidget(self.label_6, 1, 0, 1, 1)

        self.lineEdit_5 = QLineEdit(self.tab_2)
        self.lineEdit_5.setObjectName(u"lineEdit_5")

        self.gridLayout_3.addWidget(self.lineEdit_5, 2, 0, 1, 2)

        self.checkBox = QCheckBox(self.tab_2)
        self.checkBox.setObjectName(u"checkBox")

        self.gridLayout_3.addWidget(self.checkBox, 3, 0, 1, 1)

        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout.addWidget(self.tabWidget, 3, 0, 2, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 734, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"get_microsoft_token", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165client_id\uff08\u5fc5\u586b\uff09:", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u8fd0\u884c\u7ed3\u679c\uff1a", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165redirect_uri\uff08\u9009\u586b\uff09:", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\u8fd0\u884c", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_3.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.lineEdit_3.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.lineEdit_3.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.lineEdit_3.setInputMask("")
        self.lineEdit_3.setText("")
        self.lineEdit_3.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u9ed8\u8ba4\u4e3a http://localhost", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165client_secret\uff08\u5fc5\u586b\uff09:", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165refresh_token\uff08\u9009\u586b\uff09:", None))
        self.lineEdit_4.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Microsoft \u6807\u8bc6\u5e73\u53f0\u7ec8\u7ed3\u70b9", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u79df\u6237 ID\uff08\u5fc5\u586b\uff09:", None))
        self.checkBox.setText(QCoreApplication.translate("MainWindow", u"\u6b64\u5e94\u7528\u5df2\u7ecf\u8fdb\u884c\u8fc7\u7ba1\u7406\u5458\u8bb8\u53ef\u7ec8\u7ed3\u70b9\u6388\u6743", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Microsoft \u6807\u8bc6\u5e73\u53f0\u7ba1\u7406\u5458\u8bb8\u53ef\u7ec8\u7ed3\u70b9", None))
    # retranslateUi

