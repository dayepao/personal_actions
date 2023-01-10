import os

from utils_dayepao import cmd_dayepao, get_resource_path, get_self_dir

target_dir = get_self_dir()[1]
target_dir = "C:\\Users\\ll057\\Music\\VipSongsDownload"

for file in os.listdir(target_dir):
    if os.path.isfile(file_path := os.path.join(target_dir, file)):
        if file.endswith((".mflac", ".mgg")):
            print("正在处理文件: " + file)
            ps = "{} -o \"{}\" \"{}\"".format(get_resource_path("musicdecrypto.exe"), target_dir, file_path)
            ps = "{} --update-metadata --overwrite -o \"{}\" -i \"{}\"".format(get_resource_path("um.exe"), target_dir, file_path)
            # print(ps)
            out_queue, err_queue, returncode_queue = cmd_dayepao(ps)
            # while (result := out_queue.get()) != b"":
            #     print(result)
            if returncode_queue.get() == 0:
                os.remove(file_path)
            else:
                print("处理失败: " + file)
        else:
            print("跳过文件: " + file)
input("按回车键退出")
