"""Task 130 — 核心变换：多数投票：9x9划分为9个3x3块，每块取多数颜色输出（忽略灰色5）。

架构: conv_with_logic (Conv + logic gates)
Baseline 参数: ?, 节点: 10
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

# 此任务架构较复杂 (conv_with_logic)，直接使用 baseline ONNX。
# 如需优化，参考 BASELINE_TECHNIQUES.md 和 NETWORK_BUILDING_GUIDE.md。

import shutil, onnx

def build():
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task130.onnx"))
    return model

if __name__ == '__main__':
    task_num = 130
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
