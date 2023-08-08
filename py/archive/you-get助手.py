import os
from pathlib import Path

# .\ffmpeg.exe -i "111.mp4" -map 0 -c:a copy -c:s copy -c:v libx264 "111_end.mp4"


def download():
    url = input("请输入视频链接:")
    # main = "youtube-dl.exe " + url + "-f best --external-downloader aria2c.exe --external-downloader-args \"-x 16 -k 1M\" --exec \"move {} downloads\\{}\""
    main = "you-get \"" + url + "\" -o \"downloads\""
    main = main + " --format=flv"
    # main = main + " -c \"cookies.txt\""
    main = main + " --no-caption"  # 不下载弹幕等
    # main = main + " --skip-existing-file-size-check" # 不检查文件大小就跳过
    # main = main + " -l" # 下载视频列表
    # main = main + " --first 5"
    # main = main + " --last 8"
    # main = main + " -i" # 显示视频信息，不实际下载
    # main = main + " --debug"
    r_v = os.system(main)
    print(r_v)
    os.chdir('downloads')
    filenames = os.listdir('.')
    for filename in filenames:
        if Path(filename).suffix == ".flv":
            new_filename = Path(filename).with_suffix(".mp4")
            main = "..\\ffmpeg.exe -loglevel quiet -i \"" + \
                filename + "\" -c copy \"" + str(new_filename) + "\""
            r_v = os.system(main)
            os.remove(filename)
            print(r_v)
    os.chdir(os.pardir)


if Path('downloads').exists():
    download()
else:
    os.mkdir('downloads')
    download()
# os.system("pause")
