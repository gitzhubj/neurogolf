"""Task 080 — 核心变换：以少数色为中心向四邻域填充十字形多数色，灰色(5)分隔线保持。

架构: conv_with_logic (unknown)
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

# 此任务架构较复杂 (conv_with_logic)，直接使用 baseline ONNX。
# 如需优化，参考 BASELINE_TECHNIQUES.md 和 NETWORK_BUILDING_GUIDE.md。

import shutil, onnx

def build():
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task080.onnx"))
    return model

if __name__ == '__main__':
    task_num = 80
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
