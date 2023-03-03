import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_waves(selected_waves):
    """
    读取地震时程数据
    :param selected_waves: 地震时程数据列表
    :return: 地震时程数据列表[(时程时间, 时程加速度, 时程名称)]
    """
    selected_waves = selected_waves if isinstance(selected_waves, list) else [selected_waves]
    waves = []
    for selected_wave in selected_waves:
        assert isinstance(selected_wave, dict), "地震时程数据格式错误"
        # 确定跳过行数
        skiprows = selected_wave.get("skiprows")
        if not skiprows:
            skiprows = 0
            with open(selected_wave["file"], "r") as f:
                while (line := f.readline()) != b"":
                    if re.match(re.compile(r"[^ ]+ [^ ]+.*"), line):
                        skiprows = skiprows + 1
                    else:
                        break
        # 确定时程名称
        wave_name = selected_wave.get("name", Path(selected_wave["file"]).stem)
        # 确定时程时间间隔
        assert (dt := selected_wave.get("dt")), "请指定时程时间间隔"
        # 读取时程数据
        wave_data = np.loadtxt(selected_wave["file"], skiprows=skiprows)
        wave_data = wave_data if wave_data.ndim == 1 else wave_data[:, 1]
        # 归一化
        wave_data = wave_data / np.max(np.abs(wave_data))
        # 生成时程时间
        Tw = np.arange(0, np.round(len(wave_data) * dt, len(str(dt).split(".")[1])), dt)
        # 组合时程数据
        waves.append((Tw, wave_data, wave_name))
    return waves


def plot_waves(waves):
    """
    绘制地震时程数据
    :param waves: 地震时程数据列表
    :return: None
    """
    y_major_ticks = np.arange(-1, 1.1, 0.25)
    for wave in waves:
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(wave[0], wave[1], linewidth=1, alpha=0.8)
        ax.grid(which='major', alpha=0.7)
        ax.set_title(wave[2])
        ax.set_xlabel("t(s)")
        ax.set_ylabel("a(m/s^2)")
        ax.set_xlim(0, np.max(wave[0]))
        ax.set_ylim(-1, 1)
        ax.set_yticks(y_major_ticks)
    plt.show()
