"""Task 072 — XOR of top and bottom halves separated by yellow row.

Input: 13x5 grid. Row 6 (zero-indexed) is yellow(4) separator.
Top half: rows 0-5, Bottom half: rows 7-12.
Output: 6x5 grid. Green(3) where exactly one of {top,bottom} has red(2).

Architecture: Conv(8,1) simultaneously reads top red (dh=0) and
bottom red (dh=7) → Abs difference → map to channels 3 and 0.
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

    # 1) Conv(8,1) with two active channels:
    #    ch0 = top red (input ch2, dh=0), ch1 = bottom red (input ch2, dh=7)
    k_h, k_w = 8, 1
    w_shape = [_CHANNELS, _CHANNELS, k_h, k_w]
    w_data = np.zeros(w_shape, dtype=np.float32)
    w_data[0, 2, 0, 0] = 1.0   # ch0 ← input ch2 at same row (top)
    w_data[1, 2, 7, 0] = 1.0   # ch1 ← input ch2 at row+7 (bottom)
    # Weight for channels 2-9 remain zero (unused)
    w_init = onnx.helper.make_tensor("W1", _DATA_TYPE, w_shape,
                                      w_data.flatten().tolist())
    inits.append(w_init)

    conv = onnx.helper.make_node(
        "Conv", ["input", "W1"], ["conv_out"],
        kernel_shape=[k_h, k_w],
        pads=[0, 0, k_h - 1, 0]   # pad bottom so output is 30x30
    )
    nodes.append(conv)

    # 2) Slice top_red (ch0) and bottom_red (ch1) from conv_out
    # Opset 10 Slice: inputs=[data, starts, ends, axes, steps]
    sl_starts = onnx.helper.make_tensor("sl_st", onnx.TensorProto.INT64, [1], [0])
    sl_ends = onnx.helper.make_tensor("sl_en", onnx.TensorProto.INT64, [1], [1])
    sl_axes = onnx.helper.make_tensor("sl_ax", onnx.TensorProto.INT64, [1], [1])
    inits.extend([sl_starts, sl_ends, sl_axes])

    top_red = onnx.helper.make_node(
        "Slice", ["conv_out", "sl_st", "sl_en", "sl_ax"], ["top_red"]
    )
    nodes.append(top_red)

    sl_starts2 = onnx.helper.make_tensor("sl_st2", onnx.TensorProto.INT64, [1], [1])
    sl_ends2 = onnx.helper.make_tensor("sl_en2", onnx.TensorProto.INT64, [1], [2])
    inits.extend([sl_starts2, sl_ends2])

    bot_red = onnx.helper.make_node(
        "Slice", ["conv_out", "sl_st2", "sl_en2", "sl_ax"], ["bot_red"]
    )
    nodes.append(bot_red)

    # 3) XOR = Abs(top_red - bot_red)
    diff = onnx.helper.make_node("Sub", ["top_red", "bot_red"], ["diff"])
    nodes.append(diff)
    xor_val = onnx.helper.make_node("Abs", ["diff"], ["xor_val"])
    nodes.append(xor_val)

    # 4) Grid mask (1,1,30,30) for output rows 0-5, cols 0-4
    grid_mask_np = np.zeros((1, 1, _HEIGHT, _WIDTH), dtype=np.float32)
    grid_mask_np[0, 0, 0:6, 0:5] = 1.0
    gm_init = onnx.helper.make_tensor("gm", _DATA_TYPE, [1, 1, _HEIGHT, _WIDTH],
                                       grid_mask_np.flatten().tolist())
    gm_node = onnx.helper.make_node("Constant", [], ["gm_const"], value=gm_init)
    nodes.append(gm_node)

    # 5) Mask XOR to grid area
    xm = onnx.helper.make_node("Mul", ["xor_val", "gm_const"], ["xm"])
    nodes.append(xm)
    # Not-XOR (channel 0) within grid
    nxm = onnx.helper.make_node("Sub", ["gm_const", "xm"], ["nxm"])
    nodes.append(nxm)

    # 6) Channel selectors
    ch3_sel_np = np.zeros((1, _CHANNELS, 1, 1), dtype=np.float32)
    ch3_sel_np[0, 3, 0, 0] = 1.0
    ch3_init = onnx.helper.make_tensor("ch3_w", _DATA_TYPE,
                                        [1, _CHANNELS, 1, 1],
                                        ch3_sel_np.flatten().tolist())
    ch3_node = onnx.helper.make_node("Constant", [], ["ch3_sel"], value=ch3_init)
    nodes.append(ch3_node)

    ch0_sel_np = np.zeros((1, _CHANNELS, 1, 1), dtype=np.float32)
    ch0_sel_np[0, 0, 0, 0] = 1.0
    ch0_init = onnx.helper.make_tensor("ch0_w", _DATA_TYPE,
                                        [1, _CHANNELS, 1, 1],
                                        ch0_sel_np.flatten().tolist())
    ch0_node = onnx.helper.make_node("Constant", [], ["ch0_sel"], value=ch0_init)
    nodes.append(ch0_node)

    # 7) Place into output channels
    ch3_out = onnx.helper.make_node("Mul", ["xm", "ch3_sel"], ["ch3_out"])
    nodes.append(ch3_out)
    ch0_out = onnx.helper.make_node("Mul", ["nxm", "ch0_sel"], ["ch0_out"])
    nodes.append(ch0_out)
    output = onnx.helper.make_node("Add", ["ch3_out", "ch0_out"], ["output"])
    nodes.append(output)

    x = onnx.helper.make_tensor_value_info("input", _DATA_TYPE, _GRID_SHAPE)
    y = onnx.helper.make_tensor_value_info("output", _DATA_TYPE, _GRID_SHAPE)
    graph_def = onnx.helper.make_graph(nodes, "graph", [x], [y], inits)
    return onnx.helper.make_model(graph_def, ir_version=_IR_VERSION,
                                   opset_imports=_OPSET_IMPORTS)


if __name__ == '__main__':
    task_num = 72
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
