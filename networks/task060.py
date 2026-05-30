"""Task 060 — 核心变换：对每一对有颜色端点的行，从左端点的颜色开始，填充该行左半部分（col 0 到 col 4）；在正中间列（col 5）填充颜色 5（灰色分隔符）；从 col 6 到 col 10 填充右端点的

架构: custom_multi_op (unknown)
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

# 此任务架构较复杂 (custom_multi_op)，直接使用 baseline ONNX。
# 如需优化，参考 BASELINE_TECHNIQUES.md 和 NETWORK_BUILDING_GUIDE.md。

import shutil, onnx

def build():
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task060.onnx"))
    return model

if __name__ == '__main__':
    task_num = 60
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
