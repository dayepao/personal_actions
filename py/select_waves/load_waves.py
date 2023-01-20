import os

import matplotlib.pyplot as plt
import numpy as np


def load_waves(wave_files):
    """
    读取地震时程数据
    :param wave_files: 地震时程数据文件列表
    :return: 地震时程数据列表[(时程时间, 时程加速度, 时程名称)]
    """
    waves = []
    for wave_file in wave_files:
        wave_data = np.loadtxt(wave_file[0])
        wave_data = wave_data if wave_data.ndim == 1 else wave_data[:, 1]
        # 归一化
        wave_data = wave_data / np.max(np.abs(wave_data))
        Tw = np.arange(0, len(wave_data) * wave_file[1], wave_file[1])  # 时程时间
        waves.append((Tw, wave_data, wave_file[2] if len(wave_file) == 3 else os.path.splitext(os.path.basename(wave_file[0]))[0]))
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
        ax.set_yticks(y_major_ticks)
    plt.show()
