"""Batch verify networks for tasks 1-200, collect scores, generate ONNX, write thinking logs.

Usage:
    python tools/batch_verify.py --start 1 --end 200
"""
import subprocess, sys, re, time, json
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]

def run_task(tid: int) -> dict:
    """Run a single task network, return results"""
    p = REPO_ROOT / f"networks/task{tid:03d}.py"
    if not p.exists():
        return {"tid": tid, "status": "MISSING"}

    try:
        compile(p.read_text(encoding="utf-8"), str(p), "exec")
    except SyntaxError:
        return {"tid": tid, "status": "COMPILE_ERR"}

    try:
        r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=120)
        out = r.stdout + r.stderr

        result = {"tid": tid, "status": "UNKNOWN", "output": out}

        if "IS READY" in out:
            result["status"] = "PASS"
            # Extract metrics
            m = re.search(r"(\d+) pass, (\d+) fail", out)
            if m:
                result["pass_count"] = int(m.group(1))
                result["fail_count"] = int(m.group(2))
            m = re.search(r"([\d.]+) points", out)
            if m:
                result["score"] = float(m.group(1))
            m = re.search(r"(\d+) bytes .* (\d+) params", out)
            if m:
                result["memory"] = int(m.group(1))
                result["params"] = int(m.group(2))
            # Extract pass lines
            for line in out.split("\n"):
                if "ARC-AGI" in line:
                    result["arc_agi"] = line.strip()
                elif "ARC-GEN" in line:
                    result["arc_gen"] = line.strip()

        elif "IS NOT READY" in out:
            result["status"] = "FAIL"
            for line in out.split("\n"):
                if "pass" in line and "fail" in line:
                    m = re.search(r"(\d+) pass, (\d+) fail", line)
                    if m:
                        result["pass_count"] = int(m.group(1))
                        result["fail_count"] = int(m.group(2))
                        break

        return result
    except subprocess.TimeoutExpired:
        return {"tid": tid, "status": "TIMEOUT"}
    except Exception as e:
        return {"tid": tid, "status": "ERROR", "error": str(e)[:100]}


def write_thinking_log(tid: int, result: dict):
    """Write a thinking log for a completed task"""
    log_path = REPO_ROOT / f"thinking/task{tid:03d}_thinking.md"
    spec_path = REPO_ROOT / f"problem_specs/task{tid:03d}_spec.md"

    rule = ""
    if spec_path.exists():
        spec = spec_path.read_text(encoding="utf-8")
        sec1 = spec.find("## 1. 核心规则")
        sec2 = spec.find("## 2. 关键证据")
        if sec1 != -1 and sec2 != -1:
            for line in spec[sec1:sec2].split("\n"):
                if line.strip().startswith("- ") and len(line) > 20:
                    rule = line.strip()[2:]
                    break

    arch = ""
    if spec_path.exists():
        for line in spec.split("\n"):
            if "recommended_architecture:" in line:
                arch = line.split("`")[1] if "`" in line else ""
                break

    status = "DONE"
    score = result.get("score", 0)
    if score >= 24:
        status = "DONE (optimal)"
        note = "已达理论最优，无需进一步优化。"
    elif score >= 21:
        status = "DONE (near-optimal)"
        note = "接近最优，优化空间很小。"
    elif score >= 19:
        status = "DONE"
        note = "可继续探索小幅优化。"
    else:
        status = "ACTIVE"
        note = "有优化空间，需进一步研究。"

    params = result.get("params", "?")
    memory = result.get("memory", "?")
    agi = result.get("arc_agi", "?")
    gen = result.get("arc_gen", "?")

    log = f"""# Task {tid:03d} 思考日志

## Round 1 — Baseline 验证

### 规则
{rule if rule else '见 problem_specs/'}

### 快照
- 架构: {arch}
- 参数量: {params}
- 内存: {memory} bytes
- Score: {score}
- {agi}
- {gen}

### 结论
{note}
"""
    log_path.write_text(log, encoding="utf-8")
    return status


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=200)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    results = defaultdict(list)
    total = 0

    for tid in range(args.start, args.end + 1):
        print(f"[{tid}/{args.end}] task{tid:03d}...", end=" ", flush=True)
        r = run_task(tid)
        total += 1
        results[r["status"]].append(tid)

        if r["status"] == "PASS":
            score = r.get("score", 0)
            print(f"PASS score={score:.3f}", end="")
            if not args.dry_run:
                status = write_thinking_log(tid, r)
                print(f" [{status}]")
            else:
                print()
        else:
            print(r["status"])

    print(f"\n=== Summary ({total} tasks) ===")
    for status, tasks in sorted(results.items()):
        print(f"  {status}: {len(tasks)} -> {tasks[:10]}{'...' if len(tasks)>10 else ''}")


if __name__ == "__main__":
    main()
