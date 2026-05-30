"""Task 276 — 核心变换：单颜色替换。所有颜色 6 替换为 2，其余颜色不变。

架构: gather_lookup (Gather channel lookup)
Baseline 参数: 10, 节点: 1
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

color_idx_data = np.array([0, 1, 6, 3, 4, 5, 2, 7, 8, 9], dtype=np.int64)
color_idx = helper.make_tensor(
    name="color_idx", data_type=onnx.TensorProto.INT64, dims=[10],
    vals=color_idx_data.flatten().tolist())


def build():
    nodes, inits = [], []
    inits.append(color_idx)
    nodes.append(helper.make_node("Gather", ["input", "color_idx"], ["output"], axis=1))
    x = helper.make_tensor_value_info("input", _DT, _GS)
    y = helper.make_tensor_value_info("output", _DT, _GS)
    g = helper.make_graph(nodes, "g", [x], [y], inits)
    return helper.make_model(g, ir_version=8,
                             opset_imports=[helper.make_opsetid("", 17)])

if __name__ == '__main__':
    task_num = 276
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
