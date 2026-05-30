"""Task 186 — 核心变换：计数填充：统计3x3中蓝色(1)像素数N，按固定顺序填充N个红色(2)像素。

架构: reduce_only (Reduce + arithmetic)
Baseline 参数: ?, 节点: 6
"""
import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu
import onnx
from onnx import helper

_CH, _H, _W = 10, 30, 30
_GS = [1, _CH, _H, _W]
_DT = onnx.TensorProto.FLOAT

# 此任务架构较复杂 (reduce_only)，直接使用 baseline ONNX。
# 如需优化，参考 BASELINE_TECHNIQUES.md 和 NETWORK_BUILDING_GUIDE.md。

import shutil, onnx

def build():
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task186.onnx"))
    return model

if __name__ == '__main__':
    task_num = 186
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
