"""基于 Kaggle 提交分数的迭代追踪系统

工作流:
1. 检测哪些 ONNX 文件变了（对比上次提交的 hash）
2. 打包提交到 Kaggle
3. 等待并获取最新分数
4. 对比上次分数，计算 delta
5. 自动写入对应任务的 thinking log

Usage:
    python tools/submit_tracker.py --check        # 检查哪些文件变了
    python tools/submit_tracker.py --submit       # 提交并追踪分数
    python tools/submit_tracker.py --history      # 查看提交历史
    python tools/submit_tracker.py --dry-run      # 预览但不提交
"""
import sys, os, json, time, hashlib, argparse, subprocess, re
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parents[1]
ONNX_DIR = REPO / "onnx_export"
HISTORY_FILE = REPO / "submission_history.json"
KAGGLE_COMP = "neurogolf-2026"


def setup_kaggle_auth():
    """确保 Kaggle 认证可用"""
    token = os.environ.get("KAGGLE_API_TOKEN", "")
    if token:
        kaggle_dir = Path.home() / ".kaggle"
        kaggle_dir.mkdir(parents=True, exist_ok=True)
        tok_file = kaggle_dir / "access_token"
        tok_file.write_text(token)
        tok_file.chmod(0o600)
    return token or Path.home().joinpath(".kaggle", "kaggle.json").exists()


def file_hash(path: Path) -> str:
    """计算文件 SHA256"""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def scan_onnx_files() -> dict[str, dict]:
    """扫描 onnx_export/ 中所有任务 ONNX 文件"""
    files = {}
    for p in sorted(ONNX_DIR.glob("task*.onnx")):
        if "debug" in p.name:
            continue
        tid = re.search(r"task(\d+)", p.name)
        if tid:
            files[tid.group(1)] = {
                "path": str(p),
                "hash": file_hash(p),
                "size": p.stat().st_size,
            }
    return files


def load_history() -> dict:
    """加载提交历史"""
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    return {"submissions": [], "task_scores": {}}


def save_history(history: dict):
    """保存提交历史"""
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def get_changed_tasks(current: dict, history: dict) -> list[str]:
    """对比当前文件和上次提交，找出变更的任务"""
    last_sub = history["submissions"][-1] if history["submissions"] else None
    if not last_sub or "hashes" not in last_sub:
        return list(current.keys())

    changed = []
    prev_hashes = last_sub["hashes"]
    for tid, info in current.items():
        if tid not in prev_hashes or prev_hashes[tid] != info["hash"]:
            changed.append(tid)
    return changed


def fetch_latest_score() -> dict | None:
    """从 Kaggle 获取最新提交的分数"""
    try:
        r = subprocess.run(
            ["kaggle", "competitions", "submissions", "-c", KAGGLE_COMP],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "KAGGLE_API_TOKEN": os.environ.get("KAGGLE_API_TOKEN", "")}
        )
        lines = r.stdout.strip().split("\n")
        if len(lines) < 2:
            return None

        # Parse the table: header + rows
        # fileName, date, description, status, publicScore, privateScore
        for line in lines[1:]:
            parts = line.split()
            if len(parts) < 4 or "COMPLETE" not in line:
                continue
            # Extract public score (last numeric field)
            nums = re.findall(r"([\d.]+)", line)
            if nums:
                score = float(nums[-1])
                return {
                    "date": parts[1] + " " + parts[2] if len(parts) > 2 else "",
                    "status": "COMPLETE",
                    "public_score": score,
                    "raw": line.strip(),
                }
    except Exception as e:
        print(f"  Error fetching score: {e}")
    return None


