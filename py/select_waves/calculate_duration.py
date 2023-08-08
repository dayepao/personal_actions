import numpy as np
import yaml

import utils_sw
from load_waves import load_waves


def calculate_duration(waves):
    for wave in waves:
        max_acc = np.max(np.abs(wave[1]))
        t1_index = 0
        for i in range(len(wave[1])):
            if np.abs(wave[1][i]) < 0.1 * max_acc:
                continue
            t1_index = i
            break
        t2_index = 0
        for i in reversed(range(len(wave[1]))):
            if np.abs(wave[1][i]) < 0.1 * max_acc:
                continue
            t2_index = i
            break
        print(f"{wave[2]} 时程 总时长 {wave[0][-1]:.1f} s, 持续时间 {wave[0][t2_index] - wave[0][t1_index]:.1f} s")


if __name__ == "__main__":
    # 读取选取的地震波信息和结构前n个周期
    with open(utils_sw.get_self_dir()[1] / "selected_waves.yaml", "r", encoding="utf-8") as f:
        selected_waves_yaml: dict = yaml.load(f, Loader=yaml.FullLoader)

    selected_waves: list = selected_waves_yaml.get("selected_waves")
    T: list = selected_waves_yaml.get("T")

    # 加载地震时程数据
    waves = load_waves(selected_waves)

    calculate_duration(waves)
