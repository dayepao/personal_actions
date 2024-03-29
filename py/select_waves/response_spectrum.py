import tomllib

import matplotlib.pyplot as plt
import numpy as np

import calculate_code_alpha
import dynamic_solver
import load_waves
import utils_sw

# pip install numba


# 读取选取的地震波信息和结构前n个周期
with open(utils_sw.get_self_dir()[1] / "selected_waves.toml", "rb") as f:
    selected_waves_toml: dict = tomllib.load(f)

selected_waves: list = selected_waves_toml.get("selected_waves")
T: list = selected_waves_toml.get("T")


# {"name (可选)": "名称", "file": 时程文件路径, "dt": 时程时间间隔, "skiprows (可选)": 跳过行数}
# selected_waves.extend(
#     [
#         {"name": "人工波1", "file": r"RH2TG040_z.txt", "dt": 0.02},
#         {"name": "人工波2", "file": r"AW1-0.02.txt", "dt": 0.02},
#     ]
# )
# 结构前n个周期
# T = [2.833, 2.808, 2.361, 2.782, 2.761, 2.329]  # luding
# T.extend([2.184, 2.172, 2.038, 2.242, 2.227, 2.103])

# 存储选取的地震波信息和结构前n个周期
# with open(utils_sw.get_self_dir()[1] / "selected_waves.yaml", "w", encoding="utf-8") as f:
#     yaml.dump({"selected_waves": selected_waves, "T": T}, f, allow_unicode=True, width=1000, sort_keys=False)


xi = 0.05  # 阻尼比
alpha_max = 0.24  # 地震影响系数最大值
am = 1.1  # 时程波加速度峰值(m/s^2)
Tg = 0.4  # 场地特征周期

is_ms2 = False  # 是否使用m/s^2为单位

Ts = np.arange(0.01, 6 + 1e-4, 0.01)  # 谱周期序列，dt/Ts[i] <= 0.55时，Newmark-Beta算法收敛


# 加载地震时程数据
waves = load_waves.load_waves(selected_waves)
# 绘制地震时程数据
# load_waves.plot_waves(waves)

# 创建画布
plt.rcParams["font.sans-serif"] = ["SIMSUN"]  # 用来正常显示中文标签
plt.rcParams["axes.unicode_minus"] = False  # 用来正常显示负号
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)

# 生成规范反应谱并绘制
alpha: np.ndarray = np.vectorize(calculate_code_alpha.calculate_code_alpha_gbt51408)(alpha_max, Tg, xi, Ts)
SA_code = alpha if not is_ms2 else alpha * 9.81
ax.plot(Ts, SA_code, label="规范设计加速度反应谱", color="#000000", linewidth=2)


# 计算地震反应谱并绘制
SA = np.zeros((len(waves), len(Ts)))
for i in range(len(waves)):
    print("({}/{}) 正在计算 {} 的反应谱...".format(i + 1, len(waves), waves[i][2]))
    _, _, SA[i] = np.vectorize(dynamic_solver.get_res, excluded=["wave"])(wave=waves[i], am=am, xi=xi, T=Ts)
    SA[i][SA[i] > 1e4] = np.nan
    SA[i] = SA[i] if is_ms2 else SA[i] / 9.81
    ax.plot(Ts, SA[i], label=waves[i][2], color="#505050", linewidth=0.5, alpha=0.8)  # 画出反应谱
    # 输出反应谱 CSV 文件
    # utils_sw.write_lists_to_csv(utils_sw.get_self_dir()[1] / "output" / f"RES_{waves[i][2]}.csv", Ts, SA[i])
    print(f"{' ' * (len(str(i + 1)) + len(str(len(waves))) + 4)}{waves[i][2]} 反应谱指定周期点与规范谱误差为: {str(utils_sw.get_deviation_at_T(T, Ts, SA[i], SA_code))}") if T else None
    # _, _, A = dynamic_solver.fft_sdof(waves[i], am, Ts, xi)
    # A = A / 9.81
    # ax.plot(Ts, A, label=waves[i][2]+"(FFT)")
SAV = np.average(SA, axis=0)
ax.plot(Ts, SAV, label="均值反应谱", color="#FF0000", linewidth=2, linestyle="--")
print(f"\n均值反应谱 指定周期点与规范谱误差为: {str(utils_sw.get_deviation_at_T(T, Ts, SAV, SA_code))}") if T else None

ax.legend()
x_major_ticks, x_minor_ticks, y_major_ticks, y_minor_ticks = utils_sw.get_axis_ticks(Ts, SA)
ax.set_xlim(0, np.max(x_major_ticks))
ax.set_ylim(0, np.max(y_major_ticks))
ax.set_xticks(x_major_ticks)
ax.set_xticks(x_minor_ticks, minor=True)
ax.set_yticks(y_major_ticks)
ax.set_yticks(y_minor_ticks, minor=True)
ax.grid(which="major", alpha=0.7)
ax.grid(which="minor", alpha=0.2)
ax.set_xlabel("T(s)")
ax.set_ylabel("a(m/s$^2$)") if is_ms2 else ax.set_ylabel("a(g)")
plt.show()