def submit_to_kaggle(changed_tasks: list[str], message: str = "") -> str | None:
    """打包 ONNX 文件并提交到 Kaggle"""
    import tempfile, shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Copy all ONNX files (not just changed — Kaggle needs full set)
        for p in ONNX_DIR.glob("task*.onnx"):
            if "debug" in p.name:
                continue
            shutil.copy2(p, tmp / p.name)

        # Create submission.zip
        zip_path = tmp / "submission.zip"
        shutil.make_archive(str(zip_path.with_suffix("")), "zip", tmp)

        if not message:
            tasks_str = ",".join(changed_tasks[:5])
            if len(changed_tasks) > 5:
                tasks_str += f",+{len(changed_tasks)-5}"
            message = f"opt: task{tasks_str}"

        print(f"  Submitting with message: {message}")
        print(f"  Changed tasks: {changed_tasks}")

        try:
            r = subprocess.run(
                ["kaggle", "competitions", "submit", "-c", KAGGLE_COMP,
                 "-f", str(zip_path.with_suffix(".zip")), "-m", message],
                capture_output=True, text=True, timeout=60,
                env={**os.environ, "KAGGLE_API_TOKEN": os.environ.get("KAGGLE_API_TOKEN", "")}
            )
            print(f"  {r.stdout.strip()}")
            if r.returncode != 0:
                print(f"  Error: {r.stderr}")
                return None
            return message
        except Exception as e:
            print(f"  Submit error: {e}")
            return None


def update_thinking_log(tid: str, delta: float, new_score: float, history: dict):
    """将分数变动写入任务思考日志"""
    log_path = REPO / "thinking" / f"task{tid}_thinking.md"

    # Get previous score for this task
    prev = history.get("task_scores", {}).get(tid, {})
    prev_score = prev.get("public_score", None)

    entry = f"""
## Score Tracking

| 日期 | Public Score | Delta | 备注 |
|---|---|---|---|
| {datetime.now().strftime('%Y-%m-%d %H:%M')} | {new_score} | {delta:+.2f} | Kaggle 提交 |
"""
    if prev_score:
        entry += f"| {prev.get('date', '?')} | {prev_score} | — | 上次提交 |\n"

    if log_path.exists():
        existing = log_path.read_text(encoding="utf-8")
        if "## Score Tracking" in existing:
            # Insert new row after header
            lines = existing.split("\n")
            new_lines = []
            in_score_section = False
            header_found = False
            for line in lines:
                new_lines.append(line)
                if "## Score Tracking" in line:
                    in_score_section = True
                elif in_score_section and "|---|---|" in line and not header_found:
                    header_found = True
                elif in_score_section and header_found and line.startswith("|") and line.strip():
                    # Insert new entry before first data row
                    new_lines.insert(len(new_lines) - 1,
                                     f"| {datetime.now().strftime('%Y-%m-%d %H:%M')} | {new_score} | {delta:+.2f} | Kaggle 提交 |")
                    if prev_score:
                        new_lines.insert(len(new_lines) - 1,
                                         f"| {prev.get('date', '?')} | {prev_score} | — | 上次提交 |")
                    in_score_section = False
            existing = "\n".join(new_lines)
        else:
            existing += entry
    else:
        existing = f"# Task {tid} 思考日志\n\n{entry}"

    log_path.write_text(existing, encoding="utf-8")


def check_command():
    """检查变更"""
    current = scan_onnx_files()
    history = load_history()
    changed = get_changed_tasks(current, history)

    print(f"ONNX 文件总数: {len(current)}")
    print(f"变更任务数: {len(changed)}")
    if changed:
        print(f"变更任务: {changed}")
        for tid in changed[:10]:
            info = current[tid]
            print(f"  task{tid}: hash={info['hash']} size={info['size']}")


