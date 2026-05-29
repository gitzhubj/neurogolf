"""Task 073 — Blue(1) at row 2 falls to row 4, swapping with gray(5).

Architecture: Identity copy via 1x1 Conv, then Slice ch1 at row 2 to get
blue_mask, position it at rows 2 and 4 via Conv(1,1) with padding, then
Sub/Add to swap ch1 and ch5 between those two rows.

Grid is 5x5 at top-left of 30x30 canvas.
"""
import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu
import onnx

_CHANNELS, _HEIGHT, _WIDTH = 10, 30, 30
_GRID_SHAPE = [1, _CHANNELS, _HEIGHT, _WIDTH]
_DATA_TYPE = onnx.TensorProto.FLOAT
_IR_VERSION = 10
_OPSET_IMPORTS = [onnx.helper.make_opsetid("", 10)]


def build():
    nodes, inits = [], []

    # ── 1) Identity 1x1 Conv: copy input to base ──
    w_id = np.zeros((_CHANNELS, _CHANNELS, 1, 1), dtype=np.float32)
    for c in range(_CHANNELS):
        w_id[c, c, 0, 0] = 1.0
    w_id_init = onnx.helper.make_tensor(
        "W_id", _DATA_TYPE, [_CHANNELS, _CHANNELS, 1, 1],
        w_id.flatten().tolist()
    )
    inits.append(w_id_init)
    base_conv = onnx.helper.make_node(
        "Conv", ["input", "W_id"], ["base"],
        kernel_shape=[1, 1], pads=[0, 0, 0, 0]
    )
    nodes.append(base_conv)

    # ── 2) Slice ch1 at row 2 → blue_mask (1,1,1,30) ──
    # Opset 10 Slice: inputs=[data, starts, ends, axes, steps]
    sl_st = onnx.helper.make_tensor(
        "sl_st", onnx.TensorProto.INT64, [2], [1, 2]
    )
    sl_en = onnx.helper.make_tensor(
        "sl_en", onnx.TensorProto.INT64, [2], [2, 3]
    )
    sl_ax = onnx.helper.make_tensor(
        "sl_ax", onnx.TensorProto.INT64, [2], [1, 2]
    )
    inits.extend([sl_st, sl_en, sl_ax])
    blue_slice = onnx.helper.make_node(
        "Slice", ["input", "sl_st", "sl_en", "sl_ax"], ["blue_mask"]
    )
    nodes.append(blue_slice)

    # ── 3) Conv(1,1,1, weight=1.0) to position blue_mask ──
    w_pl = np.ones((1, 1, 1, 1), dtype=np.float32)
    w_pl_init = onnx.helper.make_tensor(
        "W_pl", _DATA_TYPE, [1, 1, 1, 1],
        w_pl.flatten().tolist()
    )
    inits.append(w_pl_init)

    # Position at row 2: pads=[top,left,bottom,right]
    row2_blue = onnx.helper.make_node(
        "Conv", ["blue_mask", "W_pl"], ["row2_blue"],
        kernel_shape=[1, 1], pads=[2, 0, 27, 0]
    )
    nodes.append(row2_blue)

    # Position at row 4
    row4_blue = onnx.helper.make_node(
        "Conv", ["blue_mask", "W_pl"], ["row4_blue"],
        kernel_shape=[1, 1], pads=[4, 0, 25, 0]
    )
    nodes.append(row4_blue)

    # ── 4) Channel selectors ──
    ch1_np = np.zeros((1, _CHANNELS, 1, 1), dtype=np.float32)
    ch1_np[0, 1, 0, 0] = 1.0
    ch1_init = onnx.helper.make_tensor(
        "ch1_w", _DATA_TYPE, [1, _CHANNELS, 1, 1],
        ch1_np.flatten().tolist()
    )
    ch1_sel = onnx.helper.make_node("Constant", [], ["ch1_sel"], value=ch1_init)
    nodes.append(ch1_sel)

    ch5_np = np.zeros((1, _CHANNELS, 1, 1), dtype=np.float32)
    ch5_np[0, 5, 0, 0] = 1.0
    ch5_init = onnx.helper.make_tensor(
        "ch5_w", _DATA_TYPE, [1, _CHANNELS, 1, 1],
        ch5_np.flatten().tolist()
    )
    ch5_sel = onnx.helper.make_node("Constant", [], ["ch5_sel"], value=ch5_init)
    nodes.append(ch5_sel)

    # ── 5) Project masks to channels ──
    # row2_blue_ch1 = blue_mask in ch1 at row 2  (to remove)
    # row2_blue_ch5 = blue_mask in ch5 at row 2  (to add)
    # row4_blue_ch5 = blue_mask in ch5 at row 4  (to remove)
    # row4_blue_ch1 = blue_mask in ch1 at row 4  (to add)
    r2b_c1 = onnx.helper.make_node("Mul", ["row2_blue", "ch1_sel"], ["r2b_c1"])
    nodes.append(r2b_c1)
    r2b_c5 = onnx.helper.make_node("Mul", ["row2_blue", "ch5_sel"], ["r2b_c5"])
    nodes.append(r2b_c5)
    r4b_c5 = onnx.helper.make_node("Mul", ["row4_blue", "ch5_sel"], ["r4b_c5"])
    nodes.append(r4b_c5)
    r4b_c1 = onnx.helper.make_node("Mul", ["row4_blue", "ch1_sel"], ["r4b_c1"])
    nodes.append(r4b_c1)

    # ── 6) Swap ch1 ↔ ch5 between rows 2 and 4 ──
    t1 = onnx.helper.make_node("Sub", ["base", "r2b_c1"], ["t1"])
    nodes.append(t1)
    t2 = onnx.helper.make_node("Add", ["t1", "r2b_c5"], ["t2"])
    nodes.append(t2)
    t3 = onnx.helper.make_node("Sub", ["t2", "r4b_c5"], ["t3"])
    nodes.append(t3)
    out = onnx.helper.make_node("Add", ["t3", "r4b_c1"], ["output"])
    nodes.append(out)

    # ── Build model ──
    x = onnx.helper.make_tensor_value_info("input", _DATA_TYPE, _GRID_SHAPE)
    y = onnx.helper.make_tensor_value_info("output", _DATA_TYPE, _GRID_SHAPE)
    graph_def = onnx.helper.make_graph(nodes, "graph", [x], [y], inits)
    return onnx.helper.make_model(
        graph_def, ir_version=_IR_VERSION, opset_imports=_OPSET_IMPORTS
    )


if __name__ == '__main__':
    task_num = 73
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
