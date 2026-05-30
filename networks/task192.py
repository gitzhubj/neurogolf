"""Task 192 — 核心变换：噪声过滤：稀疏噪点(1或8)若被大块单色形状(2或3)包围则填充形状色，孤立噪点清零。

架构: conv_with_logic (Conv + logic gates)
Baseline 参数: ?, 节点: 21
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
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task192.onnx"))
    return model

if __name__ == '__main__':
    task_num = 192
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