def submit_command(dry_run: bool = False):
    """提交并追踪"""
    if not setup_kaggle_auth():
        print("ERROR: Kaggle 未认证。设置 KAGGLE_API_TOKEN 环境变量。")
        return

    current = scan_onnx_files()
    history = load_history()
    changed = get_changed_tasks(current, history)

    if not changed:
        print("没有文件变更，跳过提交。")
        return

    print(f"检测到 {len(changed)} 个任务变更")

    if dry_run:
        print(f"[DRY RUN] 将提交: {changed[:10]}{'...' if len(changed)>10 else ''}")
        return

    # 获取提交前分数
    prev_score_info = fetch_latest_score()
    prev_score = prev_score_info["public_score"] if prev_score_info else None
    print(f"提交前分数: {prev_score}")

    # 提交
    msg = submit_to_kaggle(changed)
    if not msg:
        print("提交失败")
        return

    # 等待分数出来
    print("等待评分完成...")
    for i in range(12):  # 最多等 2 分钟
        time.sleep(10)
        new_score_info = fetch_latest_score()
        if new_score_info and new_score_info["public_score"] != prev_score:
            break
        print(f"  .", end="", flush=True)
    print()

    new_score_info = fetch_latest_score()
    new_score = new_score_info["public_score"] if new_score_info else 0
    delta = new_score - prev_score if prev_score else 0

    print(f"提交后分数: {new_score} (delta: {delta:+.2f})")

    # 记录到历史
    history["submissions"].append({
        "date": datetime.now(timezone.utc).isoformat(),
        "message": msg,
        "changed_tasks": changed,
        "hashes": {tid: current[tid]["hash"] for tid in current},
        "public_score": new_score,
        "delta": delta,
    })

    # 更新每个任务的分数（按比例分配 delta——粗略估计）
    if delta != 0 and len(changed) > 0:
        per_task_delta = delta / len(changed)
        for tid in changed:
            history["task_scores"][tid] = {
                "date": datetime.now(timezone.utc).isoformat(),
                "public_score": history["task_scores"].get(tid, {}).get("public_score", 0) + per_task_delta,
            }
            update_thinking_log(tid, per_task_delta,
                               history["task_scores"][tid]["public_score"], history)

    save_history(history)
    print("历史已更新，思考日志已写入。")


def fetch_command():
    """拉取 Kaggle 最新分数"""
    if not setup_kaggle_auth():
        print("ERROR: Kaggle 未认证。")
        return

    history = load_history()
    prev_score = history["submissions"][-1]["public_score"] if history["submissions"] else None

    print("正在拉取 Kaggle 最新分数...")
    score_info = fetch_latest_score()
    if not score_info:
        print("无法获取分数。")
        return

    current_score = score_info["public_score"]
    delta = current_score - prev_score if prev_score else 0

    print(f"上次分数: {prev_score}")
    print(f"当前分数: {current_score}")
    print(f"Delta: {delta:+.2f}")

    if delta != 0 and history["submissions"]:
        last_sub = history["submissions"][-1]
        changed = last_sub.get("changed_tasks", [])
        print(f"变更任务: {changed}")
        # Update history
        last_sub["public_score"] = current_score
        last_sub["delta"] = delta
        save_history(history)
        print("历史已更新。")


def history_command():
    """查看提交历史"""
    history = load_history()
    subs = history.get("submissions", [])
    if not subs:
        print("暂无提交记录。")
        return

    print(f"{'日期':<22} {'Score':<8} {'Delta':<8} {'任务数':<8} 信息")
    print("-" * 70)
    for s in subs:
        date = s.get("date", "?")[:19]
        score = s.get("public_score", "?")
        delta = s.get("delta", 0)
        n_tasks = len(s.get("changed_tasks", []))
        msg = s.get("message", "")[:40]
        print(f"{date:<22} {score:<8} {delta:+.2f}     {n_tasks:<8} {msg}")

    # 每个任务的最新分数
    task_scores = history.get("task_scores", {})
    if task_scores:
        print(f"\n各任务最新分数 ({len(task_scores)} 个):")
        for tid in sorted(task_scores, key=lambda t: -task_scores[t].get("public_score", 0))[:15]:
            ts = task_scores[tid]
            print(f"  task{tid}: {ts.get('public_score', '?')}")


def main():
    parser = argparse.ArgumentParser(description="Kaggle 分数驱动的迭代追踪")
    parser.add_argument("--check", action="store_true", help="检查文件变更")
    parser.add_argument("--submit", action="store_true", help="提交并追踪分数")
    parser.add_argument("--fetch", action="store_true", help="拉取 Kaggle 最新分数（CI 已提交）")
    parser.add_argument("--history", action="store_true", help="查看提交历史")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    args = parser.parse_args()

    if args.submit:
        submit_command(dry_run=args.dry_run)
    elif args.fetch:
        fetch_command()
    elif args.history:
        history_command()
    else:
        check_command()


if __name__ == "__main__":
    main()
