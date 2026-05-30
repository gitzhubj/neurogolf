"""Task 116 — 核心变换：垂直镜像扩展。输入 3 行 → 输出 6 行。

架构: gather_spatial (Gather spatial permutation)
Baseline 参数: 30, 节点: 1
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

spatial_idx_data = np.array([2, 1, 0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], dtype=np.int64)
spatial_idx = helper.make_tensor(
    name="spatial_idx", data_type=onnx.TensorProto.INT64, dims=[30],
    vals=spatial_idx_data.flatten().tolist())


def build():
    nodes, inits = [], []
    inits.append(spatial_idx)
    nodes.append(helper.make_node("Gather", ["input", "spatial_idx"], ["output"], axis=2))
    x = helper.make_tensor_value_info("input", _DT, _GS)
    y = helper.make_tensor_value_info("output", _DT, _GS)
    g = helper.make_graph(nodes, "g", [x], [y], inits)
    return helper.make_model(g, ir_version=8,
                             opset_imports=[helper.make_opsetid("", 12)])

if __name__ == '__main__':
    task_num = 116
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
