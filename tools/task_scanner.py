"""任务扫描器 — 批量分析 400 个任务并按可实现性排序

模仿 codegolf 的"从简单到困难排序"策略，为 agent 提供优先级清单。

Usage:
    python tools/task_scanner.py                    # 扫描全部 400 个任务
    python tools/task_scanner.py --top 20           # 只显示前 20 个优先任务
    python tools/task_scanner.py --tier 1           # 只显示 Tier 1 任务
    python tools/task_scanner.py --export tasks.csv # 导出 CSV
"""
import sys
import json
import argparse
import csv
import os
from pathlib import Path

# Windows console encoding fix
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = REPO_ROOT / "problem_specs"
INPUT_DIR = REPO_ROOT / "input"

# 更新：基于 baseline 验证的架构分类
# Tier 1 = 最简单（1-2 节点，无 Conv）
TIER1_KEYWORDS = [
    "gather_lookup",
    "transpose",
    "slice_pad",
    "single_conv",
    "Gather channel lookup",
    "Transpose H<->W swap",
    "Slice + Pad crop",
]
# Tier 2 = 简单（少量节点，无/少 Conv）
TIER2_KEYWORDS = [
    "gather_spatial",
    "slice_based_multi_op",
    "gather_based_multi_op",
    "Gather spatial permutation",
    "Slice-based multi-op",
    "Gather-based multi-op",
]
# Tier 5 = 需要复杂逻辑（Conv + logic / Reduce + Where / 多节点）
TIER5_KEYWORDS = [
    "conv_with_logic",
    "reduce_with_where",
    "reduce_only",
    "custom_multi_op",
    "Conv + logic",
    "Reduce + Where",
    "Reduce + arithmetic",
    "Custom multi-op",
]


