"""为 tasks 101-400 生成 problem_spec 文件

数据来源:
- input/taskXXX.json → 基本特征（尺寸、颜色、样本数）
- baseline/taskXXX.onnx → 权威架构提示（已验证可用）
- AGENTSforSpec.md → 格式模板

Usage:
    python tools/generate_specs.py --all           # 生成全部 101-400
    python tools/generate_specs.py --start 101 --end 200
    python tools/generate_specs.py --tasks 150,151,152
    python tools/generate_specs.py --dry-run       # 预览
"""
import sys
import json
import argparse
import onnx
import numpy as np
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = REPO_ROOT / "problem_specs"
INPUT_DIR = REPO_ROOT / "input"
BASELINE_DIR = REPO_ROOT / "baseline"


def analyze_baseline(tid: int) -> dict | None:
    """从 baseline ONNX 提取架构信息"""
    path = BASELINE_DIR / f"task{tid:03d}.onnx"
    if not path.exists():
        return None

    model = onnx.load(str(path))
    ops = [n.op_type for n in model.graph.node]
    op_set = set(ops)
    node_count = len(ops)
    init_count = sum(1 for _ in model.graph.initializer)
    size = path.stat().st_size

    info = {
        "node_count": node_count,
        "init_count": init_count,
        "size_bytes": size,
        "actual_ops": "+".join(sorted(op_set)),
        "full_ops": sorted(op_set),
    }

    # Classify architecture
    if ops == ["Gather"]:
        axis = 1
        for attr in model.graph.node[0].attribute:
            if attr.name == "axis":
                axis = attr.i
        if axis == 1:
            info.update(_gather_lookup())
        else:
            info.update(_gather_spatial())
    elif ops == ["Transpose"]:
        info.update(_transpose())
    elif op_set == {"Slice", "Pad"}:
        info.update(_slice_pad())
    elif ops == ["Conv"]:
        info.update(_single_conv())
    elif "Gather" in op_set and "Conv" not in op_set and "ReduceSum" not in op_set and "ReduceMax" not in op_set:
        info.update(_gather_based(node_count))
    elif "Conv" in op_set:
        nonlinear = "yes" if "Relu" in op_set else "no"
        info.update(_conv_logic(node_count, nonlinear, info["actual_ops"]))
    elif "ReduceSum" in op_set or "ReduceMax" in op_set:
        has_where = "Where" in op_set
        info.update(_reduce_based(has_where, node_count, info["actual_ops"]))
    elif "Slice" in op_set and node_count <= 10:
        info.update(_slice_based(node_count))
    else:
        info.update(_custom(info["actual_ops"], node_count))

    return info


def _gather_lookup():
    return {
        "recommended_architecture": "gather_lookup",
        "locality": "0",
        "single_linear_conv_possible": "yes (via Gather, better than Conv)",
        "recommended_kernel": "not_needed",
        "nonlinearity_needed": "no",
        "memory_priority": "Gather(axis=1, indices=color_table). Single node, ~10 params.",
        "fusion_hint": "Channel index permutation via Gather is the optimal approach.",
        "main_risk": "low",
        "confidence": "high",
        "pattern": "Gather channel lookup",
    }


def _gather_spatial():
    return {
        "recommended_architecture": "gather_spatial",
        "locality": "1",
        "single_linear_conv_possible": "yes (via Gather spatial, better than Conv)",
        "recommended_kernel": "not_needed",
        "nonlinearity_needed": "no",
        "memory_priority": "Gather(axis=2/3, indices). Single node, ~30 params.",
        "fusion_hint": "Spatial permutation via Gather on axis 2 or 3.",
        "main_risk": "low",
        "confidence": "high",
        "pattern": "Gather spatial permutation",
    }


def _transpose():
    return {
        "recommended_architecture": "transpose",
        "locality": "global",
        "single_linear_conv_possible": "yes (via Transpose, 0 params!)",
        "recommended_kernel": "not_needed",
        "nonlinearity_needed": "no",
        "memory_priority": "Transpose(perm=[0,1,3,2]) — 0 params, free H<->W swap.",
        "fusion_hint": "Single Transpose node. Cheapest possible spatial transform.",
        "main_risk": "low",
        "confidence": "high",
        "pattern": "Transpose H<->W swap",
    }


