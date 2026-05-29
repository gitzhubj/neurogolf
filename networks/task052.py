"""Task 052 — Row uniformity detection: if all 3 cells in a row share the
same color, output 5 for that entire row, else 0.

Architecture: ReduceSum over width -> ReduceMax over channels -> Relu
threshold at 2.5 -> broadcast per-row result to all 3 columns.

Grid is 3x3 at top-left of 30x30 canvas.
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

    # 1) ReduceSum over width (axis=3): per-channel sum across 3 columns
    row_sum = onnx.helper.make_node(
        "ReduceSum", ["input"], ["row_sum"],
        axes=[3], keepdims=1
    )
    nodes.append(row_sum)

    # 2) ReduceMax over channels (axis=1): find max colour count per row
    max_count = onnx.helper.make_node(
        "ReduceMax", ["row_sum"], ["max_count"],
        axes=[1], keepdims=1
    )
    nodes.append(max_count)

    # 3) Subtract threshold 2.5  (uniform → 3.0-2.5=0.5, non-uniform → ≤2.0-2.5≤-0.5)
    thresh_init = onnx.helper.make_tensor("thresh", _DATA_TYPE, [1], [2.5])
    inits.append(thresh_init)
    diff = onnx.helper.make_node("Sub", ["max_count", "thresh"], ["diff"])
    nodes.append(diff)

    # 4) Relu → 0.5 for uniform, 0 for non-uniform
    relu = onnx.helper.make_node("Relu", ["diff"], ["pos"])
    nodes.append(relu)

    # 5) Multiply by 2 → 1.0 for uniform, 0 for non-uniform
    two_init = onnx.helper.make_tensor("two", _DATA_TYPE, [1], [2.0])
    inits.append(two_init)
    mul2 = onnx.helper.make_node("Mul", ["pos", "two"], ["is_uniform"])
    nodes.append(mul2)

    # 6) Grid mask (1,1,30,30): 1.0 for rows 0-2, cols 0-2
    grid_mask_np = np.zeros((1, 1, _HEIGHT, _WIDTH), dtype=np.float32)
    grid_mask_np[0, 0, 0:3, 0:3] = 1.0
    grid_mask_init = onnx.helper.make_tensor(
        "grid_mask", _DATA_TYPE, [1, 1, _HEIGHT, _WIDTH],
        grid_mask_np.flatten().tolist()
    )
    grid_mask = onnx.helper.make_node("Constant", [], ["grid_mask_const"],
                                       value=grid_mask_init)
    nodes.append(grid_mask)

    # 7) Width ones (1,1,1,30) for broadcasting is_uniform to full width
    width_ones_np = np.ones((1, 1, 1, _WIDTH), dtype=np.float32)
    width_ones_init = onnx.helper.make_tensor(
        "width_ones", _DATA_TYPE, [1, 1, 1, _WIDTH],
        width_ones_np.flatten().tolist()
    )
    width_ones = onnx.helper.make_node("Constant", [], ["width_ones_const"],
                                        value=width_ones_init)
    nodes.append(width_ones)

    # 8) Broadcast is_uniform to all columns: (1,1,30,1) × (1,1,1,30) → (1,1,30,30)
    uniform_row = onnx.helper.make_node("Mul", ["is_uniform", "width_ones_const"],
                                         ["uniform_row"])
    nodes.append(uniform_row)

    # 9) Mask to grid area only
    uniform_grid = onnx.helper.make_node("Mul", ["uniform_row", "grid_mask_const"],
                                          ["uniform_grid"])
    nodes.append(uniform_grid)

    # 10) Non-uniform positions within grid
    non_uniform_grid = onnx.helper.make_node("Sub", ["grid_mask_const", "uniform_grid"],
                                              ["non_uniform_grid"])
    nodes.append(non_uniform_grid)

    # 11) Channel selectors
    ch5_sel_np = np.zeros((1, _CHANNELS, 1, 1), dtype=np.float32)
    ch5_sel_np[0, 5, 0, 0] = 1.0
    ch5_init = onnx.helper.make_tensor("ch5_w", _DATA_TYPE, [1, _CHANNELS, 1, 1],
                                        ch5_sel_np.flatten().tolist())
    ch5_sel = onnx.helper.make_node("Constant", [], ["ch5_sel_const"], value=ch5_init)
    nodes.append(ch5_sel)

    ch0_sel_np = np.zeros((1, _CHANNELS, 1, 1), dtype=np.float32)
    ch0_sel_np[0, 0, 0, 0] = 1.0
    ch0_init = onnx.helper.make_tensor("ch0_w", _DATA_TYPE, [1, _CHANNELS, 1, 1],
                                        ch0_sel_np.flatten().tolist())
    ch0_sel = onnx.helper.make_node("Constant", [], ["ch0_sel_const"], value=ch0_init)
    nodes.append(ch0_sel)

    # 12) Channel 5 output: uniform positions → 5.0
    # uniform_grid is (1,1,30,30), ch5_sel is (1,10,1,1) → broadcast to (1,10,30,30)
    ch5_tmp = onnx.helper.make_node("Mul", ["uniform_grid", "ch5_sel_const"], ["ch5_tmp"])
    nodes.append(ch5_tmp)
    five_init = onnx.helper.make_tensor("five", _DATA_TYPE, [1], [5.0])
    inits.append(five_init)
    ch5_out = onnx.helper.make_node("Mul", ["ch5_tmp", "five"], ["ch5_out"])
    nodes.append(ch5_out)

    # 13) Channel 0 output: non-uniform positions → 1.0
    ch0_out = onnx.helper.make_node("Mul", ["non_uniform_grid", "ch0_sel_const"], ["ch0_out"])
    nodes.append(ch0_out)

    # 14) Combine
    output = onnx.helper.make_node("Add", ["ch5_out", "ch0_out"], ["output"])
    nodes.append(output)

    # Build model
    x = onnx.helper.make_tensor_value_info("input", _DATA_TYPE, _GRID_SHAPE)
    y = onnx.helper.make_tensor_value_info("output", _DATA_TYPE, _GRID_SHAPE)
    graph_def = onnx.helper.make_graph(nodes, "graph", [x], [y], inits)
    return onnx.helper.make_model(graph_def, ir_version=_IR_VERSION,
                                   opset_imports=_OPSET_IMPORTS)


if __name__ == '__main__':
    task_num = 52
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
