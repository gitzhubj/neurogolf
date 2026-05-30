"""Task 040 — 核心变换：绿色(3)替换为距离最近边框的颜色，按行列距离判断归属。

架构: reduce_with_where (unknown)
Baseline 参数: ?, 节点: ?
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

# 此任务架构较复杂 (reduce_with_where)，直接使用 baseline ONNX。
# 如需优化，参考 BASELINE_TECHNIQUES.md 和 NETWORK_BUILDING_GUIDE.md。

import shutil, onnx

def build():
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task040.onnx"))
    return model

if __name__ == '__main__':
    task_num = 40
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
