import os

from utils_dayepao import cmd_dayepao, get_resource_path, get_self_dir

for file in os.listdir(get_self_dir()[1]):
    if file.endswith((".ts", ".TS")):
        print("正在处理文件: " + file)
        ps = "{} -i \"{}\" -c copy \"{}\".mp4".format(get_resource_path("ffmpeg.exe"), file, file[:-3])
        print(ps)
        out_queue, err_queue, returncode_queue = cmd_dayepao(ps)
        # while (ps_result := out_queue.get()) != b"":
        #     print(ps_result)
        while (ps_result := err_queue.get()) != b"":
            print(ps_result)
        if returncode_queue.get() == 0:
            os.remove(file)
input("按回车键退出")
