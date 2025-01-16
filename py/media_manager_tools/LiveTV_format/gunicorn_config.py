def on_starting(server):
    """只在主进程启动定时任务"""
    from livetv_format.handle_cache import schedule_update_cached_file
    schedule_update_cached_file()  # 只在主进程启动定时任务
