import numpy as np


def newmark_beta_deprecated(wave, am, Ts, xi, beta=1/6, gamma=1/2):
    """newmark-beta 积分求解单自由度结构地震荷载下的响应
    :param wave: 地震时程
    :param am: 时程波加速度峰值(m/s^2)
    :param Ts: 谱周期
    :param xi: 阻尼比
    :param beta: newmark-beta 积分系数
    :param gamma: newmark-beta 积分系数
    """
    Tw, Ag, _ = wave  # 时程时间序列, 时程加速度序列, 时程名称
    dt = Tw[1] - Tw[0]  # 时程时间间隔
    Ag = Ag * am  # 时程加速度序列(放大到指定峰值)

    U_R = np.zeros(len(Ts))  # 结构相对位移谱
    V_R = np.zeros(len(Ts))  # 结构相对速度谱
    A = np.zeros(len(Ts))  # 结构绝对加速度谱

    # 1. 积分参数赋值
    n0 = 1 / (beta * dt ** 2)
    n1 = gamma / (beta * dt)
    n2 = 1 / (beta * dt)
    n3 = 1 / (2 * beta) - 1
    n4 = gamma / beta - 1
    n5 = dt / 2 * (gamma / beta - 2)
    # n6 = dt * (1 - gamma)
    # n7 = gamma * dt

    # 2. 初始化结构参数
    m = 1
    for i in range(len(Ts)):
        wn = 2 * np.pi / Ts[i]  # 无阻尼圆频率
        k = wn ** 2 * m
        c = 2 * m * wn * xi
        ke = k + n0 * m + n1 * c
        u0 = 0  # 初始位移
        v0 = 0  # 初始速度
        a0 = 0  # 初始加速度
        u_r = np.zeros(len(Tw))  # 结构相对位移(从时程第一个点开始)
        v_r = np.zeros(len(Tw))  # 结构相对速度(从时程第一个点开始)
        a_r = np.zeros(len(Tw))  # 结构相对加速度(从时程第一个点开始)
        a = np.zeros(len(Tw))  # 结构绝对加速度(从时程第一个点开始)
        u_r[0] = 1 / ke * (-m * Ag[0] + m * (n0 * u0 + n2 * v0 + n3 * a0) + c * (n1 * u0 + n4 * v0 + n5 * a0))
        v_r[0] = n1 * (u_r[0] - u0) - n4 * v0 - n5 * a0
        a_r[0] = n0 * (u_r[0] - u0) - n2 * v0 - n3 * a0
        # 3. newmark-beta 积分求解
        for j in range(1, len(Tw)):
            u_r[j] = 1 / ke * (-m * Ag[j] + m * (n0 * u_r[j - 1] + n2 * v_r[j - 1] + n3 * a_r[j - 1]) + c * (n1 * u_r[j - 1] + n4 * v_r[j - 1] + n5 * a_r[j - 1]))
            v_r[j] = n1 * (u_r[j] - u_r[j - 1]) - n4 * v_r[j - 1] - n5 * a_r[j - 1]
            a_r[j] = n0 * (u_r[j] - u_r[j - 1]) - n2 * v_r[j - 1] - n3 * a_r[j - 1]
            a[j] = a_r[j] + Ag[j]
        U_R[i] = np.max(np.abs(u_r))  # 结构最大位移
        V_R[i] = np.max(np.abs(v_r))  # 结构最大速度
        A[i] = np.max(np.abs(a))  # 结构最大加速度
    return U_R, V_R, A


