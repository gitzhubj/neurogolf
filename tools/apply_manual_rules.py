"""Apply manually analyzed transformation rules to Tier 1/2 specs."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = REPO_ROOT / "problem_specs"

# Manually deduced rules for each task
RULES = {
    # === GATHER_LOOKUP: Color replacement ===
    16: """- 核心变换：逐像素颜色映射（同尺寸，4对颜色互换）。
- 颜色互换对：1<->5, 2<->6, 3<->4, 8<->9。
- 完整映射表：`{1:5, 2:6, 3:4, 4:3, 5:1, 6:2, 8:9, 9:8}`。
- 未出现的颜色(0,7)保持恒等映射。
- 使用 Gather(axis=1, indices=[0,5,6,4,3,1,2,7,9,8])，仅 10 参数。""",

    276: """- 核心变换：单颜色替换。所有颜色 6 替换为 2，其余颜色不变。
- 颜色映射：6 -> 2。
- 完整映射表：`{6: 2}`，其余颜色保持恒等。
- 使用 Gather(axis=1, indices=[0,1,2,3,4,5,2,7,8,9])，10 参数。""",

    309: """- 核心变换：单颜色替换。所有颜色 7 替换为 5，其余颜色不变。
- 颜色映射：7 -> 5。
- 完整映射表：`{7: 5}`，其余颜色保持恒等。
- 本质是 Gather 查表，仅 10 参数。""",

    337: """- 核心变换：颜色对调。颜色 5 和 8 互换，其余颜色不变。
- 颜色互换对：5<->8。
- 完整映射表：`{5: 8, 8: 5}`。
- 使用 Gather(axis=1, indices=[0,1,2,3,4,8,6,7,5,9])，10 参数。""",

    # === GATHER_SPATIAL: Row/column permutation ===
    53: """- 核心变换：整体下移一行。第一行清空为背景(0)，原行0→行1，原行1→行2，原行2移出。
- 输入 3x3 网格，输出 3x3 网格。
- 行映射：output[0]=background(0), output[1]=input[0], output[2]=input[1]。
- 使用 Gather(axis=2) 行索引重排。""",

    116: """- 核心变换：垂直镜像扩展。输入 3 行 → 输出 6 行。
- 输出前 3 行 = 输入行的逆序（行2,行1,行0），输出后 3 行 = 输入行的正序（行0,行1,行2）。
- 即: output = reverse(input_rows) + input_rows。
- 使用 Gather(axis=2) 行索引重排：[2,1,0, 0,1,2, ...]。""",

    164: """- 核心变换：水平镜像扩展。输入 3 列 → 输出 6 列。
- 每行：output[row] = input[row] + reverse(input[row])。
- 即每行右侧拼接其自身的镜像。
- 使用 Gather(axis=3) 列索引重排。""",

    172: """- 核心变换：垂直镜像扩展（与 task210 相同）。输入 3 行 → 输出 6 行。
- output = input_rows + reverse(input_rows)。
- 前 3 行 = 输入原始行序，后 3 行 = 输入行逆序。
- 使用 Gather(axis=2) 行索引重排。""",

    210: """- 核心变换：垂直镜像扩展。输入 3 行 → 输出 6 行。
- output = input_rows + reverse(input_rows)。
- 与 task172 同模式。
- 使用 Gather(axis=2) 行索引重排。""",

    311: """- 核心变换：水平镜像扩展。输入 3 列 → 输出 6 列。
- 每行：output[row] = input[row] + reverse(input[row])。
- 与 task164 同模式。
- 使用 Gather(axis=3) 列索引重排。""",

    385: """- 核心变换：上半部填充为下半部的垂直镜像。10 行输入 → 10 行输出。
- 下半部(rows 5-9) 保持不变。上半部(rows 0-4) = 下半部(rows 5-9)的逆序。
- 即：output[0:5] = reverse(input[5:10]), output[5:10] = input[5:10]。
- 使用 Gather(axis=2) 行索引重排实现。""",

    # === SLICE_PAD: Spatial crop/flip ===
    87: """- 核心变换：180° 旋转（等效于水平翻转 + 垂直翻转）。
- output[r][c] = input[H-1-r][W-1-c]。
- 使用 Slice(step=[-1,-1]) 双轴反向 + Pad 恢复到 30x30。
- 仅需 5 个参数（starts, ends, output_pads）。""",

    135: """- 核心变换：从 9x9 输入中裁出右下角 3x3 子区域。
- 裁剪位置: rows 0-2, cols 6-8（输入右上角 3x3）。
- Slice(starts=[0,6], ends=[3,9]) + Pad(27 rows, 27 cols)。
- 仅需 6 个参数。""",

    140: """- 核心变换：180° 旋转（与 task087 相同）。
- output[r][c] = input[H-1-r][W-1-c]。
- 使用 Slice(step=[-1,-1]) 双轴反向 + Pad 恢复。
- 仅需 5 个参数。""",

    326: """- 核心变换：裁剪为左上角 2x2 子区域。
- 从任意尺寸输入中取 rows 0-1, cols 0-1。
- Slice(starts=[0,0], ends=[2,2]) + Pad(28 rows, 28 cols)。
- 仅需 6 个参数。""",

    # === TRANSPOSE: H<->W swap ===
    179: """- 核心变换：矩阵转置（H↔W 维度交换）。
- output[r][c] = input[c][r]。
- 所有样例为 3x3 方形网格，转置后仍为 3x3。
- 使用 Transpose(perm=[0,1,3,2])，0 参数！""",

    241: """- 核心变换：矩阵转置（H↔W 维度交换）。支持非方形网格。
- output[r][c] = input[c][r]。
- 样例包含 3x3 和 4x4 等多种尺寸，转置后尺寸互换。
- 使用 Transpose(perm=[0,1,3,2])，0 参数。""",

    # === SINGLE_CONV: Mostly untangled above ===
    113: """- 核心变换：空间行/列重排（具体规则较复杂）。
- 输入可能包含多种尺寸，输出尺寸可变。
- baseline 使用 Gather(axis=2/3) 实现行/列索引重排。
- 需进一步分析 baseline Gather 的 indices 值来确定精确规则。""",
}


def update_spec_section(tid: int, rule_text: str):
    """Update Section 1 of the spec with the deduced rule"""
    spec_path = SPEC_DIR / f"task{tid:03d}_spec.md"
    if not spec_path.exists():
        return False

    spec = spec_path.read_text(encoding="utf-8")
    start = spec.find("## 1. 核心规则")
    end = spec.find("## 2. 关键证据")

    if start == -1 or end == -1:
        return False

    # Build new section 1
    new_section = "## 1. 核心规则\n\n" + rule_text + "\n"

    new_spec = spec[:start] + new_section + "\n" + spec[end:]
    spec_path.write_text(new_spec, encoding="utf-8")
    return True


def main():
    updated = 0
    for tid, rule in sorted(RULES.items()):
        if update_spec_section(tid, rule):
            print(f"task{tid:03d}: updated")
            updated += 1
    print(f"\nUpdated {updated}/{len(RULES)} tasks")


if __name__ == "__main__":
    main()