def classify_task(tid: int) -> dict:
    """基于 spec + 数据快速分类单个任务"""
    spec_path = SPEC_DIR / f"task{tid:03d}_spec.md"
    data_path = INPUT_DIR / f"task{tid:03d}.json"

    result = {
        "tid": tid,
        "has_spec": spec_path.exists(),
        "has_data": data_path.exists(),
        "train_count": 0,
        "test_count": 0,
        "arcgen_count": 0,
        "same_size": None,
        "spec_text": "",
        "tier": "unknown",
        "reason": "",
    }

    # 读 spec
    if spec_path.exists():
        spec_text = spec_path.read_text(encoding="utf-8")
        result["spec_text"] = spec_text

        # 关键词匹配分类
        if any(kw in spec_text for kw in TIER1_KEYWORDS):
            result["tier"] = "Tier1"
            result["reason"] = "Gather/Transpose/Slice-Pad（最简单）"
        elif any(kw in spec_text for kw in TIER2_KEYWORDS):
            result["tier"] = "Tier2"
            result["reason"] = "Gather-spatial/Slice多步（较简单）"
        elif any(kw in spec_text for kw in TIER5_KEYWORDS):
            result["tier"] = "Tier5"
            result["reason"] = "spec 标记为需要复杂能力/大概率不可行"
        else:
            result["tier"] = "Tier3"
            result["reason"] = "spec 未明确分类（可能可行，需探索）"
    else:
        result["tier"] = "Tier4"
        result["reason"] = "无 spec 文件（需要先分析）"

    # 读数据
    if data_path.exists():
        try:
            with open(data_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return result

        trains = data.get("train", [])
        tests = data.get("test", [])
        arcgens = data.get("arc-gen", [])

        result["train_count"] = len(trains)
        result["test_count"] = len(tests)
        result["arcgen_count"] = len(arcgens)

        all_ex = trains + tests
        if all_ex:
            result["same_size"] = all(
                len(e["input"]) == len(e["output"])
                and len(e["input"][0]) == len(e["output"][0])
                for e in all_ex
            )

            # 收集颜色
            in_colors = set()
            out_colors = set()
            for e in all_ex:
                for row in e["input"]:
                    in_colors.update(row)
                for row in e["output"]:
                    out_colors.update(row)
            result["colors_in"] = sorted(in_colors)
            result["colors_out"] = sorted(out_colors)

        # 基于数据的二次修正
        if result["tier"] in ("Tier3", "Tier4") and result.get("same_size") is True:
            if result.get("colors_in") == result.get("colors_out"):
                result["tier"] = "Tier1"
                result["reason"] = "同尺寸 + 颜色集一致 → 可能是纯颜色映射（1x1 Conv 可解）"
            else:
                result["tier"] = "Tier2"
                result["reason"] = "同尺寸 → 大概率可用 3x3 Conv 解"

        if result.get("same_size") is False and result["tier"] != "Tier5":
            result["tier"] = "Tier5"
            result["reason"] = "输入/输出尺寸不同 → 高概率 infeasible（需要动态 crop/expand）"

    return result


def scan(start: int = 1, end: int = 400) -> list[dict]:
    """扫描任务范围，返回排序后的结果列表"""
    results = []
    for tid in range(start, end + 1):
        r = classify_task(tid)
        results.append(r)
    results.sort(key=lambda r: (r.get("tier", "Z"), r["tid"]))
    return results


def print_summary(results: list[dict]):
    """打印摘要"""
    tier_counts = {}
    for r in results:
        t = r["tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1

    print("=" * 60)
    print("NeuroGolf 任务扫描报告")
    print("=" * 60)
    print()
    print("优先级 | 数量 | 说明")
    print("-------|------|------")
    tier_desc = {
        "Tier1": "Gather/Transpose/Slice-Pad/单Conv（最简单）",
        "Tier2": "Gather空间/Slice多步（较简单）",
        "Tier3": "可能可行（需探索）",
        "Tier4": "不确定（无 spec，需分析）",
        "Tier5": "Conv逻辑/Reduce+Where/自定义多节点（复杂但可行）",
        "unknown": "无法分类",
    }
    for t in ["Tier1", "Tier2", "Tier3", "Tier4", "Tier5", "unknown"]:
        cnt = tier_counts.get(t, 0)
        bar = "█" * (cnt // 5)
        print(f"  {t:<6} | {cnt:>4} | {bar} {tier_desc.get(t, '')}")

    print()
    return tier_counts


def print_top(results: list[dict], n: int = 10):
    """打印前 N 个优先任务"""
    print(f"\n前 {n} 个优先任务:")
    print("-" * 60)
    print(f"{'任务':<10} {'Tier':<7} {'Train':<7} {'Test':<7} {'Arc-GEN':<8} {'同尺寸':<7} 原因")
    print("-" * 60)
    count = 0
    for r in results:
        if r["tier"] in ("Tier5", "unknown"):
            continue
        t = r["tier"]
        same = "Y" if r.get("same_size") is True else ("N" if r.get("same_size") is False else "?")
        print(
            f"task{r['tid']:03d}  {t:<7} {r['train_count']:<7} {r['test_count']:<7} {r['arcgen_count']:<8} {same:<7} {r['reason']}"
        )
        count += 1
        if count >= n:
            break


def export_csv(results: list[dict], path: str):
    """导出 CSV"""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "tid", "tier", "reason", "train_count", "test_count",
                "arcgen_count", "same_size", "colors_in", "colors_out",
                "has_spec", "has_data",
            ],
        )
        writer.writeheader()
        for r in results:
            row = {k: r.get(k, "") for k in writer.fieldnames}
            writer.writerow(row)
    print(f"\n导出完成: {path}")


def main():
    parser = argparse.ArgumentParser(description="NeuroGolf 任务批量扫描器")
    parser.add_argument("--start", type=int, default=1, help="起始任务编号 (default: 1)")
    parser.add_argument("--end", type=int, default=400, help="结束任务编号 (default: 400)")
    parser.add_argument("--top", type=int, default=20, help="显示前 N 个优先任务 (default: 20)")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4, 5],
                        help="只显示指定 Tier 的任务")
    parser.add_argument("--export", type=str, help="导出 CSV 文件路径")
    args = parser.parse_args()

    print(f"扫描任务 task{args.start:03d} ~ task{args.end:03d} ...")
    results = scan(args.start, args.end)

    print_summary(results)

    if args.tier:
        tier_name = f"Tier{args.tier}"
        results = [r for r in results if r["tier"] == tier_name]
        print(f"\n=== {tier_name} 任务列表 ({len(results)} 个) ===")
        for r in results[:50]:
            print(f"  task{r['tid']:03d} — {r['reason']}")
        if len(results) > 50:
            print(f"  ... 还有 {len(results) - 50} 个")
    else:
        print_top(results, args.top)

    if args.export:
        export_csv(results, args.export)


if __name__ == "__main__":
    main()
