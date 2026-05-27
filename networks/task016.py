"""Task 016 — 逐像素颜色交换 (4-pair swap) via 1×1 Conv"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import neurogolf_utils as nu

MAPPING = {1: 5, 5: 1, 2: 6, 6: 2, 3: 4, 4: 3, 8: 9, 9: 8}


def weight_fn(ch_out, ch_in, kernel_coord):
    if kernel_coord == (0, 0):
        if ch_in in MAPPING and ch_out == MAPPING[ch_in]:
            return 1.0
        if ch_in not in MAPPING and ch_in == ch_out:
            return 1.0
    return 0.0


def build():
    return nu.single_layer_conv2d_network(weight_fn, kernel_size=1)


if __name__ == '__main__':
    task_num = 16
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
