"""从 spec 规则 + baseline 权重生成干净的 networks/taskXXX.py

不再机械翻译 ONNX，而是：
1. 读 spec → 理解变换规则和架构模式
2. 读 baseline ONNX → 提取权重/索引值（不复制图结构）
3. 用对应模式模板生成干净的 Python 代码

Usage:
    python tools/gen_networks.py --task 16        # 单个任务
    python tools/gen_networks.py --tier1           # 简单架构任务
    python tools/gen_networks.py --all             # 全部 400 个
"""
import sys, argparse, re, math
import onnx, numpy as np
from onnx import numpy_helper
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parents[1]
SPEC_DIR = REPO / "problem_specs"
BASELINE_DIR = REPO / "baseline"
NETWORKS_DIR = REPO / "networks"

HEADER = '''"""Task {tid:03d} — {rule_short}

架构: {arch} ({pattern})
Baseline 参数: {params}, 节点: {nodes}
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
'''

FOOTER = '''
if __name__ == '__main__':
    task_num = {tid}
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
'''


def get_spec_info(tid: int) -> dict:
    """从 spec 提取规则和架构信息"""
    spec_path = SPEC_DIR / f"task{tid:03d}_spec.md"
    if not spec_path.exists():
        return {"rule_short": "?", "arch": "unknown", "pattern": "unknown"}

    text = spec_path.read_text(encoding="utf-8")
    info = {"rule_short": "?"}

    # Extract rule
    for line in text.split("\n"):
        if line.strip().startswith("- 核心变换") or line.strip().startswith("- 核心规则"):
            info["rule_short"] = line.strip()[2:][:100]
            break

    # Extract architecture using regex
    m = re.search(r"recommended_architecture:\s*`?(\S+)`?", text)
    if m:
        info["arch"] = m.group(1)
    m = re.search(r"baseline_pattern:\s*(.+)", text)
    if m:
        info["pattern"] = m.group(1).strip()
    m = re.search(r"baseline_nodes:\s*(\d+)", text)
    if m:
        info["nodes"] = int(m.group(1))
    m = re.search(r"baseline_ops:\s*(.+)", text)
    if m:
        info["ops"] = m.group(1).strip()

    info.setdefault("arch", "unknown")
    info.setdefault("pattern", "unknown")
    info.setdefault("nodes", "?")
    info.setdefault("ops", "?")
    return info


def get_baseline_weights(tid: int) -> dict:
    """从 baseline ONNX 提取所有权重/索引值"""
    onnx_path = BASELINE_DIR / f"task{tid:03d}.onnx"
    if not onnx_path.exists():
        return {}

    model = onnx.load(str(onnx_path))
    weights = {}
    for init in model.graph.initializer:
        t = numpy_helper.to_array(init)
        weights[init.name] = {"data": t, "shape": list(init.dims), "dtype": init.data_type}
    weights["_opset"] = model.opset_import[0].version if model.opset_import else 10
    weights["_ir"] = model.ir_version if model.ir_version else 8
    weights["_ops"] = [n.op_type for n in model.graph.node]
    weights["_nodes"] = model.graph.node

    # Also check graph I/O types
    if model.graph.output:
        weights["_out_dtype"] = model.graph.output[0].type.tensor_type.elem_type
    return weights


def fmt_array(arr: np.ndarray) -> str:
    """Format numpy array as compact Python code"""
    flat = arr.flatten()
    if len(flat) == 0:
        return "np.array([], dtype=np.float32)"

    # Determine dtype
    if arr.dtype == np.int64 or arr.dtype == np.int32:
        dtype_str = "np.int64" if arr.dtype == np.int64 else "np.int32"
        parts = [str(int(v)) for v in flat]
    elif arr.dtype == np.float16:
        dtype_str = "np.float16"
        parts = [f"{float(v):.6g}" for v in flat]
    else:
        dtype_str = "np.float32"
        parts = []
        for v in flat:
            if abs(v - round(v)) < 1e-10:
                parts.append(str(int(round(v))) + ".0")
            else:
                parts.append(f"{v:.6g}")

    # Always use a clean join, no fancy line-breaking
    val_str = "[" + ", ".join(parts) + "]"
    return f"np.array({val_str}, dtype={dtype_str})"


