"""对比 cost 并生成报告"""
import sys
import json
import argparse
import re
import os
from pathlib import Path
from compute_cost import compute_cost


def extract_task_id(filename: str) -> str | None:
    m = re.search(r'task(\d+)', Path(filename).name)
    return m.group(1) if m else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--registry', required=True)
    parser.add_argument('--changed', required=True)
    parser.add_argument('--output', default='report.md')
    args = parser.parse_args()

    with open(args.registry) as f:
        registry = json.load(f)

    improved = []
    regressed = []
    unchanged = []
    errors = []

    for onnx_path in args.changed.split():
        if not onnx_path.strip():
            continue
        tid = extract_task_id(onnx_path)
        if not tid:
            errors.append((onnx_path, "无法提取任务 ID"))
            continue

        try:
            result = compute_cost(onnx_path)
        except Exception as e:
            errors.append((onnx_path, str(e)))
            continue

        new_cost = result['cost']
        old_entry = registry['tasks'].get(tid, {})
        old_cost = old_entry.get('cost', None)

        if old_cost is None:
            improved.append((tid, 0, new_cost, new_cost, result))
        else:
            delta = old_cost - new_cost
            if delta > 0:
                improved.append((tid, old_cost, new_cost, delta, result))
            elif delta < 0:
                regressed.append((tid, old_cost, new_cost, -delta, result))
            else:
                unchanged.append((tid, new_cost, result))

    lines = ["## ONNX Cost 对比报告", ""]

    if errors:
        lines.append("### 错误")
        for path, err in errors:
            lines.append(f"- **{path}**: {err}")
        lines.append("")

    if improved or regressed or unchanged:
        lines.append("| 任务 | 旧 Cost | 新 Cost | 变化 | 参数 | 内存 |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for tid, old, new, delta, r in improved:
            lines.append(f"| task{tid} | {old} | {new} | **-{delta}** :rocket: | {r['params']} | {r['memory_bytes']} |")
        for tid, old, new, delta, r in regressed:
            lines.append(f"| task{tid} | {old} | {new} | **+{delta}** :warning: | {r['params']} | {r['memory_bytes']} |")
        for tid, cost, r in unchanged:
            lines.append(f"| task{tid} | {cost} | {cost} | 0 | {r['params']} | {r['memory_bytes']} |")
        lines.append("")

    if errors and not improved:
        lines.append("### :x: 验证失败，请修复错误后重新提交")
    elif regressed:
        lines.append("### :warning: 有任务 cost 上升，请检查")
    elif improved:
        names = ", ".join(f"task{t}" for t, _, _, _, _ in improved)
        lines.append(f"### :white_check_mark: {len(improved)} 个任务 cost 下降: {names}")
        lines.append("此 PR 可自动合并。")
    else:
        lines.append("### Cost 无变化")

    report = '\n'.join(lines)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    is_improved = bool(improved) and not regressed and not errors
    with open('improved.txt', 'w') as f:
        f.write('true' if is_improved else 'false')


if __name__ == '__main__':
    main()
