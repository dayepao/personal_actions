from flask import Flask


def create_app():
    app = Flask(__name__)

    # 在这里注册其他蓝图或路由
    from .routes import modify_m3u
    app.add_url_rule("/tv.m3u", view_func=modify_m3u)

    return app
