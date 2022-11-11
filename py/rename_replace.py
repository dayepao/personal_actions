import copy
import os


def rename_and_return_child_dir(path, replace_list):
    child_dir = []
    for child_name in os.listdir(path):
        child_path = os.path.join(path, child_name)
        if os.path.isfile(child_path):
            # 重命名操作
            temp_name = child_name
            for replace_tuple in replace_list:
                temp_name = temp_name.replace(replace_tuple[0], replace_tuple[1])
            new_name = temp_name
            # if new_name != child_name and (not os.path.exists(child_path.replace("Z:\\\\server", r"C:\\Users\ll057\OneDrive - lyhscu\VPS"))):
            if new_name != child_name:
                print((child_path, os.path.join(path, new_name)))
                os.rename(child_path, os.path.join(path, new_name))
        if os.path.isdir(child_path):
            # 重命名操作
            temp_name = child_name
            for replace_tuple in replace_list:
                temp_name = temp_name.replace(replace_tuple[0], replace_tuple[1])
            new_name = temp_name
            if new_name != child_name:
                print((child_path, os.path.join(path, new_name)))
                os.rename(child_path, os.path.join(path, new_name))
                child_dir.append(os.path.join(path, new_name))
            else:
                child_dir.append(child_path)
    return child_dir


if __name__ == "__main__":
    cur_paths = ["Z:\\"]
    replace_list = [("：", " - "), (":", " - "), ("？", "#"), ("  ", " ")]
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