def _slice_pad():
    return {
        "recommended_architecture": "slice_pad",
        "locality": "0",
        "single_linear_conv_possible": "yes (via Slice+Pad)",
        "recommended_kernel": "not_needed",
        "nonlinearity_needed": "no",
        "memory_priority": "Slice to extract/crop/flip, Pad to restore 30x30.",
        "fusion_hint": "Step=-1 in Slice gives free flip. Pad mode=constant for background fill.",
        "main_risk": "low",
        "confidence": "high",
        "pattern": "Slice + Pad crop/flip/reposition",
    }


def _single_conv():
    return {
        "recommended_architecture": "single_conv",
        "locality": "k",
        "single_linear_conv_possible": "yes",
        "recommended_kernel": "3x3",
        "nonlinearity_needed": "no",
        "memory_priority": "Single Conv, no bias, no activation.",
        "fusion_hint": "All spatial logic encoded in one Conv weight tensor.",
        "main_risk": "low",
        "confidence": "high",
        "pattern": "Single Conv",
    }


def _gather_based(nodes):
    return {
        "recommended_architecture": "gather_based_multi_op",
        "locality": "varies",
        "single_linear_conv_possible": "probably",
        "recommended_kernel": "not_needed",
        "nonlinearity_needed": "no",
        "memory_priority": "Gather-based multi-op. No Conv needed.",
        "fusion_hint": f"Gather + supporting ops. {nodes} nodes total.",
        "main_risk": "medium",
        "confidence": "high",
        "pattern": "Gather-based multi-op",
    }


def _conv_logic(nodes, nonlinear, ops_str):
    return {
        "recommended_architecture": "conv_with_logic",
        "locality": "k",
        "single_linear_conv_possible": "no",
        "recommended_kernel": "3x3",
        "nonlinearity_needed": nonlinear,
        "memory_priority": "Conv + support ops (Reduce/Where/Mul/Sub). Minimize intermediate tensors.",
        "fusion_hint": f"Study baseline: {nodes} nodes, ops={ops_str[:80]}",
        "main_risk": "medium",
        "confidence": "high",
        "pattern": "Conv + logic gates",
    }


def _reduce_based(has_where, nodes, ops_str):
    arch = "reduce_with_where" if has_where else "reduce_only"
    return {
        "recommended_architecture": arch,
        "locality": "global",
        "single_linear_conv_possible": "no",
        "recommended_kernel": "not_needed",
        "nonlinearity_needed": "no",
        "memory_priority": "Reduce + threshold + conditional logic. No Conv required.",
        "fusion_hint": f"ReduceSum/ReduceMax + Greater/Equal + {'Where' if has_where else 'arithmetic'}. {nodes} nodes.",
        "main_risk": "medium",
        "confidence": "high",
        "pattern": "Reduce + " + ("Where conditional" if has_where else "arithmetic"),
    }


def _slice_based(nodes):
    return {
        "recommended_architecture": "slice_based_multi_op",
        "locality": "varies",
        "single_linear_conv_possible": "probably",
        "recommended_kernel": "not_needed",
        "nonlinearity_needed": "no",
        "memory_priority": "Slice-based multi-op. No Conv needed.",
        "fusion_hint": f"Slice + supporting ops. {nodes} nodes total.",
        "main_risk": "medium",
        "confidence": "high",
        "pattern": "Slice-based multi-op",
    }


def _custom(ops_str, nodes):
    return {
        "recommended_architecture": "custom_multi_op",
        "locality": "varies",
        "single_linear_conv_possible": "no",
        "recommended_kernel": "varies",
        "nonlinearity_needed": "unknown",
        "memory_priority": f"Complex multi-op architecture ({nodes} nodes). Study baseline directly.",
        "fusion_hint": f"Ops: {ops_str[:100]}...",
        "main_risk": "high",
        "confidence": "medium",
        "pattern": "Custom multi-op",
    }


