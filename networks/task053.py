"""Task 053 — Shift down by 1 row.

Architecture: 3x3 Conv (shift colors down) + Constant (restore bg at top row).
Grid is always 3x3, placed at top-left of 30x30 canvas.
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

    # 3x3 Conv: shift ALL channels (including bg) down by 1 row
    def wf(ch_out, ch_in, kc):
        if kc == (-1, 0) and ch_out == ch_in:
            return 1.0
        return 0.0

    # Build Conv weight tensor
    k = 3
    offsets = list(range(-k // 2 + 1, k // 2 + 1))
    import itertools
    w_shape = [_CHANNELS, _CHANNELS, k, k]
    cells = itertools.product(range(_CHANNELS), range(_CHANNELS), offsets, offsets)
    weights = [float(wf(o, i, (r, c))) for (o, i, r, c) in cells]

    w_init = onnx.helper.make_tensor("W1", _DATA_TYPE, w_shape, weights)
    conv_node = onnx.helper.make_node(
        "Conv", ["input", "W1"], ["conv_out"],
        kernel_shape=[k, k], pads=[k // 2] * 4
    )
    nodes.append(conv_node); inits.append(w_init)

    # Constant: restore bg at vacated top row (cols 0-2)
    bg_data = np.zeros(_GRID_SHAPE, dtype=np.float32)
    bg_data[0, 0, 0, 0:3] = 1.0  # ch0, row0, cols 0-2
    bg_init = onnx.helper.make_tensor("bg_fix", _DATA_TYPE, _GRID_SHAPE,
                                       bg_data.flatten().tolist())
    bg_node = onnx.helper.make_node("Constant", [], ["bg_fix"],
                                     value=bg_init)
    nodes.append(bg_node)

    # Add: combine shifted output with bg restoration
    add_out = "added"
    add_node = onnx.helper.make_node("Add", ["conv_out", "bg_fix"], [add_out])
    nodes.append(add_node)

    # Constant mask: zero out overflow at row 3 (shifted content from row 2
    # shouldn't extend beyond the 3x3 grid boundary)
    mask_data = np.ones(_GRID_SHAPE, dtype=np.float32)
    mask_data[0, :, 3, 0:3] = 0.0  # all channels, row3, cols 0-2 = 0
    mask_init = onnx.helper.make_tensor("mask", _DATA_TYPE, _GRID_SHAPE,
                                         mask_data.flatten().tolist())
    mask_node = onnx.helper.make_node("Constant", [], ["mask_const"],
                                       value=mask_init)
    nodes.append(mask_node)

    # Mul: apply mask to cancel row 3 overflow
    mul_node = onnx.helper.make_node("Mul", [add_out, "mask_const"], ["output"])
    nodes.append(mul_node)

    # Build model
    x = onnx.helper.make_tensor_value_info("input", _DATA_TYPE, _GRID_SHAPE)
    y = onnx.helper.make_tensor_value_info("output", _DATA_TYPE, _GRID_SHAPE)
    graph_def = onnx.helper.make_graph(nodes, "graph", [x], [y], inits)
    return onnx.helper.make_model(graph_def, ir_version=_IR_VERSION,
                                   opset_imports=_OPSET_IMPORTS)


if __name__ == '__main__':
    task_num = 53
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
