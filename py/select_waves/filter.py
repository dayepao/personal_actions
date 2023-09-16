import re
import shutil
from pathlib import Path

# 读取目标序号列表
list_path = Path(r"h1.txt")
with list_path.open() as f:
    rsn_list = f.read().strip()  # 读取文件内容并去除前后空白
rsn_list = rsn_list[1:-1]  # 去除首尾的中括号
rsn_list = rsn_list.split(";")  # 以分号分隔字符串


# 遍历指定目录下的所有文件，筛选出列表中的序号对应的文件
file_path = Path(r"record")
result = {}
for file in file_path.iterdir():
    # 判断后缀是否为AT2
    if file.suffix != ".AT2":
        continue
    # 通过正则匹配文件名中的 RSN 编号
    rsn = re.search(r"^RSN(\d+?)_.*?", file.name).group(1)
    if rsn not in rsn_list:
        continue
    # 匹配文件名中的角度或方向
    direction = re.search(r".*(\d{3})\.AT2", file.name)
    if not direction:
        direction = re.search(r".*-(H1|H2)\.AT2", file.name)
    if not direction:
        direction = re.search(r".*(E|N)\.AT2", file.name)

    if direction:
        direction = direction.group(1)

    # 将E和N转换为H1和H2
    if direction == "E":
        direction = "H1"
    elif direction == "N":
        direction = "H2"

    if rsn not in result:
        result[rsn] = []
    result[rsn].append({"file": file, "direction": direction})

# 将方向为角度的文件转换为方向
for rsn, items in result.items():
    unprocessed_files = [item for item in items if item["direction"] not in [None, "H1", "H2"]]
    if len(unprocessed_files) >= 2:
        unprocessed_files.sort(key=lambda x: int(x["direction"]))
        unprocessed_files[0]["direction"] = "H1"
        unprocessed_files[1]["direction"] = "H2"

target_direction = list_path.stem.upper()
for rsn, items in result.items():
    for item in items:
        if item["direction"] == target_direction:
            target_file = item["file"]
            break
    if target_file:
        print(f"RSN{rsn} 的 {target_direction} 方向文件为 {target_file.name} ----------- 全部文件为 {[item['file'].name for item in items]}")
        # if not (list_path.parent / target_direction).exists():
        #     (list_path.parent / target_direction).mkdir(exist_ok=True)
        # shutil.copy(target_file, list_path.parent / target_direction / target_file.name)
    else:
        print(f"RSN{rsn} 的 {target_direction} 方向文件不存在 ----------- 全部文件为 {[item['file'].name for item in items]}")