def analyze_task_data(tid: int) -> dict | None:
    """从输入 JSON 提取任务基本特征"""
    path = INPUT_DIR / f"task{tid:03d}.json"
    if not path.exists():
        return None

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    trains = data.get("train", [])
    tests = data.get("test", [])
    arcgen = data.get("arc-gen", [])

    info = {
        "train_count": len(trains),
        "test_count": len(tests),
        "arcgen_count": len(arcgen),
    }

    all_ex = trains + tests
    if not all_ex:
        info["sizes"] = "no_data"
        info["same_size"] = None
        info["colors_in"] = []
        info["colors_out"] = []
        return info

    # Size analysis
    sizes_in = Counter()
    sizes_out = Counter()
    for e in all_ex:
        sizes_in[(len(e["input"]), len(e["input"][0]))] += 1
        sizes_out[(len(e["output"]), len(e["output"][0]))] += 1

    same_size = all(
        len(e["input"]) == len(e["output"]) and len(e["input"][0]) == len(e["output"][0])
        for e in all_ex
    )
    info["same_size"] = same_size

    in_dims = f"{len(sizes_in)} unique sizes"
    out_dims = f"{len(sizes_out)} unique sizes"
    if len(sizes_in) == 1:
        h, w = next(iter(sizes_in))
        in_dims = f"{h}x{w} (all same)"
    if len(sizes_out) == 1:
        h, w = next(iter(sizes_out))
        out_dims = f"{h}x{w} (all same)"

    info["input_sizes"] = in_dims
    info["output_sizes"] = out_dims

    # Color analysis
    in_colors = set()
    out_colors = set()
    for e in all_ex:
        for row in e["input"]:
            in_colors.update(row)
        for row in e["output"]:
            out_colors.update(row)

    info["colors_in"] = sorted(in_colors)
    info["colors_out"] = sorted(out_colors)
    info["same_colors"] = in_colors == out_colors
    info["out_subset_in"] = out_colors.issubset(in_colors) and in_colors != out_colors

    # Determine likely task type from data
    if same_size and in_colors == out_colors and max(len(e["input"]) for e in all_ex) <= 5:
        info["likely_type"] = "pixel_color_mapping_or_permutation"
    elif same_size:
        info["likely_type"] = "local_neighborhood_or_global_statistics"
    else:
        info["likely_type"] = "spatial_transform_resize_crop_expand"

    return info


def generate_spec(tid: int, data_info: dict, arch_info: dict) -> str:
    """生成完整的 spec 文件内容（AGENTSforSpec 格式）"""

    colors_in_str = str(data_info.get("colors_in", []))
    colors_out_str = str(data_info.get("colors_out", []))

    # Determine the suggested approach sentence
    if arch_info.get("pattern", "").startswith("Gather"):
        approach = "Use Gather-based lookup or spatial permutation — no Conv needed."
    elif arch_info.get("pattern", "").startswith("Slice"):
        approach = "Use Slice+Pad for spatial crop/flip/reposition — no Conv needed."
    elif arch_info.get("pattern") == "Transpose H<->W swap":
        approach = "Use Transpose for H<->W swap — 0 params, free."
    elif arch_info.get("pattern", "").startswith("Single Conv"):
        approach = "Single Conv is sufficient — keep it simple."
    elif "Reduce" in arch_info.get("pattern", ""):
        approach = "Use ReduceSum/ReduceMax + threshold logic — no Conv needed."
    elif "Conv" in arch_info.get("pattern", ""):
        approach = "Conv + supporting ops (Reduce/Where). Refer to baseline for exact op sequence."
    else:
        approach = "Study baseline ONNX directly for optimal architecture."

    spec = f"""# Task {tid:03d} 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 输入尺寸: {data_info.get('input_sizes', 'varies')}，输出尺寸: {data_info.get('output_sizes', 'varies')}。
- 同尺寸变换: {'是' if data_info.get('same_size') else '否（输入/输出尺寸不同）'}。
- 输入颜色: {colors_in_str}，输出颜色: {colors_out_str}。
- 颜色集一致: {'是' if data_info.get('same_colors') else '否'}。{'输出颜色为输入颜色的子集' if data_info.get('out_subset_in') else ''}
- 推测任务类型: {data_info.get('likely_type', 'unknown')}。

> **注意**: 以上为数据特征自动提取。具体变换规则需人工/LLM 分析 train/test 样例后补充。

## 2. 关键证据

- 训练样本: {data_info.get('train_count', '?')} 个，测试样本: {data_info.get('test_count', '?')} 个，ARC-GEN 样本: {data_info.get('arcgen_count', '?')} 个。
- 输入样例可能包含多种尺寸和颜色组合，详见 `input/task{tid:03d}.json`。
- 架构方案已由 baseline ONNX 验证通过（{arch_info.get('node_count', '?')} 节点，{arch_info.get('size_bytes', '?')} 字节）。

> **建议**: 运行 `python tools/task_scanner.py` 查看任务分类，或手动查看 `input/task{tid:03d}.json`。

## 3. 歧义与风险

- 歧义点: 具体变换规则尚未人工分析。当前仅基于数据特征推测。风险等级: `medium`。
- Baseline 已验证可用，架构方向可信。风险等级: `low`。

## 4. NeuroGolf 架构提示

> **以下内容来自 baseline ONNX（已验证 100% 通过所有测试用例）**

- `recommended_architecture`: `{arch_info.get('recommended_architecture', 'unknown')}`
- `locality`: `{arch_info.get('locality', 'varies')}`
- `single_linear_conv_possible`: `{arch_info.get('single_linear_conv_possible', 'unknown')}`
- `recommended_kernel`: `{arch_info.get('recommended_kernel', 'varies')}`
- `nonlinearity_needed`: `{arch_info.get('nonlinearity_needed', 'unknown')}`
- `memory_priority`: {arch_info.get('memory_priority', 'N/A')}
- `fusion_hint`: {arch_info.get('fusion_hint', 'N/A')}
- `approach`: {approach}

Baseline 实际架构: **{arch_info.get('pattern', '?')}** — {arch_info.get('actual_ops', '?')} ({arch_info.get('node_count', '?')} nodes, {arch_info.get('init_count', '?')} initializers, {arch_info.get('size_bytes', '?')} bytes)

## 5. 最终摘要

```yaml
task_id: {tid:03d}
train_samples: {data_info.get('train_count', '?')}
test_samples: {data_info.get('test_count', '?')}
arcgen_samples: {data_info.get('arcgen_count', '?')}
same_size: {data_info.get('same_size', 'unknown')}
colors_in: {colors_in_str}
colors_out: {colors_out_str}
locality: {arch_info.get('locality', 'varies')}
single_linear_conv_possible: {arch_info.get('single_linear_conv_possible', 'unknown')}
recommended_architecture: {arch_info.get('recommended_architecture', 'unknown')}
recommended_kernel: {arch_info.get('recommended_kernel', 'varies')}
nonlinearity_needed: {arch_info.get('nonlinearity_needed', 'unknown')}
memory_priority: {arch_info.get('memory_priority', 'N/A')}
fusion_hint: {arch_info.get('fusion_hint', 'N/A')}
approach: {approach}
main_risk: {arch_info.get('main_risk', 'unknown')}
confidence: {arch_info.get('confidence', 'medium')}
baseline_pattern: {arch_info.get('pattern', 'unknown')}
baseline_ops: {arch_info.get('actual_ops', '?')}
baseline_nodes: {arch_info.get('node_count', '?')}
baseline_size_bytes: {arch_info.get('size_bytes', '?')}
```
"""
    return spec


