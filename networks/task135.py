"""Task 135 — 核心变换：从 9x9 输入中裁出右下角 3x3 子区域。

架构: slice_pad (Slice + Pad crop/flip/reposition)
Baseline 参数: 12, 节点: 2
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
    # Slice: extract sub-region
    starts = np.array([0, 0], dtype=np.int64)
    ends = np.array([3, 3], dtype=np.int64)
    axes = np.array([2, 3], dtype=np.int64)
    steps = np.array([1, 1], dtype=np.int64)
    s_init = helper.make_tensor("starts", onnx.TensorProto.INT64, [2], starts)
    e_init = helper.make_tensor("ends", onnx.TensorProto.INT64, [2], ends)
    a_init = helper.make_tensor("axes", onnx.TensorProto.INT64, [2], axes)
    st_init = helper.make_tensor("steps", onnx.TensorProto.INT64, [2], steps)
    for t in [s_init, e_init, a_init, st_init]:
        inits.append(t)
    nodes.append(helper.make_node("Slice", ["input", "starts", "ends", "axes", "steps"], ["cropped"]))

    # Pad: restore to 30x30
    pads = np.array([0, 0, 0, 0, 0, 0, 27, 27], dtype=np.int64)
    p_init = helper.make_tensor("pads", onnx.TensorProto.INT64, [8], pads)
    inits.append(p_init)
    nodes.append(helper.make_node("Pad", ["cropped", "pads"], ["output"], mode="constant", value=0.0))

    x = helper.make_tensor_value_info("input", _DT, _GS)
    y = helper.make_tensor_value_info("output", _DT, _GS)
    g = helper.make_graph(nodes, "g", [x], [y], inits)
    return helper.make_model(g, ir_version=8,
                             opset_imports=[helper.make_opsetid("", 10)])

if __name__ == '__main__':
    task_num = 135
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
