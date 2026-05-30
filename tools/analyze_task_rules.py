"""分析每个任务的 train/test 样例，自动推断变换规则，更新 spec。

支持的规则检测:
- 颜色映射表 (gather_lookup): 检测逐像素颜色映射
- 空间变换 (gather_spatial/slice_pad): 检测行/列重排、裁剪、翻转
- 转置 (transpose): 检测 H<->W 交换
- 邻域操作 (single_conv): 检测 3x3 邻域规则
- 复杂逻辑: 标记为需要人工分析

Usage:
    python tools/analyze_task_rules.py --tasks 16,53,87  # 指定任务
    python tools/analyze_task_rules.py --tier1            # 全部 Tier1 任务
    python tools/analyze_task_rules.py --all --dry-run    # 预览全部
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

# Tasks by baseline architecture
SIMPLE_ARCHS = {
    'gather_lookup', 'gather_spatial', 'transpose', 'slice_pad', 'single_conv',
    'gather_based_multi_op', 'slice_based_multi_op',
}


def get_arch(tid: int) -> str:
    spec_path = SPEC_DIR / f"task{tid:03d}_spec.md"
    if not spec_path.exists():
        return ''
    text = spec_path.read_text(encoding='utf-8')
    for line in text.split('\n'):
        if line.strip().startswith('- `recommended_architecture`:'):
            parts = line.split('`')
            if len(parts) >= 4:
                return parts[3]
    return ''


def load_task_data(tid: int) -> dict:
    with open(INPUT_DIR / f"task{tid:03d}.json", encoding='utf-8') as f:
        return json.load(f)


def detect_color_mapping(trains: list) -> dict | None:
    """检测逐像素颜色映射规则"""
    mapping = {}
    for e in trains:
        inp = e['input']
        out = e['output']
        if len(inp) != len(out) or (inp and len(inp[0]) != len(out[0])):
            return None  # Different sizes - not a per-pixel mapping

        for r in range(len(inp)):
            for c in range(len(inp[0])):
                in_color = inp[r][c]
                out_color = out[r][c]
                if in_color in mapping:
                    if mapping[in_color] != out_color:
                        return None  # Inconsistent mapping
                else:
                    mapping[in_color] = out_color

    if not mapping:
        return None

    # Check if it's a permutation (bijection on active colors)
    mapped_from = set(mapping.keys())
    mapped_to = set(mapping.values())

    return {
        'type': 'color_mapping',
        'mapping': {k: v for k, v in sorted(mapping.items())},
        'is_permutation': mapped_from == mapped_to and len(mapped_from) == len(mapping),
        'is_swap': all(
            mapping.get(v) == k for k, v in mapping.items() if v in mapping
        ),
        'identity_count': sum(1 for k, v in mapping.items() if k == v),
    }


def detect_spatial_shift(trains: list) -> dict | None:
    """检测空间位移（平移、翻转、旋转）"""
    if not trains:
        return None

    first = trains[0]
    inp = first['input']
    out = first['output']
    in_h, in_w = len(inp), len(inp[0])
    out_h, out_w = len(out), len(out[0])

    # Check all examples for consistency
    shifts_found = []
    for e in trains:
        inp = e['input']
        out = e['output']

        # Check for row permutation (Gather on axis=2)
        if in_h == out_h and in_w == out_w:
            # Try to find row mapping
            row_map = {}
            for out_r in range(out_h):
                for in_r in range(in_h):
                    if inp[in_r] == out[out_r]:
                        row_map[out_r] = in_r
                        break

            if len(row_map) >= min(in_h, out_h) * 0.8:
                # Check for common patterns
                keys = sorted(row_map.keys())
                vals = [row_map[k] for k in keys]

                pattern = 'unknown'
                if vals == list(range(len(vals))):
                    pattern = 'identity'
                elif all(v == (k + 1) % in_h for k, v in zip(keys, vals)):
                    pattern = 'shift_up'
                elif all(v == (k - 1) % in_h for k, v in zip(keys, vals)):
                    pattern = 'shift_down'
                elif vals == list(reversed(range(len(vals)))):
                    pattern = 'flip_vertical'

                shifts_found.append({
                    'pattern': pattern,
                    'row_map': dict(zip(keys, vals)),
                })

    if not shifts_found:
        return None

    # Check consistency
    patterns = [s['pattern'] for s in shifts_found]
    if all(p == patterns[0] for p in patterns):
        return {
            'type': 'spatial_shift',
            'pattern': patterns[0],
            'row_map': shifts_found[0]['row_map'],
            'same_size': in_h == out_h and in_w == out_w,
        }
    return None


def detect_flip_or_transpose(trains: list) -> dict | None:
    """检测翻转或转置"""
    if not trains:
        return None

    first = trains[0]
    inp = first['input']
    out = first['output']
    in_h, in_w = len(inp), len(inp[0])
    out_h, out_w = len(out), len(out[0])

    # Check transpose
    if in_h == out_w and in_w == out_h:
        all_transpose = True
        for e in trains:
            inp = e['input']
            out = e['output']
            for r in range(in_h):
                for c in range(in_w):
                    if inp[r][c] != out[c][r]:
                        all_transpose = False
                        break
        if all_transpose:
            return {'type': 'transpose', 'pattern': 'H_W_swap'}

    # Check horizontal flip
    if in_h == out_h and in_w == out_w:
        all_hflip = True
        for e in trains:
            inp = e['input']
            out = e['output']
            for r in range(in_h):
                for c in range(in_w):
                    if inp[r][c] != out[r][in_w - 1 - c]:
                        all_hflip = False
                        break
        if all_hflip:
            return {'type': 'flip', 'pattern': 'horizontal'}

        # Check vertical flip
        all_vflip = True
        for e in trains:
            inp = e['input']
            out = e['output']
            for r in range(in_h):
                for c in range(in_w):
                    if inp[r][c] != out[in_h - 1 - r][c]:
                        all_vflip = False
                        break
        if all_vflip:
            return {'type': 'flip', 'pattern': 'vertical'}

    return None


def detect_crop(trains: list) -> dict | None:
    """检测裁剪操作"""
    if not trains:
        return None

    first = trains[0]
    inp = first['input']
    out = first['output']
    in_h, in_w = len(inp), len(inp[0])
    out_h, out_w = len(out), len(out[0])

    if in_h < out_h or in_w < out_w:
        return None  # Not a crop

    # For each example, find where the output matches the input
    crops = []
    for e in trains:
        inp = e['input']
        out = e['output']

        # Simple case: output == input[r0:r0+oh, c0:c0+ow]
        found = False
        for r0 in range(in_h - out_h + 1):
            for c0 in range(in_w - out_w + 1):
                match = True
                for r in range(out_h):
                    if inp[r0 + r][c0:c0 + out_w] != out[r]:
                        match = False
                        break
                if match:
                    crops.append({'r0': r0, 'c0': c0, 'oh': out_h, 'ow': out_w})
                    found = True
                    break
            if found:
                break

    if len(crops) == len(trains):
        positions = [(c['r0'], c['c0']) for c in crops]
        if all(p == positions[0] for p in positions):
            return {
                'type': 'crop',
                'r0': positions[0][0],
                'c0': positions[0][1],
                'crop_h': out_h,
                'crop_w': out_w,
                'input_h': in_h,
                'input_w': in_w,
            }

    return None


def detect_neighbor_rule(trains: list) -> dict | None:
    """尝试检测局部邻域规则（对于 small Conv 任务）"""
    if not trains:
        return None

    first = trains[0]
    inp = first['input']
    out = first['output']
    in_h, in_w = len(inp), len(inp[0])
    out_h, out_w = len(out), len(out[0])

    if in_h != out_h or in_w != out_w:
        return {'type': 'neighbor_rule', 'note': 'input/output sizes differ, likely spatial transform'}

    # For same-size tasks, note that rule likely involves neighbor operations
    # Specific rule deduction would require deeper analysis
    return {
        'type': 'neighbor_rule',
        'same_size': True,
        'grid_size': f'{in_h}x{in_w}',
        'note': 'Same-size transform, likely involves local neighborhood operations'
    }


def format_color_rule(rule: dict) -> str:
    """Format color mapping rule for spec"""
    mapping = rule['mapping']

    # Find swap pairs
    swaps = []
    identity = []
    used = set()
    for k, v in sorted(mapping.items()):
        if k in used:
            continue
        if mapping.get(v) == k and k != v:
            swaps.append(f'{k}<->{v}')
            used.add(k)
            used.add(v)
        elif k == v:
            identity.append(str(k))
        else:
            swaps.append(f'{k}->{v}')

    lines = []
    lines.append(f"- 核心变换：逐像素颜色映射（同尺寸，每个位置独立映射）。")
    if swaps:
        lines.append(f"- 颜色映射：{' '.join(swaps)}。")
    if identity:
        lines.append(f"- 保持不变的通道：{' '.join(identity)}。")
    lines.append(f"- 完整映射表：`{mapping}`")
    lines.append(f"- 实质是{'排列（置换）' if rule.get('is_permutation') else '部分映射'}，"
                 f"{'且' if rule.get('is_swap') else '非'}对称互换。")
    return '\n'.join(lines)


def format_spatial_rule(rule: dict) -> str:
    """Format spatial shift rule for spec"""
    pattern = rule.get('pattern', 'unknown')
    desc = {
        'shift_up': '整体向上平移一行（第一行移出，最后一行填入背景）',
        'shift_down': '整体向下平移一行（最后一行移出，第一行填入背景）',
        'flip_vertical': '垂直翻转（上下镜像）',
        'flip_horizontal': '水平翻转（左右镜像）',
        'identity': '恒等变换',
    }
    row_map = rule.get('row_map', {})
    return f"- 核心变换：空间行重排。{desc.get(pattern, pattern)}。\n- 行映射关系：`{row_map}`"


def format_crop_rule(rule: dict) -> str:
    """Format crop rule for spec"""
    return (f"- 核心变换：裁剪。从 {rule['input_h']}x{rule['input_w']} 输入中裁出 "
            f"({rule['r0']},{rule['c0']}) 开始的 {rule['crop_h']}x{rule['crop_w']} 子区域。")


def analyze_and_update_spec(tid: int, dry_run: bool = False) -> str | None:
    """分析任务规则并生成更新的 spec Section 1"""
    arch = get_arch(tid)
    data = load_task_data(tid)
    trains = data.get('train', [])
    tests = data.get('test', [])

    if not trains:
        return None

    rule_desc = None

    # Try different detectors based on architecture
    if arch in ('gather_lookup',):
        rule = detect_color_mapping(trains)
        if rule:
            rule_desc = format_color_rule(rule)

    if arch in ('gather_spatial',) and not rule_desc:
        rule = detect_spatial_shift(trains)
        if rule:
            rule_desc = format_spatial_rule(rule)

    if arch in ('slice_pad',) and not rule_desc:
        rule = detect_crop(trains)
        if rule:
            rule_desc = format_crop_rule(rule)
        if not rule_desc:
            rule = detect_flip_or_transpose(trains)
            if rule:
                rule_desc = (f"- 核心变换：{'H<->W transpose' if rule.get('pattern') == 'H_W_swap' else rule.get('pattern', '')}翻转。\n"
                            f"- 0 参数即可实现。")

    if arch in ('transpose',) and not rule_desc:
        rule = detect_flip_or_transpose(trains)
        if rule:
            rule_desc = (f"- 核心变换：矩阵转置（H↔W 维度交换）。\n"
                        f"- 每个像素 output[r][c] = input[c][r]。\n"
                        f"- 使用 Transpose(perm=[0,1,3,2])，0 参数。")

    if arch == 'single_conv' and not rule_desc:
        # Try color mapping first (might be wrong architecture)
        rule = detect_color_mapping(trains)
        if rule and rule.get('is_permutation'):
            rule_desc = format_color_rule(rule) + "\n- **注意**: baseline 使用单 Conv，但此任务本质是颜色映射，"
            rule_desc += "可能用 Gather 更优。"
        else:
            rule_desc = detect_neighbor_rule(trains)
            if rule_desc:
                rule_desc = (f"- 核心变换：局部邻域操作。输入/输出同尺寸({rule_desc['grid_size']})。\n"
                            f"- baseline 使用单层 Conv 实现，具体权重需分析训练样例确定。\n"
                            f"- 建议打印 train 样例分析邻域规则（3×3 范围内像素变化模式）。")

    if not rule_desc:
        # Generic analysis
        first = trains[0]
        in_h, in_w = len(first['input']), len(first['input'][0])
        out_h, out_w = len(first['output']), len(first['output'][0])
        rule_desc = (f"- 变换类型：{arch or '未知'}。\n"
                    f"- 输入尺寸 {in_h}x{in_w}，输出尺寸 {out_h}x{out_w}。\n"
                    f"- 需手动分析 train 样例确定具体规则。")

    if dry_run:
        return rule_desc

    # Update the spec file
    spec_path = SPEC_DIR / f"task{tid:03d}_spec.md"
    if not spec_path.exists():
        return rule_desc

    spec = spec_path.read_text(encoding='utf-8')

    # Replace Section 1 (between "## 1. 核心规则" and "## 2. 关键证据")
    start = spec.find("## 1. 核心规则")
    end = spec.find("## 2. 关键证据")

    if start == -1 or end == -1:
        return rule_desc

    # Keep the auto-generated note
    note_start = spec.find("> **注意**", start, end)
    if note_start == -1:
        note_start = spec.find("> **Auto-generated", start, end)

    new_section1 = "## 1. 核心规则\n\n" + rule_desc + "\n"
    if note_start != -1:
        new_section1 += "\n" + spec[note_start:end].strip() + "\n"

    new_spec = spec[:start] + new_section1 + "\n" + spec[end:]
    spec_path.write_text(new_spec, encoding='utf-8')

    return rule_desc


def main():
    parser = argparse.ArgumentParser(description="分析任务规则并更新 spec")
    parser.add_argument("--tasks", type=str, help="e.g. 16,53,87,179")
    parser.add_argument("--tier1", action="store_true", help="所有简单架构任务")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.tasks:
        tids = [int(t.strip()) for t in args.tasks.split(",")]
    elif args.tier1:
        tids = []
        for tid in range(1, 401):
            arch = get_arch(tid)
            if arch in SIMPLE_ARCHS:
                tids.append(tid)
    elif args.all:
        tids = list(range(1, 401))
    else:
        print("Specify --tasks, --tier1, or --all")
        return

    analyzed = 0
    for tid in tids:
        result = analyze_and_update_spec(tid, dry_run=args.dry_run)
        if result:
            analyzed += 1
            if args.dry_run:
                print(f"\n=== task{tid:03d} ({get_arch(tid)}) ===")
                print(result)

    print(f"\nAnalyzed: {analyzed}/{len(tids)}")
    if args.dry_run:
        print("[DRY RUN] No files modified.")
    else:
        print("Specs updated.")


if __name__ == "__main__":
    main()
