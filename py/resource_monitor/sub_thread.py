import psutil
from PySide6.QtCore import QThread, QTimer, Signal

# pip install psutil

# https://psutil.readthedocs.io/en/latest/


class get_system_utilization(QThread):
    signal = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

    def get_system_utilization(self):
        system_utilization = {}
        system_utilization["cpu_utilization"] = psutil.cpu_percent()
        system_utilization["per_cpu_utilization"] = psutil.cpu_percent(percpu=True)
        system_utilization["cpu_freq"] = psutil.cpu_freq()  # MHz
        system_utilization["per_cpu_freq"] = psutil.cpu_freq(percpu=True)  # MHz
        system_utilization["memory_utilization"] = psutil.virtual_memory().percent
        self.signal.emit(system_utilization)

    def run(self):
        timer = QTimer()
        timer.timeout.connect(self.get_system_utilization)
        timer.start(500)
        self.exec()


class resource_monitor(QThread):
    signal = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)

    def emit_signal(self):
        self.signal.emit(self.resource)

    def handle_sub_thread(self, command: str, sub_thread: str):
        if command == "stop":
            if sub_thread in dir(self):
                getattr(self, sub_thread).quit()
                getattr(self, sub_thread).wait()
        elif command == "restart":
            if sub_thread in dir(self):
                getattr(self, sub_thread).quit()
                getattr(self, sub_thread).wait()
                getattr(self, sub_thread).start()
            else:
                getattr(self, f"start_{sub_thread}")()

    def start_get_system_utilization_thread(self):
        self.get_system_utilization_thread = get_system_utilization()

        def on_thread_finished():
            self.resource["system_utilization"] = "系统使用率子线程已停止，正在尝试重启..."
            timer = QTimer()
            timer.singleShot(3000, lambda: self.handle_sub_thread("restart", "get_system_utilization_thread"))
        self.get_system_utilization_thread.finished.connect(on_thread_finished)

        def update_system_utilization(system_utilization: dict):
            self.resource["system_utilization"] = system_utilization
        self.get_system_utilization_thread.signal.connect(update_system_utilization)

        self.get_system_utilization_thread.start()

    def stop(self):
        if 'emit_timer' in dir(self):
            self.emit_timer.stop()
        self.handle_sub_thread("stop", "get_system_utilization_thread")

    def run(self):
        self.resource = {"system_utilization": "正在获取系统资源使用情况..."}
        self.emit_signal()

        # 启动监控子线程
        self.start_get_system_utilization_thread()

        self.emit_timer = QTimer()
        self.emit_timer.timeout.connect(self.emit_signal)
        self.emit_timer.start(1000)
        self.exec()
        self.stop()
