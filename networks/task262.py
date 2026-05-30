"""Task 262 — 核心变换：行内灰色定位：3x3每行灰色(5)所在列号决定整行颜色，列0->红(2)列1->黄(4)列2->绿(3)。

架构: gather_based_multi_op (Gather-based multi-op)
Baseline 参数: 6, 节点: 1
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

spatial_idx_data = np.array([0, 0, 0, 0, 27, 27], dtype=np.int64)
spatial_idx = helper.make_tensor(
    name="spatial_idx", data_type=onnx.TensorProto.INT64, dims=[6],
    vals=spatial_idx_data.flatten().tolist())


def build():
    nodes, inits = [], []
    inits.append(spatial_idx)
    nodes.append(helper.make_node("Gather", ["input", "spatial_idx"], ["output"], axis=2))
    x = helper.make_tensor_value_info("input", _DT, _GS)
    y = helper.make_tensor_value_info("output", _DT, _GS)
    g = helper.make_graph(nodes, "g", [x], [y], inits)
    return helper.make_model(g, ir_version=8,
                             opset_imports=[helper.make_opsetid("", 16)])

if __name__ == '__main__':
    task_num = 262
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
