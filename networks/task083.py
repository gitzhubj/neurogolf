"""Task 083 — 核心变换：2×2 对称平铺。将 3×4 输入作为左上象限，通过镜像生成其余三个象限。

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
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task083.onnx"))
    return model

if __name__ == '__main__':
    task_num = 83
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
