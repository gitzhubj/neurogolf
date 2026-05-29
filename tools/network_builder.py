"""Multi-layer ONNX network builder for NeuroGolf.

Supports: Conv, ReLU, Add, Concat, Constant nodes.
All networks comply with IR v10, opset 10, static shapes (1,10,30,30).
"""
import itertools
import onnx
import numpy as np

_DATA_TYPE = onnx.TensorProto.FLOAT
_CHANNELS, _HEIGHT, _WIDTH = 10, 30, 30
_GRID_SHAPE = [1, _CHANNELS, _HEIGHT, _WIDTH]
_IR_VERSION = 10
_OPSET_IMPORTS = [onnx.helper.make_opsetid("", 10)]

_node_counter = 0


def _make_name(prefix):
    global _node_counter
    _node_counter += 1
    return f"{prefix}_{_node_counter}"


def reset_counter():
    global _node_counter
    _node_counter = 0


def make_conv(input_name, out_channels, kernel_size, weight_fn, padding=None, output_name=None):
    """Create a Conv node + weight initializer. Returns (node, weight, output_name)."""
    k = kernel_size
    offsets = range(-k // 2 + 1, k // 2 + 1)
    w_shape = [out_channels, _CHANNELS, k, k]
    cells = itertools.product(range(out_channels), range(_CHANNELS), offsets, offsets)
    weights = [float(weight_fn(o, i, (r, c))) for (o, i, r, c) in cells]

    w_name = _make_name("W")
    if output_name is None:
        output_name = _make_name("conv_out")

    w_init = onnx.helper.make_tensor(w_name, _DATA_TYPE, w_shape, weights)
    pads = padding if padding is not None else [k // 2] * 4
    node = onnx.helper.make_node(
        "Conv", [input_name, w_name], [output_name],
        kernel_shape=[k, k], pads=pads
    )
    return node, w_init, output_name


def make_relu(input_name, output_name=None):
    """Create a ReLU node. Returns (node, output_name)."""
    if output_name is None:
        output_name = _make_name("relu_out")
    node = onnx.helper.make_node("Relu", [input_name], [output_name])
    return node, output_name


def make_add(a_name, b_name):
    """Element-wise addition. Returns (node, output_name)."""
    output_name = _make_name("add_out")
    node = onnx.helper.make_node("Add", [a_name, b_name], [output_name])
    return node, output_name


def make_mul(a_name, b_name):
    """Element-wise multiplication. Returns (node, output_name)."""
    output_name = _make_name("mul_out")
    node = onnx.helper.make_node("Mul", [a_name, b_name], [output_name])
    return node, output_name


def make_constant(name, shape, values):
    """Create a Constant node. Returns (node, output_name)."""
    output_name = name
    np_values = np.array(values, dtype=np.float32).reshape(shape)
    node = onnx.helper.make_node(
        "Constant", [], [output_name],
        value=onnx.helper.make_tensor(name, _DATA_TYPE, shape, np_values.flatten().tolist())
    )
    return node, output_name


def make_concat(input_names, axis=1):
    """Concatenate along given axis. Returns (node, output_name)."""
    output_name = _make_name("concat_out")
    node = onnx.helper.make_node("Concat", input_names, [output_name], axis=axis)
    return node, output_name


def make_reshape(input_name, target_shape):
    """Reshape tensor. Returns (node, output_name)."""
    output_name = _make_name("reshape_out")
    shape_name = _make_name("shape_const")
    shape_init = onnx.helper.make_tensor(
        shape_name, onnx.TensorProto.INT64,
        [len(target_shape)], list(target_shape)
    )
    node = onnx.helper.make_node("Reshape", [input_name, shape_name], [output_name])
    return node, shape_init, output_name


def build_network(input_name, output_name, nodes, initializers):
    """Build and return an ONNX model from nodes and initializers."""
    x = onnx.helper.make_tensor_value_info(input_name, _DATA_TYPE, _GRID_SHAPE)
    y = onnx.helper.make_tensor_value_info(output_name, _DATA_TYPE, _GRID_SHAPE)
    graph_def = onnx.helper.make_graph(nodes, "graph", [x], [y], initializers)
    model_def = onnx.helper.make_model(
        graph_def, ir_version=_IR_VERSION, opset_imports=_OPSET_IMPORTS
    )
    return model_def


def single_conv_network(weight_fn, kernel_size=1):
    """Build a single-layer Conv network (replicates neurogolf_utils behavior)."""
    reset_counter()
    conv, w_init, _ = make_conv("input", _CHANNELS, kernel_size, weight_fn, output_name="output")
    return build_network("input", "output", [conv], [w_init])


def two_layer_network(weight_fn1, weight_fn2, kernel_size1=3, kernel_size2=1):
    """Conv → ReLU → Conv."""
    reset_counter()
    nodes, inits = [], []

    conv1, w1, c1_out = make_conv("input", _CHANNELS, kernel_size1, weight_fn1)
    nodes.append(conv1); inits.append(w1)

    relu, r_out = make_relu(c1_out)
    nodes.append(relu)

    conv2, w2, _ = make_conv(r_out, _CHANNELS, kernel_size2, weight_fn2, output_name="output")
    nodes.append(conv2); inits.append(w2)

    return build_network("input", "output", nodes, inits)


def three_layer_network(weight_fn1, weight_fn2, weight_fn3,
                         kernel_size1=3, kernel_size2=3, kernel_size3=1):
    """Conv → ReLU → Conv → ReLU → Conv."""
    reset_counter()
    nodes, inits = [], []

    conv1, w1, c1_out = make_conv("input", _CHANNELS, kernel_size1, weight_fn1)
    nodes.append(conv1); inits.append(w1)

    relu1, r1_out = make_relu(c1_out)
    nodes.append(relu1)

    conv2, w2, c2_out = make_conv(r1_out, _CHANNELS, kernel_size2, weight_fn2)
    nodes.append(conv2); inits.append(w2)

    relu2, r2_out = make_relu(c2_out)
    nodes.append(relu2)

    conv3, w3, _ = make_conv(r2_out, _CHANNELS, kernel_size3, weight_fn3, output_name="output")
    nodes.append(conv3); inits.append(w3)

    return build_network("input", "output", nodes, inits)


def make_pad(input_name, pads, constant_value=0.0, output_name=None):
    """Create a Pad node (opset 10, constant mode).
    pads: [begin_d0, end_d0, begin_d1, end_d1, ...] per dimension.
    """
    if output_name is None:
        output_name = _make_name("pad_out")
    node = onnx.helper.make_node(
        "Pad", [input_name], [output_name],
        mode="constant", value=float(constant_value), pads=pads
    )
    return node, output_name


def shift_network(kernel_size=3, shift_row=-1, shift_col=0):
    """Build a network that shifts the input spatially.

    Uses Conv + Constant top-row-fix for proper background handling.
    shift_row: -1 = down, 1 = up; shift_col: -1 = right, 1 = left.
    """
    reset_counter()
    nodes, inits = [], []

    # Conv: shift all channels
    def wf(ch_out, ch_in, kc):
        if kc == (shift_row, shift_col) and ch_out == ch_in:
            return 1.0
        return 0.0

    conv, w, conv_out = make_conv("input", _CHANNELS, kernel_size, wf)
    nodes.append(conv); inits.append(w)

    # Constant: fix top row background (only for shift down)
    bg_data = np.zeros((1, _CHANNELS, _HEIGHT, _WIDTH), dtype=np.float32)
    if shift_row == -1:
        # Top row of ch0 = 1.0
        bg_data[0, 0, 0, :] = 1.0
    # TODO: handle other shift directions

    const_name = _make_name("bg_fix")
    const_node = onnx.helper.make_node(
        "Constant", [], [const_name],
        value=onnx.helper.make_tensor(const_name, _DATA_TYPE,
                                       [1, _CHANNELS, _HEIGHT, _WIDTH],
                                       bg_data.flatten().tolist())
    )
    nodes.append(const_node)

    # Add: combine shifted output with bg fix
    add_node = onnx.helper.make_node("Add", [conv_out, const_name], ["output"])
    nodes.append(add_node)

    return build_network("input", "output", nodes, inits)
