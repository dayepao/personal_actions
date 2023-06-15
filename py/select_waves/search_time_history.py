import re
from pathlib import Path

import dynamic_solver
import load_waves
import numpy as np
import utils_sw

# pip install pyyaml
# pip install numba


# 读取选取的地震波信息和结构前n个周期
target_time_history = [
    {"name": "Target", "file": r"WhittierNarrows-01_NO_618-PW 1460 0.02.txt", "dt": 0.02},
]
search_dir = Path(r"PEERNGARecords_Unscaled")


T = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]
xi = 0.05  # 阻尼比
alpha_max = 0.24  # 地震影响系数最大值
am = 1.1  # 时程波加速度峰值(m/s^2)
Tg = 0.4  # 场地特征周期

is_ms2 = False  # 是否使用m/s^2为单位

Ts = np.arange(0.01, 6 + 1e-4, 0.01)  # 谱周期序列，dt/Ts[i] <= 0.55时，Newmark-Beta算法收敛


candidate_time_history = []
for time_history in search_dir.glob("*.txt"):
    candidate_time_history.append({"name": time_history.name, "file": time_history, "dt": float(re.search(r"_([\d\.]+)\.txt", time_history.name).group(1))})

# 加载地震时程数据
target_wave = load_waves.load_waves(target_time_history)
waves = load_waves.load_waves(candidate_time_history)

# 计算目标时程的反应谱
_, _, SA_target = np.vectorize(dynamic_solver.get_res, excluded=["wave"])(wave=target_wave[0], am=am, xi=xi, T=Ts)
SA_target[SA_target > 1e4] = np.nan
SA_target = SA_target if is_ms2 else SA_target / 9.81


# 计算地震反应谱并绘制
SA = np.zeros((len(waves), len(Ts)))
for i in range(len(waves)):
    # print("({}/{}) 正在计算 {} 的反应谱...".format(i + 1, len(waves), waves[i][2]))
    _, _, SA[i] = np.vectorize(dynamic_solver.get_res, excluded=["wave"])(wave=waves[i], am=am, xi=xi, T=Ts)
    SA[i][SA[i] > 1e4] = np.nan
    SA[i] = SA[i] if is_ms2 else SA[i] / 9.81
    if all(float(error[1].rstrip("%")) < 5 for error in utils_sw.get_deviation_at_T(T, Ts, SA[i], SA_target)):
        print("找到匹配的地震波：{}".format(waves[i][2]))
