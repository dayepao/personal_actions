import csv
import re
import sys
from pathlib import Path

import __main__
import numpy as np


def get_deviation_at_T(T, Ts, SA_i, SA_code):
    """
    计算反应谱在指定周期T的偏差
    :param T: 指定周期列表
    :param Ts: 反应谱周期
    :param SA_i: 时程反应谱加速度
    :param SA_code: 规范反应谱加速度
    :return: [(Ts[idx], SAV[idx])]
    """
    deviation = []
    for i in range(len(T)):
        idx = np.argmin(np.abs(Ts - T[i]))
        # deviation.append((np.round(Ts[idx], len(str(Ts[1] - Ts[0]).split(".")[1])), str(np.round(np.abs(SA_i[idx] - SA_code[idx]) / SA_code[idx] * 100, 2)) + "%"))
        deviation.append((T[i], str(np.round(np.abs(SA_i[idx] - SA_code[idx]) / SA_code[idx] * 100, 2)) + "%"))
    return deviation


# 获取坐标轴刻度
def get_axis_ticks(Ts, SA):
    SA_max = np.max(SA[~np.isnan(SA)])
    base = 0.5 * 10 ** np.floor(np.log10(SA_max))
    x_major_ticks = np.arange(0, np.max(Ts) + 1e-9, 1)
    x_minor_ticks = np.arange(0, np.max(Ts) + 1e-9, 0.2)
    y_major_ticks = np.arange(0, base * (np.ceil(SA_max / base) + 1) + 1e-9, base)
    y_minor_ticks = np.arange(0, base * (np.ceil(SA_max / base) + 1) + 1e-9, base / 5)
    return x_major_ticks, x_minor_ticks, y_major_ticks, y_minor_ticks


def write_lists_to_csv(filename, *args):
    """
    将任意数量的列表写入到指定的CSV文件

    参数：
    filename (str or Path): 要写入的CSV文件的名字
    *args (list): 任意数量的列表

    注意：这个函数假设所有的列表长度相等。
    """
    # 确保所有的列表长度都相等
    assert all(len(lst) == len(args[0]) for lst in args)

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        for items in zip(*args):
            writer.writerow(items)


# 获取当前程序文件路径、文件夹路径、文件名
def get_self_dir():
    """获取自身路径

    返回`(self_path, self_dir, self_name)`

    self_path: 当前程序文件完整路径 (包括文件名)
    self_dir: 当前程序文件所在文件夹路径
    self_name: 当前程序文件名
    """
    self_path = Path(__main__.__file__).resolve() if Path(__file__).suffix == ".py" else Path(sys.executable).resolve()
    self_dir, self_name = self_path.parent, self_path.name
    return self_path, self_dir, self_name


# 将 PEER 格式的时程文件转换为 1 列的时程文件
def peer_to_single_column(peer_file):
    """将 PEER 格式的时程文件转换为 1 列的时程文件

    参数：
    peer_file (str or Path): PEER 格式的时程文件
    """
    peer_file = Path(peer_file)

    # 读取 PEER 格式的时程文件
    with open(peer_file, "r") as f:
        lines = f.readlines()

    # 提取 PEER 格式的时程文件中的时程数据
    data = []
    found_npts_dt = False
    for line in lines:
        if not found_npts_dt:
            if re_result := re.search(r"NPTS\s*=\s*(\d+)\s*.*\s*DT\s*=\s*([\.\d]+)", line):
                npts, dt = int(re_result.group(1)), float(re_result.group(2))
                found_npts_dt = True
        elif re.match(r"[\s]*-?[\d\.]+(?:[Ee][+\-]?\d+)?", line):
            data.extend(map(float, re.findall(r"-?[\d\.]+(?:[Ee][+\-]?\d+)?", line)))
    data = np.array(data, dtype=float)

    # 将时程数据写入 1 列的时程文件
    np.savetxt(peer_file.with_name(f"{peer_file.stem}_{npts}_{dt}.txt"), data, fmt="%.6e")


if __name__ == "__main__":
    # Ts = np.arange(0, 6, 0.01)
    # SA = np.array(0.4)
    # print(get_axis_ticks(Ts, SA))
    # for file in Path(r"PEERNGARecords_Unscaled").glob("*.AT2"):
    #     peer_to_single_column(file)
    for num in range(101, 201):
        print(f"{num},", end="")