def make_init(name: str, arr: np.ndarray, onnx_dtype: str = "_DT") -> str:
    """Generate initializer creation code"""
    if onnx_dtype == "_DT":
        onnx_dtype = "onnx.TensorProto.FLOAT"
    shape = list(arr.shape)
    var_name = name.replace(".", "_").replace("/", "_").replace("::", "_")
    code = f"{var_name}_data = {fmt_array(arr)}\n"
    code += f"{var_name} = helper.make_tensor(\n"
    code += f'    name="{name}", data_type={onnx_dtype}, dims={shape},\n'
    code += f"    vals={var_name}_data.flatten().tolist())"
    return code, var_name


# ─── Pattern Templates ───────────────────────────────

def gen_gather_lookup(tid: int, spec: dict, w: dict) -> str:
    """Gather(axis=1) for color permutation"""
    # Find the channel index array
    idx_arr = None
    for name, val in w.items():
        if name.startswith("_"): continue
        arr = val["data"]
        if arr.size == 10 and val["dtype"] == 7:  # INT64, size 10
            idx_arr = arr
            break
    if idx_arr is None:
        # Fallback: try to deduce from spec rule
        idx_arr = np.arange(10, dtype=np.int64)

    idx_code, idx_var = make_init("color_idx", idx_arr, "onnx.TensorProto.INT64")

    code = HEADER.format(tid=tid, rule_short=spec.get("rule_short", ""),
                         arch=spec["arch"], pattern=spec["pattern"],
                         params=idx_arr.size, nodes=1)
    code += f"""
{idx_code}


def build():
    nodes, inits = [], []
    inits.append({idx_var})
    nodes.append(helper.make_node("Gather", ["input", "{idx_var}"], ["output"], axis=1))
    x = helper.make_tensor_value_info("input", _DT, _GS)
    y = helper.make_tensor_value_info("output", _DT, _GS)
    g = helper.make_graph(nodes, "g", [x], [y], inits)
    return helper.make_model(g, ir_version={w.get('_ir', 8)},
                             opset_imports=[helper.make_opsetid("", {w.get('_opset', 13)})])
"""
    code += FOOTER.format(tid=tid)
    return code


def gen_transpose(tid: int, spec: dict, w: dict) -> str:
    """Transpose for H<->W swap"""
    code = HEADER.format(tid=tid, rule_short=spec.get("rule_short", ""),
                         arch=spec["arch"], pattern=spec["pattern"],
                         params=0, nodes=1)
    code += f"""

def build():
    nodes, inits = [], []
    nodes.append(helper.make_node("Transpose", ["input"], ["output"], perm=[0, 1, 3, 2]))
    x = helper.make_tensor_value_info("input", _DT, _GS)
    y = helper.make_tensor_value_info("output", _DT, _GS)
    g = helper.make_graph(nodes, "g", [x], [y], inits)
    return helper.make_model(g, ir_version={w.get('_ir', 8)},
                             opset_imports=[helper.make_opsetid("", {w.get('_opset', 13)})])
"""
    code += FOOTER.format(tid=tid)
    return code


def gen_gather_spatial(tid: int, spec: dict, w: dict) -> str:
    """Gather(axis=2 or 3) for row/col permutation"""
    # Find the spatial index array (size 30)
    idx_arr = None
    axis = 2
    for name, val in w.items():
        if name.startswith("_"): continue
        arr = val["data"]
        if arr.size == 30 and val["dtype"] == 7:  # INT64, size 30
            idx_arr = arr
            break

    if idx_arr is None:
        # Try size 6 or other spatial indices
        for name, val in w.items():
            if name.startswith("_"): continue
            arr = val["data"]
            if val["dtype"] == 7 and 5 < arr.size <= 30:
                idx_arr = arr
                break

    if idx_arr is None:
        idx_arr = np.arange(30, dtype=np.int64)

    idx_code, idx_var = make_init("spatial_idx", idx_arr, "onnx.TensorProto.INT64")

    # Determine axis from spec or baseline
    ops = w.get("_ops", [])
    if ops == ["Gather"] and w.get("_nodes"):
        for attr in w["_nodes"][0].attribute:
            if attr.name == "axis":
                axis = attr.i

    code = HEADER.format(tid=tid, rule_short=spec.get("rule_short", ""),
                         arch=spec["arch"], pattern=spec["pattern"],
                         params=idx_arr.size, nodes=1)
    code += f"""
{idx_code}


def build():
    nodes, inits = [], []
    inits.append({idx_var})
    nodes.append(helper.make_node("Gather", ["input", "{idx_var}"], ["output"], axis={axis}))
    x = helper.make_tensor_value_info("input", _DT, _GS)
    y = helper.make_tensor_value_info("output", _DT, _GS)
    g = helper.make_graph(nodes, "g", [x], [y], inits)
    return helper.make_model(g, ir_version={w.get('_ir', 8)},
                             opset_imports=[helper.make_opsetid("", {w.get('_opset', 13)})])
"""
    code += FOOTER.format(tid=tid)
    return code


