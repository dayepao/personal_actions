import copy
import os
import re
import sys
from pathlib import Path

from rename_replace import rename_replace
from utils_dayepao import get_self_dir


# 删除指定后缀的文件
def delete_useless_file(path):
    for child_name in os.listdir(path):
        if (child_path := Path.joinpath(path, child_name)).is_file():
            if child_name.endswith((".torrent", ".txt", ".url", ".srt", ".ass", ".ssa", ".nfo", ".jpg", ".png", ".xltd")):
                os.remove(child_path)


def get_left_same_part(file_list):
    # 判断文件数量是否为1
    if len(file_list) == 1:
        return ""

    left_same_part = ""
    i = 0
    flag = True
    for i in range(len(file_list[0])):
        left_same_part += file_list[0][i]
        for file in file_list:
            if left_same_part != file[:i+1]:
                left_same_part = left_same_part[:-1]
                flag = False
            if not flag:
                break
        i += 1
        if not flag:
            break

    # 判断最后一个字符是否为数字
    if left_same_part and left_same_part[-1].isdigit():
        left_same_part = left_same_part[:-1]

    return left_same_part


def get_right_same_part(file_list):
    # 判断文件数量是否为1
    if len(file_list) == 1:
        return ""

    right_same_part = ""
    i = 0
    flag = True
    for i in range(len(file_list[0])):
        right_same_part = file_list[0][-i-1] + right_same_part
        for file in file_list:
            if right_same_part != file[-i-1:]:
                right_same_part = right_same_part[1:]
                flag = False
            if not flag:
                break
        i += 1
        if not flag:
            break

    # 去除后缀
    right_same_part, ext = Path(right_same_part).stem, Path(right_same_part).suffix
    if ext == "":
        right_same_part = ""

    # 判断第一个字符是否为数字
    if right_same_part and right_same_part[0].isdigit():
        right_same_part = right_same_part[1:]

    return right_same_part


# 识别文件名中的集数
def get_episode_num(file_name: str, episode_num_len: int = 2):
    is_pure_num = re.search(re.compile(r"^\d+$"), Path(file_name).stem)
    if is_pure_num:
        file_name = "e{}".format(file_name)

    file_name = file_name.replace("BDE4", "")
    file_name = file_name.replace("【", "[")
    file_name = file_name.replace("】", "]")
    file_name = file_name.replace("[", "e")
    file_name = file_name.replace("(", "")
    file_name = file_name.replace(")", "")
    file_name = file_name.replace(" ", "")
    file_name = file_name.replace("M", "m")
    file_name = file_name.replace("E", "e")
    file_name = file_name.replace("P", "p")
    file_name = file_name.replace("S", "s")
    file_name = file_name.replace("ep", "e")
    file_name = file_name.replace("sp", "e")
    episode_num = re.findall(re.compile(r"e(\d+)[^0-9]"), file_name)
    temp_episode_num = copy.deepcopy(episode_num)
    for num in temp_episode_num:
        if num == "0" or int(num) > 700:
            episode_num.remove(num)
    if episode_num and len(episode_num) == 1:
        episode_num = str(int(episode_num[0])).rjust(episode_num_len, "0")
    else:
        episode_num = None

    return episode_num


def handle_error(none_name, duplicate_name):
    if none_name:
        print("\033[1;33m未识别的文件: \033[0m")
        for name in none_name:
            print("    {}".format(name))
    if duplicate_name:
        print("\033[1;31m存在重复: \033[0m")
        for old_name, new_name in duplicate_name.items():
            print("    {} >>>>>> {}".format(old_name, new_name))
    print("")


def get_filename_map_same_part_removal(root_path):
    print("正在尝试使用去除重复部分的方法重命名...")
    filename_map = {}
    none_name = []
    delete_useless_file(root_path)
    for video_name in os.listdir(root_path):
        if not (video_path := Path.joinpath(root_path, video_name)).is_dir():
            continue
        delete_useless_file(video_path)
        for season in os.listdir(video_path):
            if (not (season_path := Path.joinpath(video_path, season)).is_dir()) or ("Season" not in season and "season" not in season):
                continue
            delete_useless_file(season_path)
            file_list = os.listdir(season_path)
            episode_num_len = max(len(str(len(file_list))), 2)
            left_same_part = get_left_same_part(file_list)
            right_same_part = get_right_same_part(file_list)
            file_dict = {}
            for file in file_list:
                file_dict[file] = file.replace(left_same_part, "").replace(right_same_part, "")
            for file, temp_file in file_dict.items():
                if not Path.joinpath(season_path, file).is_file():
                    continue
                if (episode_num := get_episode_num(temp_file, episode_num_len)):
                    filename_map[str(Path.joinpath(video_name, season, file))] = str(Path.joinpath(video_name, season, "{} - S{}E{}.mp4".format(video_name, season[-2:], episode_num)))
                else:
                    none_name.append(str(Path.joinpath(video_name, season, file)))

    new_name_list = list(filename_map.values())
    duplicate_name = {}
    for old_name, new_name in filename_map.items():
        if new_name_list.count(new_name) > 1:
            duplicate_name[old_name] = new_name
    if none_name or duplicate_name:
        handle_error(none_name, duplicate_name)
        return None
    return filename_map


def get_filename_map_regular(root_path):
    print("正在尝试使用正则表达式识别文件名...")
    filename_map = {}
    none_name = []
    delete_useless_file(root_path)
    for video_name in os.listdir(root_path):
        if not (video_path := Path.joinpath(root_path, video_name)).is_dir():
            continue
        delete_useless_file(video_path)
        for season in os.listdir(video_path):
            if (not (season_path := Path.joinpath(video_path, season)).is_dir()) or ("Season" not in season and "season" not in season):
                continue
            delete_useless_file(season_path)
            file_list = os.listdir(season_path)
            episode_num_len = max(len(str(len(file_list))), 2)
            for file in file_list:
                if not Path.joinpath(season_path, file).is_file():
                    continue
                if (episode_num := get_episode_num(file, episode_num_len)):
                    filename_map[str(Path.joinpath(video_name, season, file))] = str(Path.joinpath(video_name, season, "{} - S{}E{}.mp4".format(video_name, season[-2:], episode_num)))
                else:
                    none_name.append(str(Path.joinpath(video_name, season, file)))

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
    if not (root_path := Path.joinpath(get_self_dir()[1], "rename_media")).exists():
        os.mkdir(root_path)
        print("创建目录: ", root_path)

    print("开始处理文件名中不受支持的字符")
    print("正在处理")
    rename_replace(root_path, [(":", " - "), ("", " - "), ("？", "#"), ("  ", " ")])
    print("处理完成")

    print("开始重命名")
    print("正在处理")

    if not (filename_map := get_filename_map_same_part_removal(root_path)):
        filename_map = get_filename_map_regular(root_path)
    # print(json.dumps(filename_map, indent=4, ensure_ascii=False))

    if filename_map:
        for old_name, new_name in filename_map.items():
            old_path = Path.joinpath(root_path, old_name)
            new_path = Path.joinpath(root_path, new_name)
            if old_path != new_path:
                if new_path.exists():
                    if input("文件已存在: {}，是否删除？[y/N]".format(new_path)) in ("y", "Y"):
                        os.remove(new_path)
                    else:
                        print("请手动处理后重新运行程序")
                        sys.exit(0)
                os.rename(old_path, new_path)
                print("重命名: ", old_name, " >>>>>> ", new_name)

    print("处理完成")
    input("按回车键退出")
