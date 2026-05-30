"""将 baseline ONNX 文件转换为 networks/taskXXX.py 源码

生成的代码可读、可修改，作为我们优化的起点。

Usage:
    python tools/onnx_to_network.py --task 16        # 单个任务
    python tools/onnx_to_network.py --tier1           # 全部 Tier1 任务
    python tools/onnx_to_network.py --all             # 全部 400 个任务
    python tools/onnx_to_network.py --task 16 --optimize  # 转换并尝试优化
"""
import sys
import argparse
import onnx
import numpy as np
from onnx import numpy_helper, helper
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_DIR = REPO_ROOT / "baseline"
NETWORKS_DIR = REPO_ROOT / "networks"
SPEC_DIR = REPO_ROOT / "problem_specs"


def get_rule_text(tid: int) -> str:
    """从 spec 获取规则描述"""
    spec_path = SPEC_DIR / f"task{tid:03d}_spec.md"
    if not spec_path.exists():
        return "规则待分析"
    text = spec_path.read_text(encoding="utf-8")
    sec1 = text.find("## 1. 核心规则")
    sec2 = text.find("## 2. 关键证据")
    if sec1 == -1 or sec2 == -1:
        return "规则待分析"
    rules = []
    for line in text[sec1:sec2].split("\n"):
        line = line.strip()
        if line.startswith("- ") and len(line) > 10:
            rules.append(line[2:])
    return "\n".join(rules) if rules else "规则待分析"


