"""Task 241 — 核心变换：矩阵转置（H↔W 维度交换）。支持非方形网格。

架构: transpose (Transpose H<->W swap)
Baseline 参数: 0, 节点: 1
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


def build():
    nodes, inits = [], []
    nodes.append(helper.make_node("Transpose", ["input"], ["output"], perm=[0, 1, 3, 2]))
    x = helper.make_tensor_value_info("input", _DT, _GS)
    y = helper.make_tensor_value_info("output", _DT, _GS)
    g = helper.make_graph(nodes, "g", [x], [y], inits)
    return helper.make_model(g, ir_version=8,
                             opset_imports=[helper.make_opsetid("", 12)])

if __name__ == '__main__':
    task_num = 241
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
