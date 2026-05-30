"""Task 009 — 核心变换：对象水平压实——将网格中的同色 8-连通对象向左滑动，消除对象之间（及对象与左边界之间）的水平空白列。对象保持各自形状、颜色和垂直位置，仅水平平移。

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
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task009.onnx"))
    return model

if __name__ == '__main__':
    task_num = 9
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