def newmark_beta(wave, am, Ts, xi, beta=1/6, gamma=1/2):
    """newmark-beta 积分求解单自由度结构地震荷载下的响应
    :param wave: 地震时程
    :param am: 时程波加速度峰值(m/s^2)
    :param Ts: 谱周期
    :param xi: 阻尼比
    :param beta: newmark-beta 积分系数
    :param gamma: newmark-beta 积分系数
    """
    Tw, Ag, _ = wave  # 时程时间间隔, 时程时间序列, 时程加速度序列, 时程名称
    dt = Tw[1] - Tw[0]  # 时程时间间隔
    Ag = Ag * am  # 时程加速度序列(放大到指定峰值)

    # 初始化结构参数
    m = 1

    U_R = np.zeros(len(Ts))  # 结构相对位移谱
    V_R = np.zeros(len(Ts))  # 结构相对速度谱
    A = np.zeros(len(Ts))  # 结构绝对加速度谱

    for i in range(len(Ts)):
        wn = 2 * np.pi / Ts[i]  # 无阻尼圆频率
        k = wn ** 2 * m
        c = 2 * m * wn * xi
        # 1. 积分参数赋值
        n1 = m / (beta * dt ** 2) + c * gamma / (beta * dt)
        n2 = m / (beta * dt) + (gamma / beta - 1) * c
        n3 = (1/(2 * beta) - 1) * m + dt * (gamma / (2 * beta) - 1) * c
        k_hat = k + n1
        u_r = np.zeros(len(Tw))  # 结构相对位移(从时程第一个点开始)
        v_r = np.zeros(len(Tw))  # 结构相对速度(从时程第一个点开始)
        a_r = np.zeros(len(Tw))  # 结构相对加速度(从时程第一个点开始)
        a = np.zeros(len(Tw))  # 结构绝对加速度(从时程第一个点开始)
        a_r[0] = -Ag[0]
        for j in range(1, len(Tw)):
            p_e = -m * Ag[j] + n1 * u_r[j - 1] + n2 * v_r[j - 1] + n3 * a_r[j - 1]
            u_r[j] = p_e / k_hat
            v_r[j] = gamma / (beta * dt) * (u_r[j] - u_r[j - 1]) + (1 - gamma / beta) * v_r[j - 1] + dt * (1 - gamma / (2 * beta)) * a_r[j - 1]
            a_r[j] = 1 / (beta * dt ** 2) * (u_r[j] - u_r[j - 1]) - 1 / (beta * dt) * v_r[j - 1] - (1 / (2 * beta) - 1) * a_r[j - 1]
            a[j] = a_r[j] + Ag[j]

        U_R[i] = np.max(np.abs(u_r))  # 结构最大位移
        V_R[i] = np.max(np.abs(v_r))  # 结构最大速度
        A[i] = np.max(np.abs(a))  # 结构最大加速度
    return U_R, V_R, A


def nigam_jennings(wave, am, Ts, xi):
    """nigam_jennings 求解单自由度结构地震荷载下的响应
    :param wave: 地震时程
    :param am: 时程波加速度峰值(m/s^2)
    :param Ts: 谱周期
    :param xi: 阻尼比
    """
    Tw, Ag, _ = wave  # 时程时间间隔, 时程时间序列, 时程加速度序列, 时程名称
    dt = Tw[1] - Tw[0]  # 时程时间间隔
    Ag = Ag * am  # 时程加速度序列(放大到指定峰值)

    # 初始化结构参数
    # m = 1

    U_R = np.zeros(len(Ts))  # 结构相对位移谱
    V_R = np.zeros(len(Ts))  # 结构相对速度谱
    A = np.zeros(len(Ts))  # 结构绝对加速度谱

    for i in range(len(Ts)):
        wn = 2 * np.pi / Ts[i]  # 无阻尼圆频率
        wd = wn * np.sqrt(1 - xi ** 2)  # 阻尼圆频率
        # k = wn ** 2 * m
        # c = 2 * m * wn * xi
        # 参数赋值
        a11 = np.exp(-xi * wn * dt) * (xi / np.sqrt(1 - xi ** 2) * np.sin(wd * dt) + np.cos(wd * dt))
        a12 = np.exp(-xi * wn * dt) / wd * np.sin(wd * dt)
        a21 = -wn / np.sqrt(1 - xi ** 2) * np.exp(-xi * wn * dt) * np.sin(wd * dt)
        a22 = np.exp(-xi * wn * dt) * (np.cos(wd * dt) - xi / np.sqrt(1 - xi ** 2) * np.sin(wd * dt))
        b11 = np.exp(-xi * wn * dt) * (((2 * xi ** 2 - 1) / (wn ** 2 * dt) + xi / wn) * np.sin(wd * dt) / wd + (2 * xi / (wn ** 3 * dt) + 1 / wn ** 2) * np.cos(wd * dt)) - 2 * xi / (wn ** 3 * dt)
        b12 = -np.exp(-xi * wn * dt) * (((2 * xi ** 2 - 1) / (wn ** 2 * dt)) * np.sin(wd * dt) / wd + 2 * xi / (wn ** 3 * dt) * np.cos(wd * dt)) - 1 / wn ** 2 + 2 * xi / (wn ** 3 * dt)
        b21 = -1 / wn ** 2 * (-1 / dt + np.exp(-xi * wn * dt) * ((wn / np.sqrt(1 - xi ** 2) + xi / (dt * np.sqrt(1 - xi ** 2))) * np.sin(wd * dt) + 1 / dt * np.cos(wd * dt)))
        b22 = -1 / (wn ** 2 * dt) * (1 - np.exp(-xi * wn * dt)*(xi / np.sqrt(1 - xi ** 2) * np.sin(wd * dt) + np.cos(wd * dt)))
        u_r = np.zeros(len(Tw))  # 结构相对位移(从时程第一个点开始)
        v_r = np.zeros(len(Tw))  # 结构相对速度(从时程第一个点开始)
        a_r = np.zeros(len(Tw))  # 结构相对加速度(从时程第一个点开始)
        a = np.zeros(len(Tw))  # 结构绝对加速度(从时程第一个点开始)
        a_r[0] = -Ag[0]
        for j in range(1, len(Tw)):
            u_r[j] = a11 * u_r[j - 1] + a12 * v_r[j - 1] + b11 * Ag[j - 1] + b12 * Ag[j]
            v_r[j] = a21 * u_r[j - 1] + a22 * v_r[j - 1] + b21 * Ag[j - 1] + b22 * Ag[j]
            a_r[j] = -Ag[j] - wn ** 2 * u_r[j] - 2 * xi * wn * v_r[j]
            a[j] = a_r[j] + Ag[j]
        U_R[i] = np.max(np.abs(u_r))  # 结构最大位移
        V_R[i] = np.max(np.abs(v_r))  # 结构最大速度
        A[i] = np.max(np.abs(a))  # 结构最大加速度
    return U_R, V_R, A


