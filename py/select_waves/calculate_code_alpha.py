import numpy as np


def calculate_code_alpha_gb50011(alpha_max, Tg, xi, T):
    """计算《建筑抗震设计规范》(GB 50011-2010) 中的地震影响系数
    :param alpha_max: 地震影响系数最大值
    :param Tg: 场地特征周期
    :param xi: 阻尼比
    :param T: 结构自振周期
    :return: alpha"""
    # 计算参数
    gamma = 0.9 + (0.05 - xi) / (0.3 + 6 * xi)
    eta_1 = 0.02 + (0.05 - xi) / (4 + 32 * xi)
    eta_2 = 1 + (0.05 - xi) / (0.08 + 1.6 * xi)

    # 计算地震影响系数
    if 0 <= T < 0.1:
        alpha = np.interp(T, [0, 0.1], [0.45 * alpha_max, eta_2 * alpha_max])
    elif 0.1 <= T < Tg:
        alpha = eta_2 * alpha_max
    elif Tg <= T < 5 * Tg:
        alpha = (Tg / T) ** gamma * eta_2 * alpha_max
    elif 5 * Tg <= T <= 6:
        alpha = np.abs(eta_2 * 0.2 ** gamma - eta_1 * (T - 5 * Tg)) * alpha_max
    else:
        alpha = np.nan

    return alpha


def calculate_code_alpha_gbt51408(alpha_max, Tg, xi, T):
    """计算《建筑隔震设计标准》(GB/T 51408-2021) 中的地震影响系数
    :param alpha_max: 地震影响系数最大值
    :param Tg: 场地特征周期
    :param xi: 阻尼比
    :param T: 结构自振周期
    :return: alpha"""
    # 计算参数
    gamma = 0.9 + (0.05 - xi) / (0.3 + 6 * xi)
    eta = 1 + (0.05 - xi) / (0.08 + 1.6 * xi)

    # 计算地震影响系数
    if 0 <= T < 0.1:
        alpha = np.interp(T, [0, 0.1], [0.45 * alpha_max, eta * alpha_max])
    elif 0.1 <= T < Tg:
        alpha = eta * alpha_max
    elif Tg <= T <= 6:
        alpha = (Tg / T) ** gamma * eta * alpha_max
    else:
        alpha = np.nan

    return alpha


if __name__ == '__main__':
    alpha = calculate_code_alpha_gbt51408(0.24, 0.4, 0.05, 5)
    print(alpha)