def onnx_to_python(tid: int) -> str:
    """将 baseline ONNX 转为可读的 Python 网络构建代码"""
    onnx_path = BASELINE_DIR / f"task{tid:03d}.onnx"
    if not onnx_path.exists():
        return None

    model = onnx.load(str(onnx_path))
    graph = model.graph
    ops = [n.op_type for n in graph.node]
    rule = get_rule_text(tid)

    # Build header
    lines = []
    lines.append(f'"""Task {tid:03d} — Auto-generated from baseline ONNX')
    lines.append(f"")
    lines.append(f"规则: {rule}")
    lines.append(f"")
    lines.append(f"Baseline 架构: {' + '.join(sorted(set(ops)))} ({len(ops)} nodes)")
    lines.append(f"Baseline 大小: {onnx_path.stat().st_size} bytes")
    lines.append(f"")
    lines.append(f"此为 baseline 的直接翻译，待优化。")
    lines.append(f'"""')
    lines.append(f"import sys, numpy as np")
    lines.append(f"from pathlib import Path")
    lines.append(f"sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))")
    lines.append(f"import neurogolf_utils as nu")
    lines.append(f"import onnx")
    lines.append(f"from onnx import helper")
    lines.append(f"")
    lines.append(f"_CH, _H, _W = 10, 30, 30")
    lines.append(f"_GS = [1, _CH, _H, _W]")
    lines.append(f"_DT = onnx.TensorProto.FLOAT")
    lines.append(f"")

    def safe_name(name: str) -> str:
        """Sanitize ONNX node name to valid Python identifier"""
        return name.replace('/', '_').replace('::', '_').replace('.', '_').replace('-', '_')

    # Build global name map: all ONNX names -> Python-safe names
    name_map = {}

    # Collect all names from graph inputs, outputs, initializers, and node outputs
    all_onnx_names = set()
    for inp in graph.input:
        all_onnx_names.add(inp.name)
    for out in graph.output:
        all_onnx_names.add(out.name)
    for init in graph.initializer:
        all_onnx_names.add(init.name)
    for node in graph.node:
        for out_name in node.output:
            all_onnx_names.add(out_name)

    # Keep 'input' and 'output' as-is (they're special graph I/O names)
    # Use deduplication to avoid name collisions
    py_names_used = set()
    for name in sorted(all_onnx_names):
        if name in ('input', 'output'):
            name_map[name] = name
            py_names_used.add(name)
        else:
            base = safe_name(name)
            unique = base
            i = 1
            while unique in py_names_used:
                unique = f"{base}_{i}"
                i += 1
            name_map[name] = unique
            py_names_used.add(unique)

    def fmt_array(tensor, np_dtype):
        """Format numpy array as Python code, handling long arrays"""
        flat = tensor.flatten()
        parts = []
        for v in flat:
            if isinstance(v, (np.bool_, bool)):
                parts.append('1.0' if v else '0.0')
            elif np.isinf(v) or np.isnan(v):
                parts.append('0.0')
            elif np_dtype == 'np.int64' or np_dtype == 'np.int32':
                parts.append(str(int(v)))
            elif isinstance(v, (int, np.integer)):
                parts.append(str(int(v)))
            else:
                try:
                    if abs(v - round(v)) < 1e-10:
                        parts.append(str(int(round(v))))
                    else:
                        parts.append(f'{v:.6g}')
                except (TypeError, OverflowError):
                    parts.append(f'{float(v):.6g}')
        vals_str = '[' + ', '.join(parts) + ']'
        if len(vals_str) > 200:
            short_lines = []
            line = '['
            for p in parts:
                candidate = line + ('' if line.endswith('[') else ', ') + p
                if len(candidate) > 150:
                    short_lines.append(line.rstrip(', '))
                    line = ' ' + p
                else:
                    line = candidate
            short_lines.append(line.rstrip(', '))
            vals_str = ',\n'.join(short_lines) + ']'
        return vals_str

    # Generate initializer code with unique Python variable names
    init_counter = [0]  # mutable counter
    used_names = set()

    def unique_init_name(hint: str = "init") -> str:
        base = safe_name(hint)
        name = base
        i = 1
        while name in used_names:
            name = f"{base}_{i}"
            i += 1
        used_names.add(name)
        return name

    init_names = []
    for init in graph.initializer:
        tensor = numpy_helper.to_array(init)
        py_name = name_map.get(init.name, safe_name(init.name))
        init_names.append(py_name)
        shape = list(init.dims)
        dt = init.data_type  # Use original data type from ONNX

        # Determine dtype string — preserve original ONNX data type
        dt_map = {
            1: ("np.float32", "onnx.TensorProto.FLOAT"),
            2: ("np.uint8", "onnx.TensorProto.UINT8"),
            3: ("np.int8", "onnx.TensorProto.INT8"),
            4: ("np.uint16", "onnx.TensorProto.UINT16"),
            5: ("np.int16", "onnx.TensorProto.INT16"),
            6: ("np.int32", "onnx.TensorProto.INT32"),
            7: ("np.int64", "onnx.TensorProto.INT64"),
            9: ("np.bool_", "onnx.TensorProto.BOOL"),
            10: ("np.float16", "onnx.TensorProto.FLOAT16"),
            11: ("np.float64", "onnx.TensorProto.DOUBLE"),
            12: ("np.uint32", "onnx.TensorProto.UINT32"),
            13: ("np.uint64", "onnx.TensorProto.UINT64"),
        }
        if dt in dt_map:
            np_dtype, onnx_dtype = dt_map[dt]
        else:
            np_dtype, onnx_dtype = "np.float32", "onnx.TensorProto.FLOAT"

        # Always write the full array, using compact format
        vals_str = fmt_array(tensor, np_dtype)

        lines.append(f"# {py_name}: shape={shape}, dtype={dt} (from {init.name})")
        lines.append(f"{py_name} = np.array({vals_str}, dtype={np_dtype})")
        if list(tensor.shape) != shape and tensor.size > 0:
            lines.append(f"{py_name} = {py_name}.reshape({shape})")
        lines.append(f"{py_name}_init = helper.make_tensor(")
        lines.append(f'    name="{init.name}", data_type={onnx_dtype}, dims={shape},')
        lines.append(f"    vals={py_name}.flatten().tolist())")
        lines.append(f"")

    # Generate node code
    lines.append(f"def build():")
    lines.append(f"    nodes, inits = [], []")
    lines.append(f"")

    for init_name in init_names:
        lines.append(f"    inits.append({init_name}_init)")

    if init_names:
        lines.append(f"")

    for i, node in enumerate(graph.node):
        op = node.op_type
        inputs = list(node.input)
        outputs = list(node.output)
        attrs = {}
        for attr in node.attribute:
            if attr.name == "value" and op == "Constant":
                # Skip Constant nodes — they are embedded in the ONNX graph.
                # This means the generated network is incomplete.
                # Use baseline ONNX directly for verification.
                lines.append(f"    # [{i}] Constant: [] -> {outputs}  # SKIPPED")
                out_str = outputs[0] if outputs else ""
                lines.append(f"    _ = '{out_str}'  # placeholder")
                lines.append(f"")
                continue

            val = helper.get_attribute_value(attr)
            attrs[attr.name] = val

        lines.append(f"    # [{i}] {op}: {inputs} -> {outputs}")
        attr_parts = []
        for k, v in attrs.items():
            if isinstance(v, bytes):
                v = v.decode("utf-8", errors="replace")
                attr_parts.append(f'{k}="{v}"')
            elif isinstance(v, list):
                if len(str(v)) < 200:
                    attr_parts.append(f"{k}={v}")
                # else skip overly long list attributes
            elif isinstance(v, str):
                attr_parts.append(f'{k}="{v}"')
            elif isinstance(v, (int, float)):
                attr_parts.append(f"{k}={v}")

        inputs_str = ", ".join(f'"{inp}"' for inp in inputs)
        outputs_str = ", ".join(f'"{out}"' for out in outputs)
        lines.append(f'    nodes.append(helper.make_node(')
        lines.append(f'        "{op}", [{inputs_str}], [{outputs_str}]')
        if attr_parts:
            for ap in attr_parts:
                lines.append(f"        , {ap}")
        lines.append(f"    ))")
        lines.append(f"")

    # Build graph and model
    # Determine I/O types from the model
    input_dtype = 1  # default FLOAT
    output_dtype = 1
    if graph.input:
        input_dtype = graph.input[0].type.tensor_type.elem_type
    if graph.output:
        output_dtype = graph.output[0].type.tensor_type.elem_type

    dt_to_onnx = {1: '_DT', 10: 'onnx.TensorProto.FLOAT16', 9: 'onnx.TensorProto.BOOL',
                  7: 'onnx.TensorProto.INT64', 6: 'onnx.TensorProto.INT32',
                  11: 'onnx.TensorProto.DOUBLE'}
    input_dt_str = dt_to_onnx.get(input_dtype, '_DT')
    output_dt_str = dt_to_onnx.get(output_dtype, '_DT')

    lines.append(f'    x = helper.make_tensor_value_info("input", {input_dt_str}, _GS)')
    lines.append(f'    y = helper.make_tensor_value_info("output", {output_dt_str}, _GS)')
    opset_ver = model.opset_import[0].version if model.opset_import else 10
    ir_ver = model.ir_version if model.ir_version else 8
    lines.append(f'    graph = helper.make_graph(nodes, "g", [x], [y], inits)')
    lines.append(f'    return helper.make_model(graph, ir_version={ir_ver},')
    lines.append(f'                             opset_imports=[helper.make_opsetid("", {opset_ver})])')
    lines.append(f"")
    lines.append(f"")
    lines.append(f"if __name__ == '__main__':")
    lines.append(f"    task_num = {tid}")
    lines.append(f"    examples = nu.load_examples(task_num)")
    lines.append(f"    network = build()")
    lines.append(f"    nu.verify_network(network, task_num, examples)")

    return "\n".join(lines)


