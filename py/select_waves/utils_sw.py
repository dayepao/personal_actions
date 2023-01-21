import numpy as np


def get_deviation_at_T(T, Ts, SA_i, alpha):
    """
    计算反应谱在指定周期T的偏差
    :param T: 指定周期列表
    :param Ts: 反应谱周期
    :param SA_i: 时程反应谱加速度
    :param alpha: 规范反应谱加速度
    :return: [(Ts[idx], SAV[idx])]
    """
    deviation = []
    for i in range(len(T)):
        idx = np.argmin(np.abs(Ts - T[i]))
        # deviation.append((np.round(Ts[idx], len(str(Ts[1] - Ts[0]).split(".")[1])), str(np.abs(SA_i[idx] - alpha[idx]) / alpha[idx] * 100) + "%"))
        deviation.append((T[i], str(np.round(np.abs(SA_i[idx] - alpha[idx]) / alpha[idx] * 100, 2)) + "%"))
    return deviation
