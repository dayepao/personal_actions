import os
from pathlib import Path

from utils_dayepao import cmd_dayepao, get_resource_path, get_self_dir

target_dir = get_self_dir()[1]
target_dir = "C:\\Users\\ll057\\Music"

for file in os.listdir(target_dir):
    if (file_path := Path(target_dir, file)).is_file():
        if file.endswith((".ts", ".TS")):
            print("正在处理文件: " + file)
            ps = "{} -i \"{}\" -c copy \"{}.mp4\"".format(get_resource_path("ffmpeg.exe"), file_path, file_path.stem)
            out_queue, err_queue, returncode_queue = cmd_dayepao(ps)
            if returncode_queue.get() == 0:
                os.remove(file_path)
            else:
                print("处理失败: " + file)
        else:
            print("跳过文件: " + file)
input("按回车键退出")
