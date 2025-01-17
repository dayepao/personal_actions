from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

from .cache_config import CACHE_FILE_CONFIGS
from .utils_app import http_request


# 下载并更新缓存的文件
def update_cached_file(file_url, file_path: Path):
    """下载文件并更新缓存"""
    assert isinstance(file_path, Path), "file_path 必须为 Path 对象"
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        response = http_request("get", file_url)
        response.raise_for_status()

        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"缓存文件 {file_path.name} 更新于 {datetime.now()}")
    except Exception as e:
        print(f"更新缓存文件 {file_path.name} 失败: {e}")


# 定时任务更新缓存文件
def schedule_update_cached_file():
    """定时任务, 定时更新缓存文件"""
    scheduler = BackgroundScheduler()
    for cache_file, config in CACHE_FILE_CONFIGS.items():
        cache_expiry_time = config["CACHE_EXPIRY_TIME"]
        # 将缓存失效时间(timedelta)转换为秒数
        cache_expiry_seconds = cache_expiry_time.total_seconds()

        scheduler.add_job(
            update_cached_file,
            "interval",
            seconds=cache_expiry_seconds,
            args=[config["FILE_URL"], config["CACHE_PATH"].joinpath(cache_file)],
        )
    scheduler.start()
    print("缓存文件更新任务已启动")
    # 立即执行一次任务
    for job in scheduler.get_jobs():
        job.modify(next_run_time=datetime.now())


if __name__ == "__main__":
    # 启动定时任务
    schedule_update_cached_file()
    import time
    time.sleep(60)
