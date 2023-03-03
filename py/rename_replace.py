import copy
import os
from pathlib import Path


def rename_and_return_child_dir(path, replace_list):
    child_dir = []
    for child_name in os.listdir(path):
        child_path = Path(path).joinpath(child_name)
        temp_name = child_name
        for replace_tuple in replace_list:
            temp_name = temp_name.replace(replace_tuple[0], replace_tuple[1])
        new_name = temp_name
        new_child_path = Path(path).joinpath(new_name)
        if new_name != child_name:
            print(f"{child_path}  --->  {new_child_path}")
            os.rename(child_path, new_child_path)
        if new_child_path.is_dir():
            child_dir.append(str(new_child_path))
    return child_dir


def rename_replace_old(path, replace_list):
    if type(path) == list:
        cur_paths = path
    else:
        cur_paths = [path]
    print("正在处理")
    while True:
        temp_dir = []
        for cur_path in cur_paths:
            cur_child_dir = rename_and_return_child_dir(cur_path, replace_list)
            if len(cur_child_dir) == 0:
                continue
            temp_dir.extend(cur_child_dir)
        cur_paths = copy.deepcopy(temp_dir)
        if cur_paths == []:
            break
    print("处理完成")


def rename_replace(paths, replace_list):
    if type(paths) not in [list, tuple, str]:
        print("paths 参数类型错误")
        return
    if type(paths) == str:
        paths = [paths]
    for path in paths:
        for root, dirs, files in os.walk(path, topdown=False):  # topdown=False 从下往上遍历
            for old_name in dirs + files:
                old_path = Path(root).joinpath(old_name)
                temp_name: str = old_name
                for replace_tuple in replace_list:
                    temp_name = temp_name.replace(replace_tuple[0], replace_tuple[1])
                new_name = temp_name
                new_path = Path(root).joinpath(new_name)
                if new_name != old_name:
                    print(f"{old_path}  --->  {new_path}")
                    os.rename(old_path, new_path)


if __name__ == "__main__":
    paths = ["Y:\\", "Z:\\"]
    replace_list = [(":", " - "), ("", " - "), ("？", "#"), ("  ", " ")]
    # rename_replace_old(path, replace_list)
    rename_replace(paths, replace_list)
