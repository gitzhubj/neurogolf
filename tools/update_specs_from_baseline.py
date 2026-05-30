"""根据 baseline ONNX 文件修正 problem_specs 的架构提示

baseline 是已验证可用的方案，用它来纠正 spec 中的错误架构建议。

Usage:
    python tools/update_specs_from_baseline.py --all       # 更新全部 400 个 spec
    python tools/update_specs_from_baseline.py --tasks 1-10 # 更新指定范围
    python tools/update_specs_from_baseline.py --dry-run   # 预览不写入
"""
import sys
import re
import onnx
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = REPO_ROOT / "problem_specs"
BASELINE_DIR = REPO_ROOT / "baseline"

# YAML section to replace markers
YAML_START = "## 5. 最终摘要"
ARCH_START = "## 4. NeuroGolf 架构提示"


def analyze_baseline(tid: int) -> dict | None:
    """分析 baseline ONNX 返回正确的架构提示"""
    path = BASELINE_DIR / f"task{tid:03d}.onnx"
    if not path.exists():
        return None

    model = onnx.load(str(path))
    ops = [n.op_type for n in model.graph.node]
    op_set = set(ops)
    node_count = len(ops)
    init_count = sum(1 for _ in model.graph.initializer)

    info = {
        "node_count": node_count,
        "init_count": init_count,
        "actual_ops": "+".join(sorted(op_set)),
    }

    if ops == ["Gather"]:
        axis = 1
        for attr in model.graph.node[0].attribute:
            if attr.name == "axis":
                axis = attr.i
        if axis == 1:
            info.update({
                "recommended_architecture": "gather_lookup",
                "locality": "0",
                "single_linear_conv_possible": "yes",
                "recommended_kernel": "not_needed",
                "nonlinearity_needed": "no",
                "memory_priority": "Use Gather(axis=1, indices=[color_table]) instead of 1x1 Conv. Saves 90% params.",
                "fusion_hint": "Single Gather node. Channel index permutation is all that is needed.",
                "main_risk": "low — pattern confirmed by baseline",
                "confidence": "high",
            })
        else:
            info.update({
                "recommended_architecture": "gather_spatial",
                "locality": "1",
                "single_linear_conv_possible": "yes",
                "recommended_kernel": "not_needed",
                "nonlinearity_needed": "no",
                "memory_priority": "Use Gather(axis=2/3, indices=[row/col_order]) instead of Conv. Saves 96% params.",
                "fusion_hint": "Single Gather node on spatial axis for permutation.",
                "main_risk": "low — pattern confirmed by baseline",
                "confidence": "high",
            })
    elif ops == ["Transpose"]:
        info.update({
            "recommended_architecture": "transpose",
            "locality": "global",
            "single_linear_conv_possible": "yes",
            "recommended_kernel": "not_needed",
            "nonlinearity_needed": "no",
            "memory_priority": "Transpose(perm=[0,1,3,2]) is free (0 params).",
            "fusion_hint": "Single Transpose node swaps H and W.",
            "main_risk": "low",
            "confidence": "high",
        })
    elif op_set == {"Slice", "Pad"}:
        info.update({
            "recommended_architecture": "slice_pad",
            "locality": "0",
            "single_linear_conv_possible": "yes",
            "recommended_kernel": "not_needed",
            "nonlinearity_needed": "no",
            "memory_priority": "Slice to crop, Pad to restore 30x30. Minimal memory.",
            "fusion_hint": "Two nodes: Slice(extract) + Pad(restore). Step=-1 gives free flip.",
            "main_risk": "low — pattern confirmed by baseline",
            "confidence": "high",
        })
    elif ops == ["Conv"]:
        info.update({
            "recommended_architecture": "single_conv",
            "locality": "k",
            "single_linear_conv_possible": "yes",
            "recommended_kernel": "3x3",
            "nonlinearity_needed": "no",
            "memory_priority": "Single Conv, bias-free. Keep kernel minimal.",
            "fusion_hint": "All logic in one Conv weight tensor.",
            "main_risk": "low",
            "confidence": "high",
        })
    elif "Conv" in op_set:
        nonlinear = "yes" if "Relu" in op_set else "no"
        info.update({
            "recommended_architecture": "conv_with_logic",
            "locality": "k",
            "single_linear_conv_possible": "no",
            "recommended_kernel": "3x3",
            "nonlinearity_needed": nonlinear,
            "memory_priority": "Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.",
            "fusion_hint": f"Baseline uses {node_count} nodes: {info['actual_ops'][:60]}. Study baseline for optimal op sequence.",
            "main_risk": "medium — multi-op, check baseline for correct sequence",
            "confidence": "high",
        })
    elif "ReduceSum" in op_set or "ReduceMax" in op_set:
        has_where = "Where" in op_set
        info.update({
            "recommended_architecture": "reduce_with_where" if has_where else "reduce_only",
            "locality": "global",
            "single_linear_conv_possible": "no",
            "recommended_kernel": "not_needed",
            "nonlinearity_needed": "no",
            "memory_priority": "Reduce + threshold + conditional. No Conv needed.",
            "fusion_hint": f"Baseline uses {node_count} nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.",
            "main_risk": "medium — check baseline for exact op sequence",
            "confidence": "high",
        })
    else:
        info.update({
            "recommended_architecture": "custom_multi_op",
            "locality": "varies",
            "single_linear_conv_possible": "no",
            "recommended_kernel": "varies",
            "nonlinearity_needed": "unknown",
            "memory_priority": f"Multi-op custom architecture ({node_count} nodes). Study baseline directly.",
            "fusion_hint": f"Ops used: {info['actual_ops'][:80]}...",
            "main_risk": "high — complex architecture, refer to baseline",
            "confidence": "medium",
        })

    return info