def gen_slice_pad(tid: int, spec: dict, w: dict) -> str:
    """Slice+Pad for crop/flip/reposition"""
    # This is more complex - extract Slice and Pad parameters from baseline nodes
    nodes = w.get("_nodes", [])
    slice_starts = [0, 0]
    slice_ends = [3, 3]
    slice_axes = [2, 3]
    slice_steps = [1, 1]
    pad_values = [0, 0, 0, 0, 0, 0, 27, 27]

    for node in nodes:
        if node.op_type == "Slice":
            for attr in node.attribute:
                if attr.name == "starts":
                    slice_starts = list(attr.ints)
                elif attr.name == "ends":
                    slice_ends = list(attr.ints)
                elif attr.name == "axes":
                    slice_axes = list(attr.ints)
                elif attr.name == "steps":
                    slice_steps = list(attr.ints)
        elif node.op_type == "Pad":
            for attr in node.attribute:
                if attr.name == "pads":
                    pad_values = list(attr.ints)

    code = HEADER.format(tid=tid, rule_short=spec.get("rule_short", ""),
                         arch=spec["arch"], pattern=spec["pattern"],
                         params=len(slice_starts) + len(slice_ends) + len(pad_values),
                         nodes=2)
    code += f"""

def build():
    nodes, inits = [], []
    # Slice: extract sub-region
    starts = np.array({slice_starts}, dtype=np.int64)
    ends = np.array({slice_ends}, dtype=np.int64)
    axes = np.array({slice_axes}, dtype=np.int64)
    steps = np.array({slice_steps}, dtype=np.int64)
    s_init = helper.make_tensor("starts", onnx.TensorProto.INT64, [{len(slice_starts)}], starts)
    e_init = helper.make_tensor("ends", onnx.TensorProto.INT64, [{len(slice_ends)}], ends)
    a_init = helper.make_tensor("axes", onnx.TensorProto.INT64, [{len(slice_axes)}], axes)
    st_init = helper.make_tensor("steps", onnx.TensorProto.INT64, [{len(slice_steps)}], steps)
    for t in [s_init, e_init, a_init, st_init]:
        inits.append(t)
    nodes.append(helper.make_node("Slice", ["input", "starts", "ends", "axes", "steps"], ["cropped"]))

    # Pad: restore to 30x30
    pads = np.array({pad_values}, dtype=np.int64)
    p_init = helper.make_tensor("pads", onnx.TensorProto.INT64, [{len(pad_values)}], pads)
    inits.append(p_init)
    nodes.append(helper.make_node("Pad", ["cropped", "pads"], ["output"], mode="constant", value=0.0))

    x = helper.make_tensor_value_info("input", _DT, _GS)
    y = helper.make_tensor_value_info("output", _DT, _GS)
    g = helper.make_graph(nodes, "g", [x], [y], inits)
    return helper.make_model(g, ir_version={w.get('_ir', 8)},
                             opset_imports=[helper.make_opsetid("", {w.get('_opset', 13)})])
"""
    code += FOOTER.format(tid=tid)
    return code