def fft_sdof(wave, am, Ts, xi):
    """fft 求解单自由度结构地震荷载下的响应

    U(wn_bar * j) = F(wn_bar * j) * H(wn_bar * j);

    V(wn_bar * j) = U(wn_bar * j) * wn_bar * j;

    A(wn_bar * j) = V(wn_bar * j) * wn_bar * j = -U(wn_bar * j) * wn_bar ** 2

    其中:
        f(t) = -m * Ag(t)

        F(wn_bar * j) = -m * Agf(wn_bar * j)

    :param wave: 地震时程
    :param am: 时程波加速度峰值(m/s^2)
    :param Ts: 谱周期
    :param xi: 阻尼比
    """
    Tw, Ag, _ = wave  # 时程时间间隔, 时程时间序列, 时程加速度序列, 时程名称
    dt = Tw[1] - Tw[0]  # 时程时间间隔
    Ag = Ag * am  # 时程加速度序列(放大到指定峰值)

    # 为了加速傅里叶变换且获得更高精度，对时程进行补零处理，补零点数为2的整数次幂且大于或等于时程点数
    # 这是由于某些算法(例如 Cooley-Tukey/Radix-2)针对2的整数次幂的输入进行了优化
    Nfft = 2 ** (int(np.ceil(np.log2(len(Tw)))) + 0)  # fft点数，越多精度越高，但计算量也越大
    Agf = np.fft.fft(Ag, Nfft)  # 对地震动加速度序列作傅里叶变换
    f = np.fft.fftfreq(Nfft, d=dt)  # fft频率序列
    wn_bar = 2 * np.pi * f  # fft角频率序列

    # Agf = np.fft.fft(Ag)  # 对地震动加速度序列作傅里叶变换
    # f = np.fft.fftfreq(len(Ag), d=dt)  # fft频率序列
    # wn_bar = 2 * np.pi * f  # fft角频率序列

    U_R = np.zeros(len(Ts))  # 结构相对位移谱
    V_R = np.zeros(len(Ts))  # 结构相对速度谱
    A = np.zeros(len(Ts))  # 结构绝对加速度谱

    # 初始化结构参数
    m = 1

    for i in range(len(Ts)):
        wn = 2 * np.pi / Ts[i]  # 无阻尼圆频率
        k = wn ** 2 * m  # 刚度
        beta_n = wn_bar / wn
        # H = 1 / (wn ** 2 + 2 * wn_bar * xi * wn * 1j - wn_bar ** 2)  # fft传递函数
        H = (1 / k) * (1 / (1 - beta_n ** 2 + 2 * xi * beta_n * 1j))  # fft传递函数
        u_r = np.fft.ifft(-m * Agf * H).real  # 快速Fourier逆变换并取实部，结构相对位移
        v_r = np.fft.ifft(-m * Agf * H * wn_bar * 1j).real  # 快速Fourier逆变换并取实部，结构相对速度
        a = np.fft.ifft(-(-m * Agf * H) * wn_bar ** 2 + Agf).real  # 快速Fourier逆变换并取实部，结构绝对加速度
        U_R[i] = np.max(np.abs(u_r))  # 结构最大位移
        V_R[i] = np.max(np.abs(v_r))  # 结构最大速度
        A[i] = np.max(np.abs(a))  # 结构最大加速度
    return U_R, V_R, A
