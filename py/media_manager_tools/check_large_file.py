from pathlib import Path

from moviepy.editor import VideoFileClip

# pip install moviepy


def find_large_files(path, extensions, min_size_in_gb):
    """
    遍历指定路径下指定后缀名文件，输出大于指定大小的文件名及其实际大小，同时输出媒体文件的时长

    参数:
        path: 需要遍历的路径.
        extensions: 指定的文件后缀名列表，例如 ['.txt', '.pdf', '.mp4', '.mp3'].
        min_size_in_gb: 最小文件大小，单位为GB.
    """

    # 确保文件后缀名以点开头
    extensions = [ext if ext.startswith(".") else "." + ext for ext in extensions]

    min_size_in_bytes = min_size_in_gb * 1024 * 1024 * 1024  # 将GB转换为字节

    for file in Path(path).rglob("*"):
        if file.is_file() and any(file.name.lower().endswith(ext) for ext in extensions):
            file_size_in_bytes = file.stat().st_size
            if file_size_in_bytes > min_size_in_bytes:
                file_size_in_gb = file_size_in_bytes / (1024 * 1024 * 1024)  # 将字节转换为GB
                if file.suffix in [".mp4", ".mp3", ".mkv", ".avi", ".flv", ".mov"]:
                    clip = VideoFileClip(str(file))
                    duration = clip.duration  # 获取时长
                    hours, remainder = divmod(duration, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    print(f"文件 '{file}' 的大小超过 {min_size_in_gb} GB, 实际大小为 {file_size_in_gb:.2f} GB, 时长为 {int(hours)}:{int(minutes)}:{round(seconds)}.")
                    clip.close()  # 关闭视频文件，释放资源
                else:
                    print(f"文件 '{file}' 的大小超过 {min_size_in_gb} GB, 实际大小为 {file_size_in_gb:.2f} GB.")


# 调用函数，例如:
find_large_files(r"", [".mp4", ".mp3", ".mkv", ".avi", ".flv", ".mov"], 15)
