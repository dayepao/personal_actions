bind = "0.0.0.0:35456"  # 绑定地址和端口
workers = 4  # 设置工作进程数
worker_class = "gevent"  # 可以选择其他类型的 worker，例如 sync、gevent、eventlet 等
loglevel = "info"  # 日志级别
accesslog = "-"  # 将访问日志输出到标准输出
errorlog = "-"  # 将错误日志输出到标准输出
# timeout = 120  # 超时时间
# preload = True  # 启用预加载应用代码


def on_starting(server):
    """只在主进程启动定时任务"""
    import time

    from livetv_format.handle_cache import schedule_update_cached_file
    schedule_update_cached_file()
    time.sleep(15)