def process_task(tid: int, dry_run: bool = False) -> bool:
    """处理单个任务：生成或更新 spec"""
    data_info = analyze_task_data(tid)
    arch_info = analyze_baseline(tid)

    if data_info is None:
        print(f"  task{tid:03d}: no input data, skipping")
        return False
    if arch_info is None:
        print(f"  task{tid:03d}: no baseline ONNX, skipping")
        return False

    spec = generate_spec(tid, data_info, arch_info)

    if dry_run:
        print(f"  task{tid:03d}: {arch_info.get('pattern', '?')} ({arch_info.get('node_count','?')}n) "
              f"in={data_info.get('input_sizes','?')} out={data_info.get('output_sizes','?')} "
              f"colors_in={data_info.get('colors_in',[])} colors_out={data_info.get('colors_out',[])}")
        return True

    spec_path = SPEC_DIR / f"task{tid:03d}_spec.md"
    spec_path.write_text(spec, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="为 tasks 101-400 生成 problem_spec")
    parser.add_argument("--all", action="store_true", help="全部 101-400")
    parser.add_argument("--start", type=int, default=101)
    parser.add_argument("--end", type=int, default=400)
    parser.add_argument("--tasks", type=str, help="逗号分隔的任务ID")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.tasks:
        task_range = [int(t.strip()) for t in args.tasks.split(",")]
    else:
        task_range = range(args.start, args.end + 1)

    generated = 0
    skipped = 0
    patterns = Counter()

    for tid in task_range:
        arch_info = analyze_baseline(tid)
        if arch_info:
            patterns[arch_info.get("pattern", "unknown")] += 1

        if process_task(tid, dry_run=args.dry_run):
            generated += 1
        else:
            skipped += 1

    print(f"\nGenerated: {generated}, Skipped: {skipped}")

    if not args.dry_run:
        print("\n=== 架构模式分布 ===")
        for pat, cnt in patterns.most_common():
            print(f"  {pat:<40} {cnt:>4}")

    if args.dry_run:
        print("[DRY RUN] No files written.")


if __name__ == "__main__":
    main()