def generate_new_arch_section(info: dict) -> str:
    """生成修正后的架构提示段落"""
    return f"""## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `{info.get('recommended_architecture', 'unknown')}`
- `locality`: `{info.get('locality', 'varies')}`
- `single_linear_conv_possible`: `{info.get('single_linear_conv_possible', 'unknown')}`
- `recommended_kernel`: `{info.get('recommended_kernel', 'varies')}`
- `nonlinearity_needed`: `{info.get('nonlinearity_needed', 'unknown')}`
- `memory_priority`: {info.get('memory_priority', 'N/A')}
- `fusion_hint`: {info.get('fusion_hint', 'N/A')}

Baseline 实际架构: {info.get('actual_ops', '?')} ({info.get('node_count', '?')} nodes, {info.get('init_count', '?')} initializers)"""


def generate_new_yaml_section(info: dict, tid: int) -> str:
    """生成修正后的 YAML 摘要"""
    return f"""## 5. 最终摘要

```yaml
task_id: {tid:03d}
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: {info.get('locality', 'varies')}
single_linear_conv_possible: {info.get('single_linear_conv_possible', 'unknown')}
recommended_architecture: {info.get('recommended_architecture', 'unknown')}
memory_priority: {info.get('memory_priority', 'N/A')}
fusion_hint: {info.get('fusion_hint', 'N/A')}
main_risk: {info.get('main_risk', 'unknown')}
confidence: {info.get('confidence', 'medium')}
actual_ops: {info.get('actual_ops', '?')}
actual_nodes: {info.get('node_count', '?')}
```"""


def update_spec(tid: int, info: dict, dry_run: bool = False) -> bool:
    """更新单个 spec 文件的架构部分"""
    spec_path = SPEC_DIR / f"task{tid:03d}_spec.md"
    if not spec_path.exists():
        print(f"  task{tid:03d}: spec not found, skipping")
        return False

    old_spec = spec_path.read_text(encoding="utf-8")

    # Find and replace Section 4 (架构提示)
    arch_start = old_spec.find("## 4. NeuroGolf 架构提示")
    yaml_start = old_spec.find("## 5. 最终摘要")

    if arch_start == -1 or yaml_start == -1:
        print(f"  task{tid:03d}: cannot find sections 4/5 in spec, skipping")
        return False

    new_arch = generate_new_arch_section(info)
    new_yaml = generate_new_yaml_section(info, tid)

    new_spec = old_spec[:arch_start] + new_arch + "\n\n" + new_yaml + "\n"

    if dry_run:
        old_rec = ""
        m = re.search(r"recommended_architecture:\s*(\S+)", old_spec[arch_start:yaml_start])
        if m:
            old_rec = m.group(1)
        new_rec = info.get("recommended_architecture", "?")
        print(f"  task{tid:03d}: {old_rec} -> {new_rec} ({info.get('actual_ops','?')}, {info.get('node_count','?')} nodes)")
        return True

    spec_path.write_text(new_spec, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="根据 baseline 修正 spec 架构提示")
    parser.add_argument("--all", action="store_true", help="处理全部 400 个 spec")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=100)
    parser.add_argument("--tasks", type=str, help="逗号分隔的任务ID，如 16,53,87")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    args = parser.parse_args()

    if args.all:
        task_range = range(1, 401)
    elif args.tasks:
        task_range = [int(t.strip()) for t in args.tasks.split(",")]
    else:
        task_range = range(args.start, args.end + 1)

    updated = 0
    skipped = 0

    for tid in task_range:
        info = analyze_baseline(tid)
        if info is None:
            skipped += 1
            continue

        if update_spec(tid, info, dry_run=args.dry_run):
            updated += 1

    print(f"\nUpdated: {updated}, Skipped: {skipped}")

    if args.dry_run:
        print("[DRY RUN] No files were modified. Remove --dry-run to apply changes.")


if __name__ == "__main__":
    main()
