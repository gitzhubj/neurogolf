"""Task 089 — 核心变换：将源图案复制到每个目标标记格的位置。目标标记格的颜色用于确定图案的锚点（即图案中哪种颜色应对齐到标记位置）。

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
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task089.onnx"))
    return model

if __name__ == '__main__':
    task_num = 89
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
