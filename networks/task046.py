"""Task 046 — 核心规则：5 标记了"分配通道"。row 1 包含彩色块（可以是一种或多种颜色），被 5 分隔。row 0 和 row 2 中的 5 标记了目标位置——row 0 的 5 将 row 1 的块"拉"到

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
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task046.onnx"))
    return model

if __name__ == '__main__':
    task_num = 46
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
