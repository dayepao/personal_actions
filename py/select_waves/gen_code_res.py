import numpy as np


def gen_code_res_gb50011(alpha_max, Tg, xi, Ts):
    """生成GB50011-2010 《建筑抗震设计规范》中的反应谱
    :param alpha_max: 地震影响系数最大值
    :param Tg: 场地特征周期
    :param xi: 阻尼比
    :param Ts: 谱周期序列
    :return: alpha"""
    # 计算参数
    gamma = 0.9 + (0.05 - xi) / (0.3 + 6 * xi)
    eta_1 = 0.02 + (0.05 - xi) / (4 + 32 * xi)
    eta_2 = 1 + (0.05 - xi) / (0.08 + 1.6 * xi)

    # 生成规范反应谱
    alpha = np.zeros_like(Ts)
    alpha[Ts <= 0.1] = np.interp(Ts[Ts <= 0.1], [0, 0.1], [0.45 * alpha_max, eta_2 * alpha_max])
    alpha[(Ts > 0.1) & (Ts <= Tg)] = eta_2 * alpha_max
    alpha[(Ts > Tg) & (Ts <= 5 * Tg)] = (Tg / Ts[(Ts > Tg) & (Ts <= 5 * Tg)]) ** gamma * eta_2 * alpha_max
    alpha[(Ts > 5 * Tg) & (Ts <= 6)] = np.abs(eta_2 * 0.2 ** gamma - eta_1 * (Ts[(Ts > 5 * Tg) & (Ts <= 6)] - 5 * Tg)) * alpha_max

    return alpha


if __name__ == '__main__':
    alpha = gen_code_res_gb50011(0.24, 0.4, 0.05, np.arange(0.01, 6, 0.01))
    print(alpha)
