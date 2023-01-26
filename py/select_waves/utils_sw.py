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


if __name__ == '__main__':
    Ts = np.arange(0, 6, 0.01)
    SA = np.array(0.4)
    print(get_axis_ticks(Ts, SA))
