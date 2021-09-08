import json
import sys
from urllib import parse

import httpx
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow

import get_microsoft_token_ui
import popup_ui


class para:
    url = "https://login.microsoftonline.com/common/oauth2/v2.0"
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }


class refresh_refresh_token_thread_work(QThread):
    signal = Signal(str)

    def run(self):
        result = ""
        postdata = {
            'grant_type': 'refresh_token',
            'refresh_token': ui.refresh_token,
            'client_id': ui.client_id,
            'client_secret': ui.client_secret,
            'redirect_uri': ui.redirect_uri
        }
        res = httpx.post(para.url + "/token", data=postdata, headers=para.headers)
        if res.status_code == 200:
            jsonstr = json.loads(res.text)
            result = json.dumps(jsonstr, sort_keys=False, indent=4, separators=(',', ':'))
        else:
            result = "错误"
        self.signal.emit(result)


class new_refresh_token_thread_work(QThread):
    signal = Signal(str)

    def run(self):
        result = ""
        postdata = {
            'grant_type': 'authorization_code',
            'code': ui.code,
            'client_id': ui.client_id,
            'client_secret': ui.client_secret,
            'redirect_uri': ui.redirect_uri
        }
        res = httpx.post(para.url + "/token", data=postdata, headers=para.headers)
        if res.status_code == 200:
            jsonstr = json.loads(res.text)
            result = json.dumps(jsonstr, sort_keys=False, indent=4, separators=(',', ':'))
        else:
            result = "错误"
        self.signal.emit(result)


class get_admin_consent_work(QThread):
    signal = Signal(str)

    def __init__(self, isConsented=False, params={}, parent=None) -> None:
        super().__init__(parent=parent)
        self.params = params
        self.isConsented = isConsented

    def run(self):
        result = ""
        params_json = {}
        if self.isConsented:
            result = self.get_client_token()
            self.signal.emit(result)
            return

        if "error" in self.params.keys():
            if "error_description" in self.params.keys():
                result = "错误: " + "".join(self.params['error']) + "\n错误描述: " + "".join(self.params["error_description"])
            else:
                result = "错误: " + "".join(self.params['error']) + "\n错误描述: 未知"
        else:
            for key, value in self.params.items():
                params_json[key] = "".join(value)

            if ("admin_consent" not in params_json.keys()) or (params_json["admin_consent"] != "True"):
                result = "未知错误"
            else:
                result = self.get_client_token()
        self.signal.emit(result)

    def get_client_token(self):
        url = "https://login.microsoftonline.com/" + ui.tenant_id + "/oauth2/v2.0/token"
        postdata = {
            'client_id': ui.client_id,
            'client_secret': ui.client_secret,
            'scope': ui.set_scope(
                'https://graph.microsoft.com/.default'
            ),
            'grant_type': 'client_credentials'
        }
        res = httpx.post(url, data=postdata, headers=para.headers)
        if res.status_code == 200:
            jsonstr = json.loads(res.text)
            result = json.dumps(jsonstr, sort_keys=False, indent=4, separators=(',', ':'))
        else:
            result = "错误"
        return result


class mainwindow(QMainWindow, get_microsoft_token_ui.Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.get_refresh_token)
        self.tabWidget.setCurrentIndex(0)

    def get_refresh_token(self):
        self.textBrowser.setText("正在处理...")
        self.client_id = self.lineEdit.text()
        self.client_secret = self.lineEdit_2.text()
        if (self.client_id == '') or (self.client_secret == ''):
            self.textBrowser.setText("client_id和client_secret为必填项")
            return
        self.redirect_uri = self.lineEdit_3.text()
        if self.redirect_uri == '':
            self.redirect_uri = 'http://localhost'
        if self.tabWidget.currentIndex() == 0:
            self.refresh_token = self.lineEdit_4.text()
            if self.refresh_token != '':
                self.refresh_refresh_token()
            else:
                self.new_refresh_token()
        elif self.tabWidget.currentIndex() == 1:
            self.tenant_id = self.lineEdit_5.text()
            if self.tenant_id == '':
                self.textBrowser.setText("租户 ID为必填项")
                return
            self.get_admin_consent()

    def on_thread_started(self):
        self.pushButton.setEnabled(False)
        self.checkBox.setEnabled(False)

    def on_thread_finished(self):
        self.pushButton.setEnabled(True)
        self.checkBox.setEnabled(True)

    def set_scope(self, *args: str):
        return " ".join(args)

    def show_Dialog(self, request_url: str):
        self.input_url = ""
        ui2 = dialog(request_url)
        ui2.exec()

    def handle_input_url(self):
        result = ()
        if self.input_url == '':
            result = (False, "请输入重定向的地址")
        else:
            params = parse.parse_qs(parse.urlparse(self.input_url).query)
            result = (True, params)
        return result

    def refresh_refresh_token(self):
        thread = refresh_refresh_token_thread_work()
        thread.finished.connect(self.on_thread_finished)

        def set_result(result):
            self.textBrowser.setText(result)
        thread.signal.connect(set_result)

        self.on_thread_started()
        thread.start()
        thread.exec()

    def new_refresh_token(self):
        scope = self.set_scope(
            'Files.ReadWrite.All',
            'offline_access'
        )
        request_url = para.url + "/authorize?client_id=" + self.client_id + "&scope=" + scope + "&response_type=" + "code" + "&redirect_uri=" + self.redirect_uri

        self.show_Dialog(request_url)
        handle_input_url_result = self.handle_input_url()
        if not handle_input_url_result[0]:
            self.textBrowser.setText(handle_input_url_result[1])
            return
        params = handle_input_url_result[1]

        if 'code' not in params.keys():
            self.textBrowser.setText("重定向的地址中找不到参数\"code\"，请检查")
            return
        self.code = "".join(params['code'])

        thread = new_refresh_token_thread_work()
        thread.finished.connect(self.on_thread_finished)

        def set_result(result):
            self.textBrowser.setText(result)
        thread.signal.connect(set_result)

        self.on_thread_started()
        thread.start()
        thread.exec()

    def get_admin_consent(self):
        request_url = "https://login.microsoftonline.com/" + self.tenant_id + "/adminconsent?client_id=" + self.client_id + "&redirect_uri=" + self.redirect_uri
        params = {}
        isConsented = True

        if not self.checkBox.isChecked():
            isConsented = False
            self.show_Dialog(request_url)
            handle_input_url_result = self.handle_input_url()
            if not handle_input_url_result[0]:
                self.textBrowser.setText(handle_input_url_result[1])
                return
            params = handle_input_url_result[1]

        thread = get_admin_consent_work(isConsented=isConsented, params=params)
        thread.finished.connect(self.on_thread_finished)

        def set_result(result):
            self.textBrowser.setText(result)
        thread.signal.connect(set_result)

        self.on_thread_started()
        thread.start()
        thread.exec()


class dialog(QDialog, popup_ui.Ui_Dialog):
    def __init__(self, request_url, parent=None) -> None:
        super().__init__(parent=parent)
        self.request_url = request_url
        self.setupUi(self)
        self.textBrowser.setText(str(self.request_url))
        self.buttonBox.accepted.connect(self.get_input_url)

    def get_input_url(self):
        ui.input_url = self.lineEdit.text()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = mainwindow()
    ui.show()
    sys.exit(app.exec())
