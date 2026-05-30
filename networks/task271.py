"""Task 271 — 核心变换：最大蓝点分量：9x9中4个3x3连通分量，选取蓝色(1)像素最多的分量输出。

架构: conv_with_logic (Conv + logic gates)
Baseline 参数: ?, 节点: 22
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
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task271.onnx"))
    return model

if __name__ == '__main__':
    task_num = 271
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
