import copy
import os


def rename_and_return_child_dir(path, replace_list):
    child_dir = []
    for child_name in os.listdir(path):
        child_path = os.path.join(path, child_name)
        temp_name = child_name
        for replace_tuple in replace_list:
            temp_name = temp_name.replace(replace_tuple[0], replace_tuple[1])
        new_name = temp_name
        new_child_path = os.path.join(path, new_name)
        if new_name != child_name:
            print(f"{child_path}  --->  {new_child_path}")
            os.rename(child_path, new_child_path)
        if os.path.isdir(new_child_path):
            child_dir.append(new_child_path)
    return child_dir


def rename_replace(path, replace_list):
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


if __name__ == "__main__":
    path = ["Y:\\", "Z:\\"]
    replace_list = [("：", " - "), (":", " - "), ("", " - "), ("？", "#"), ("  ", " ")]
    rename_replace(path, replace_list)