def gen_single_conv(tid: int, spec: dict, w: dict) -> str:
    """Single Conv layer with extracted weights"""
    # Find the Conv weight tensor
    weight_arr = None
    bias_arr = None
    for name, val in w.items():
        if name.startswith("_"): continue
        arr = val["data"]
        if len(arr.shape) == 4 and arr.shape[0] >= 1:  # Conv weight
            weight_arr = arr
        elif len(arr.shape) == 1 and arr.size <= 10:  # possibly bias
            if bias_arr is None:
                bias_arr = arr

    if weight_arr is None:
        weight_arr = np.zeros((10, 10, 3, 3), dtype=np.float32)
        for i in range(10):
            weight_arr[i, i, 1, 1] = 1.0

    w_code, w_var = make_init("conv_w", weight_arr)
    kernel = list(weight_arr.shape[2:])

    bias_code = ""
    if bias_arr is not None:
        b_code, b_var = make_init("conv_b", bias_arr)
        bias_code = f"\n{b_code}"

    params = int(np.prod(weight_arr.shape)) + (int(bias_arr.size) if bias_arr is not None else 0)

    # Determine if Conv has any special attributes from baseline
    group = 1
    for node in w.get("_nodes", []):
        if node.op_type == "Conv":
            for attr in node.attribute:
                if attr.name == "group":
                    group = attr.i

    code = HEADER.format(tid=tid, rule_short=spec.get("rule_short", ""),
                         arch=spec["arch"], pattern=spec["pattern"],
                         params=params, nodes=1)
    code += f"""
{w_code}{bias_code}


def build():
    nodes, inits = [], []
    inits.append({w_var})"""
    if bias_arr is not None:
        code += f"\n    inits.append({b_var})"
        inputs = '["input", "conv_w", "conv_b"]'
    else:
        inputs = '["input", "conv_w"]'

    code += f"""
    nodes.append(helper.make_node("Conv", {inputs}, ["output"],
        kernel_shape={kernel}, pads=[{kernel[0]//2}, {kernel[1]//2}, {kernel[0]//2}, {kernel[1]//2}]"""
    if group != 1:
        code += f", group={group}"
    code += """))
    x = helper.make_tensor_value_info("input", _DT, _GS)
    y = helper.make_tensor_value_info("output", _DT, _GS)
    g = helper.make_graph(nodes, "g", [x], [y], inits)
    return helper.make_model(g,"""
    code += f" ir_version={w.get('_ir', 8)},\n"
    code += f"                             opset_imports=[helper.make_opsetid(\"\", {w.get('_opset', 13)})])"
    code += "\n"
    code += FOOTER.format(tid=tid)
    return code


def gen_fallback(tid: int, spec: dict, w: dict) -> str:
    """Fallback: copy baseline ONNX directly, note that manual conversion is needed"""
    code = HEADER.format(tid=tid, rule_short=spec.get("rule_short", ""),
                         arch=spec["arch"], pattern=spec["pattern"],
                         params="?", nodes=spec.get("nodes", "?"))
    code += f"""
# 此任务架构较复杂 ({spec['arch']})，直接使用 baseline ONNX。
# 如需优化，参考 BASELINE_TECHNIQUES.md 和 NETWORK_BUILDING_GUIDE.md。

import shutil, onnx

def build():
    model = onnx.load(str(Path(__file__).resolve().parents[1] / "baseline" / "task{tid:03d}.onnx"))
    return model
"""
    code += FOOTER.format(tid=tid)
    return code


# ─── Dispatcher ──────────────────────────────────────

PATTERN_GENS = {
    "gather_lookup": gen_gather_lookup,
    "transpose": gen_transpose,
    "gather_spatial": gen_gather_spatial,
    "slice_pad": gen_slice_pad,
    "single_conv": gen_single_conv,
    "gather_based_multi_op": gen_gather_spatial,  # try spatial pattern
    "slice_based_multi_op": gen_slice_pad,         # try slice pattern
}

FALLBACK_ARCHS = {"conv_with_logic", "reduce_with_where", "reduce_only", "custom_multi_op"}


def gen_network(tid: int) -> str | None:
    """为单个任务生成干净的 network 代码"""
    spec = get_spec_info(tid)
    w = get_baseline_weights(tid)

    if not w:
        return None

    arch = spec["arch"]

    if arch in PATTERN_GENS:
        gen_fn = PATTERN_GENS[arch]
        try:
            return gen_fn(tid, spec, w)
        except Exception as e:
            print(f"  task{tid:03d}: pattern gen failed ({e}), using fallback")
            return gen_fallback(tid, spec, w)
    else:
        return gen_fallback(tid, spec, w)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=int)
    parser.add_argument("--tier1", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=200)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.task:
        tids = [args.task]
    elif args.tier1:
        tids = []
        for tid in range(1, 401):
            spec = get_spec_info(tid)
            if spec["arch"] in PATTERN_GENS:
                tids.append(tid)
    elif args.all:
        tids = list(range(1, 401))
    else:
        tids = list(range(args.start, args.end + 1))

    generated = 0
    for tid in tids:
        code = gen_network(tid)
        if code is None:
            continue

        if args.dry_run:
            print(f"  task{tid:03d}: {get_spec_info(tid)['arch']} ({len(code)} chars)")
        else:
            out = NETWORKS_DIR / f"task{tid:03d}.py"
            out.write_text(code, encoding="utf-8")
        generated += 1

    print(f"\nGenerated: {generated}/{len(tids)}")
    if args.dry_run:
        print("[DRY RUN]")


if __name__ == "__main__":
    main()
