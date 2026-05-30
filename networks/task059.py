"""Task 059 — 核心变换：区域填充。对每个被灰线分隔的子区域（3×3 或 3×4 等），统计该区域内出现的非零、非灰颜色的数量。该子区域在输出中被整体填充为该区域中出现次数最多的颜色（或其他基于全局的投票规则）。

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
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task059.onnx"))
    return model

if __name__ == '__main__':
    task_num = 59
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
