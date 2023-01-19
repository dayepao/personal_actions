import matplotlib.pyplot as plt
import numpy as np

import dynamic_calculator
import load_waves

# ("地震波文件路径", 时程时间间隔, "地震波名称(可选)")
wave_files = [
    (r"AW1-0.02.txt", 0.02, "AW1"),
    (r"BorregoMtn_NO_40-PW 8000 0.005.txt", 0.005),
]


xi = 0.05  # 阻尼比
am = 1.1  # 时程波加速度峰值(m/s^2)
Ts = np.arange(0.01, 6, 0.01)  # 谱周期横坐标，dt/Ts[i] <= 0.55时，Newmark-Beta算法收敛

# 加载地震时程数据
waves = load_waves.load_waves(wave_files)
# 绘制地震时程数据
# load_waves.plot_waves(waves)


# 计算地震响应谱并绘制
plt.rcParams['font.sans-serif'] = ['SIMSUN']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
SA = np.zeros((len(waves), len(Ts)))
for i in range(len(waves)):
    _, _, SA[i] = dynamic_calculator.nigam_jennings(waves[i], am, Ts, xi)
    SA[i] = SA[i] / 9.8
    ax.plot(Ts, SA[i], label=waves[i][2])
SAV = np.average(SA, axis=0)
ax.plot(Ts, SAV, label="均值反应谱")

ax.legend()
x_major_ticks = np.arange(0, 6.1, 1)
x_minor_ticks = np.arange(0, 6.1, 0.2)
y_major_ticks = np.arange(0, int(np.max(SA) * 10) / 10 + 0.11, 0.05)
y_minor_ticks = np.arange(0, int(np.max(SA) * 10) / 10 + 0.11, 0.01)
ax.set_xticks(x_major_ticks)
ax.set_xticks(x_minor_ticks, minor=True)
ax.set_yticks(y_major_ticks)
ax.set_yticks(y_minor_ticks, minor=True)
ax.grid(which='major', alpha=0.7)
ax.grid(which='minor', alpha=0.2)
ax.set_xlabel("t(s)")
ax.set_ylabel("a(g)")
plt.show()
