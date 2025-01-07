import re
import sys
from pathlib import Path

path = r""

if input(f"Delete all obsolete bif files in {path}? (y/n) ").lower() != "y":
    sys.exit()

for bif_file in Path(path).rglob("*.bif"):
    if bif_file.is_file():
        video_extensions = (".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm", ".mpg", ".mpeg", ".m4v", ".3gp")
        video_file = None
        for video_extension in video_extensions:
            video_name = re.match(r"^(.*?)(?:(?:-\d+)*)$", bif_file.stem).group(1)
            tmp_video_file = bif_file.with_name(f"{video_name}{video_extension}")
            if tmp_video_file.is_file():
                video_file = tmp_video_file
                break
        if not video_file:
            print(f"Obsolete: {bif_file}, no video file found")
            # bif_file.unlink()
        else:
            # 获取文件的修改时间
            bif_time = bif_file.stat().st_mtime
            video_time = video_file.stat().st_mtime
            if bif_time < video_time:
                print(f"Obsolete: {bif_file}, video file is newer")
                # bif_file.unlink()
