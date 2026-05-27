"""批量处理所有任务的 runner"""
import sys
import json
import subprocess
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO_ROOT = Path(__file__).resolve().parents[1]


def process_task(task_json: Path) -> dict:
    """对单个任务运行完整流水线：分析→构建→验证→导出"""
    tid = task_json.stem.replace('task', '')
    # TODO: 调用网络构建和验证逻辑
    return {"task": tid, "status": "pending"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tasks', nargs='*', help='任务 ID 列表，不指定则处理全部')
    parser.add_argument('--parallel', type=int, default=4)
    args = parser.parse_args()

    data_dir = REPO_ROOT / 'data' / 'training'
    jsons = sorted(data_dir.glob('task*.json'))

    if args.tasks:
        jsons = [j for j in jsons if j.stem.replace('task', '') in args.tasks]

    print(f"Processing {len(jsons)} tasks...")

    results = []
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {pool.submit(process_task, j): j for j in jsons}
        for future in as_completed(futures):
            results.append(future.result())

    passed = sum(1 for r in results if r['status'] == 'ok')
    print(f"Done: {passed}/{len(results)} passed")


if __name__ == '__main__':
    main()
