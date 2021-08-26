import json
import sys
from urllib import parse

import httpx
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow

import get_refresh_token_ui
import popup_ui


class para:
    url = "https://login.microsoftonline.com/common/oauth2/v2.0"
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }


class refresh_refresh_token_thread_work(QThread):
    signal = Signal()

    def run(self):
        postdata = {
            'grant_type': 'refresh_token',
            'refresh_token': para.refresh_token,
            'client_id': para.client_id,
            'client_secret': para.client_secret,
            'redirect_uri': para.redirect_uri
        }
        res = httpx.post(para.url + "/token", data=postdata, headers=para.headers)
        if res.status_code == 200:
            jsonstr = json.loads(res.text)
            para.result = json.dumps(jsonstr, sort_keys=False, indent=4, separators=(',', ':'))
        else:
            para.result = "错误"
        self.signal.emit()


class new_refresh_token_thread_work(QThread):
    signal = Signal()

    def run(self):
        postdata = {
            'grant_type': 'authorization_code',
            'code': para.code,
            'client_id': para.client_id,
            'client_secret': para.client_secret,
            'redirect_uri': para.redirect_uri
        }
        res = httpx.post(para.url + "/token", data=postdata, headers=para.headers)
        if res.status_code == 200:
            jsonstr = json.loads(res.text)
            para.result = json.dumps(jsonstr, sort_keys=False, indent=4, separators=(',', ':'))
        else:
            para.result = "错误"
        self.signal.emit()


class mainwindow(QMainWindow, get_refresh_token_ui.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.get_refresh_token)

    def get_refresh_token(self):
        self.textBrowser.setText("正在处理...")
        para.client_id = self.lineEdit.text()
        para.client_secret = self.lineEdit_2.text()
        if (para.client_id == '') or (para.client_secret == ''):
            self.textBrowser.setText("client_id和client_secret为必填项")
            return
        para.redirect_uri = self.lineEdit_3.text()
        if para.redirect_uri == '':
            para.redirect_uri = 'http://localhost'
        para.refresh_token = self.lineEdit_4.text()
        if para.refresh_token != '':
            self.refresh_refresh_token()
        else:
            self.new_refresh_token()

    def refresh_refresh_token(self):
        self.pushButton.setEnabled(False)
        thread = refresh_refresh_token_thread_work()

        def on_thread_finished():
            self.textBrowser.setText(str(para.result))
        thread.finished.connect(on_thread_finished)

        def set_pushButton():
            self.pushButton.setEnabled(True)
        thread.signal.connect(set_pushButton)
        thread.start()
        thread.exec()

    def new_refresh_token(self):
        para.url1 = para.url + "/authorize?client_id=" + para.client_id + "&scope=" + "Files.Read.All Files.ReadWrite.All offline_access" + "&response_type=" + "code" + "&redirect_uri=" + para.redirect_uri
        self.show_Dialog()
        if ('input_url' not in dir(para)) or (para.input_url == ''):
            self.textBrowser.setText("请输入重定向的地址")
            return
        params = parse.parse_qs(parse.urlparse(para.input_url).query)
        if 'code' not in params.keys():
            self.textBrowser.setText("重定向的地址中找不到参数\"code\"，请检查")
            return
        para.code = "".join(params['code'])
        self.pushButton.setEnabled(False)
        thread = new_refresh_token_thread_work()

        def on_thread_finished():
            self.textBrowser.setText(str(para.result))
        thread.finished.connect(on_thread_finished)

        def set_pushButton():
            self.pushButton.setEnabled(True)
        thread.signal.connect(set_pushButton)
        thread.start()
        thread.exec()

    def show_Dialog(self):
        ui2 = dialog()
        ui2.exec()


class dialog(QDialog, popup_ui.Ui_Dialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.textBrowser.setText(str(para.url1))
        self.buttonBox.accepted.connect(self.get_input_url)
        self.buttonBox.rejected.connect(self.del_input_url)

    def get_input_url(self):
        para.input_url = self.lineEdit.text()

    def del_input_url(self):
        if 'input_url' in dir(para):
            del para.input_url


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = mainwindow()
    ui.show()
    sys.exit(app.exec())
