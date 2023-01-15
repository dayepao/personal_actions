import os

from utils_dayepao import get_self_dir

target_dir = get_self_dir()[1]
target_dir = "C:\\Users\\ll057\\Music"
# target_dir = "C:\\Users\\ll057\\Music\\VipSongsDownload"

for file in os.listdir(target_dir):
    if os.path.isfile(file_path := os.path.join(target_dir, file)):
        rm_tuple = []
        rm_tuple.append("flac")
        rm_tuple.append("ogg")
        rm_tuple.append("m4a")
        if file.endswith(rm_tuple := tuple(rm_tuple)):
            os.remove(file_path)
        else:
            print("跳过文件: " + file)
input("按回车键退出")