def convert_task(tid: int, dry_run: bool = False) -> bool:
    """转换单个任务"""
    code = onnx_to_python(tid)
    if code is None:
        print(f"  task{tid:03d}: no baseline ONNX")
        return False

    if dry_run:
        print(f"  task{tid:03d}: generated {len(code)} chars")
        return True

    out_path = NETWORKS_DIR / f"task{tid:03d}.py"
    out_path.write_text(code, encoding="utf-8")
    return True


def get_tier1_tasks() -> list[int]:
    """获取 Tier 1 任务列表"""
    simple_archs = {'gather_lookup', 'transpose', 'slice_pad', 'single_conv'}
    tids = []
    for tid in range(1, 401):
        spec_path = SPEC_DIR / f"task{tid:03d}_spec.md"
        if not spec_path.exists():
            continue
        text = spec_path.read_text(encoding="utf-8")
        for line in text.split("\n"):
            if "recommended_architecture:" in line:
                for arch in simple_archs:
                    if arch in line:
                        tids.append(tid)
                        break
                break
    return tids


def main():
    parser = argparse.ArgumentParser(description="baseline ONNX → networks/taskXXX.py")
    parser.add_argument("--task", type=int, help="单个任务编号")
    parser.add_argument("--tier1", action="store_true", help="全部 Tier 1 任务")
    parser.add_argument("--all", action="store_true", help="全部 400 个任务")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=400)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.task:
        tids = [args.task]
    elif args.tier1:
        tids = get_tier1_tasks()
        print(f"Tier 1 tasks: {tids}")
    elif args.all:
        tids = list(range(1, 401))
    else:
        tids = list(range(args.start, args.end + 1))

    converted = 0
    for tid in tids:
        if convert_task(tid, dry_run=args.dry_run):
            converted += 1

    print(f"\nConverted: {converted}/{len(tids)}")
    if args.dry_run:
        print("[DRY RUN] No files written.")
    else:
        print(f"Output: {NETWORKS_DIR}/")


if __name__ == "__main__":
    main()
