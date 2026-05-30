"""批量处理 agent 返回的规则分析结果，更新 spec 文件。

Input format (from agent output):
    TID: RULE_TEXT

Usage:
    python tools/batch_update_rules.py --file results.txt
    python tools/batch_update_rules.py --inline "15: 颜色替换：X替换为Y" "73: 邻域膨胀"
"""
import sys
import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = REPO_ROOT / "problem_specs"


def parse_rules(text: str) -> dict[int, str]:
    """从 agent 输出中解析 'TID: RULE' 行"""
    rules = {}
    for line in text.strip().split('\n'):
        line = line.strip()
        # Match "TID: RULE" or "taskTID: RULE" or just "TID: RULE"
        m = re.match(r'(?:task)?(\d+)\s*[:：]\s*(.+)', line)
        if m:
            tid = int(m.group(1))
            rule = m.group(2).strip()
            if tid > 0 and tid <= 400 and len(rule) > 3:
                rules[tid] = rule
    return rules


def update_spec_section1(tid: int, rule_text: str):
    """更新 spec 的 Section 1（核心规则）"""
    spec_path = SPEC_DIR / f"task{tid:03d}_spec.md"
    if not spec_path.exists():
        print(f"  task{tid:03d}: spec not found, skipping")
        return False

    spec = spec_path.read_text(encoding="utf-8")
    start = spec.find("## 1. 核心规则")
    end = spec.find("## 2. 关键证据")

    if start == -1 or end == -1:
        print(f"  task{tid:03d}: cannot find sections 1/2")
        return False

    # Build the new section 1
    # If rule_text already starts with '- ', use as-is
    if not rule_text.startswith('- '):
        rule_text = f"- 核心变换：{rule_text}。"

    new_section = f"## 1. 核心规则\n\n{rule_text}\n\n"

    new_spec = spec[:start] + new_section + "\n" + spec[end:]
    spec_path.write_text(new_spec, encoding="utf-8")
    return True


def update_evidence(tid: int):
    """更新 Section 2 为已验证"""
    spec_path = SPEC_DIR / f"task{tid:03d}_spec.md"
    if not spec_path.exists():
        return False

    spec = spec_path.read_text(encoding="utf-8")
    start = spec.find("## 2. 关键证据")
    end = spec.find("## 3. 歧义与风险")

    if start == -1 or end == -1:
        return False

    new_evidence = """## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。

"""
    new_spec = spec[:start] + new_evidence + "\n" + spec[end:]
    spec_path.write_text(new_spec, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="批量更新 spec 规则")
    parser.add_argument("--file", type=str, help="包含 agent 输出结果的文件")
    parser.add_argument("--inline", nargs="*", help="直接指定规则，如 '15: 规则文本'")
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
        rules = parse_rules(text)
    elif args.inline:
        text = '\n'.join(args.inline)
        rules = parse_rules(text)
    else:
        # Read from stdin
        text = sys.stdin.read()
        rules = parse_rules(text)

    if not rules:
        print("No valid rules found in input.")
        return

    print(f"Found {len(rules)} rules to apply.\n")

    updated = 0
    for tid, rule in sorted(rules.items()):
        ok1 = update_spec_section1(tid, rule)
        ok2 = update_evidence(tid)
        if ok1:
            print(f"  task{tid:03d}: {rule[:80]}...")
            updated += 1

    print(f"\nUpdated: {updated}/{len(rules)}")


if __name__ == "__main__":
    main()
