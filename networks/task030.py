"""Task 030 — 核心变换：重力沉降 — 每个连通块在垂直方向下移，直到碰到网格底部或碰到其他已下沉的块为止。块内形状在沉降过程中保持不变，水平位置（列坐标）保持不变。

架构: reduce_with_where (unknown)
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

# 此任务架构较复杂 (reduce_with_where)，直接使用 baseline ONNX。
# 如需优化，参考 BASELINE_TECHNIQUES.md 和 NETWORK_BUILDING_GUIDE.md。

import shutil, onnx

def build():
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task030.onnx"))
    return model

if __name__ == '__main__':
    task_num = 30
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
