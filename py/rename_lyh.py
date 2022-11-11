import os
import re
import sys

from utils_dayepao import get_self_dir


# 删除指定后缀的文件
def delete_useless_file(path):
    for child_name in os.listdir(path):
        child_path = os.path.join(path, child_name)
        if os.path.isfile(child_path):
            if child_name.endswith((".torrent", ".txt", ".url", ".srt", ".ass", ".ssa", ".nfo", ".jpg", ".png")):
                os.remove(child_path)


# 识别文件名中的集数
def get_episode_num(file_name: str):
    is_pure_num = re.search(r"^\d+$", os.path.splitext(file_name)[0])
    if is_pure_num:
        file_name = "e{}".format(file_name)

    file_name = file_name.replace("BDE4", "")
    file_name = file_name.replace("(", "")
    file_name = file_name.replace(")", "")
    file_name = file_name.replace(" ", "")
    file_name = file_name.replace("M", "m")
    file_name = file_name.replace("E", "e")
    file_name = file_name.replace("P", "p")
    file_name = file_name.replace("S", "s")
    file_name = file_name.replace("ep", "e")
    file_name = file_name.replace("sp", "e")
    file_name = file_name.replace("e", "e0")
    file_name = file_name.replace("00", "0")
    episode_num = re.search(r".*e(\d+)[^0-9]*", file_name)
    if episode_num:
        if episode_num.group(1).startswith("0") and len(episode_num.group(1)) == 3 and episode_num.group(1)[0] == "0":
            episode_num = episode_num.group(1)[1:]
        else:
            episode_num = episode_num.group(1)
    return episode_num if episode_num else None


def handle_error(none_name, duplicate_name):
    if none_name:
        print("\033[1;33m未识别的文件: \033[0m")
        for name in none_name:
            print("    {}".format(name))
    if duplicate_name:
        print("\033[1;31m存在重复: \033[0m")
        for old_name, new_name in duplicate_name.items():
            print("    {} >>>>>> {}".format(old_name, new_name))


def get_filename_map(root_path):
    filename_map = {}
    none_name = []
    delete_useless_file(root_path)
    for video_name in os.listdir(root_path):
        video_path = os.path.join(root_path, video_name)
        if not os.path.isdir(video_path):
            continue
        delete_useless_file(video_path)
        for season in os.listdir(video_path):
            season_path = os.path.join(video_path, season)
            if not os.path.isdir(season_path):
                continue
            delete_useless_file(season_path)
            for file in os.listdir(season_path):
                file_path = os.path.join(season_path, file)
                if not os.path.isfile(file_path):
                    continue
                if (episode_num := get_episode_num(file)):
                    filename_map[os.path.join(video_name, season, file)] = os.path.join(video_name, season, "{} S{}E{}.mp4".format(video_name, season[-2:], episode_num))
                else:
                    none_name.append(os.path.join(video_name, season, file))

    new_name_list = list(filename_map.values())
    duplicate_name = {}
    for old_name, new_name in filename_map.items():
        if new_name_list.count(new_name) > 1:
            duplicate_name[old_name] = new_name
    if none_name or duplicate_name:
        handle_error(none_name, duplicate_name)
        return None
    return filename_map


if __name__ == "__main__":
    root_path = os.path.join(get_self_dir()[1], "rename_lyh")
    if not os.path.exists(root_path):
        os.mkdir(root_path)
        print("创建目录: ", root_path)

    filename_map = get_filename_map(root_path)
    # print(json.dumps(filename_map, indent=4, ensure_ascii=False))

    if filename_map:
        for old_name, new_name in filename_map.items():
            old_path = os.path.join(root_path, old_name)
            new_path = os.path.join(root_path, new_name)
            if old_path != new_path:
                if os.path.exists(new_path):
                    if input("文件已存在: {}，是否删除？[y/N]".format(new_path)) in ("y", "Y"):
                        os.remove(new_path)
                    else:
                        print("请手动处理后重新运行程序")
                        sys.exit(0)
                os.rename(old_path, new_path)
                print("重命名: ", old_name, " >>>>>> ", new_name)

    print("处理完成")
    input("按回车键退出")
