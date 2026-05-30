"""Task 024 — 核心变换：颜色 1 和 3 的锚点填充其所在整行；颜色 2 的锚点填充其所在整列。行填充（1, 3）优先于列填充（2）。

架构: reduce_only (unknown)
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

# 此任务架构较复杂 (reduce_only)，直接使用 baseline ONNX。
# 如需优化，参考 BASELINE_TECHNIQUES.md 和 NETWORK_BUILDING_GUIDE.md。

import shutil, onnx

def build():
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task024.onnx"))
    return model

if __name__ == '__main__':
    task_num = 24
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
