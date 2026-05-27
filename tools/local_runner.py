"""本地开发运行器 — 替代 Kaggle Notebook 的交互式环境"""
import sys
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / 'tools'))

import neurogolf_utils as nu


def solve_and_verify(task_num: int):
    """对单个任务：构建网络 → 验证 → 若通过则输出到 onnx_export/"""
    examples = nu.load_examples(task_num)

    # TODO: 分析变换规律，手写权重函数
    # 这里先用 identity 占位
    def weight_fn(channel_out, channel_in, kernel_coord):
        if kernel_coord == (0, 0) and channel_in == channel_out:
            return 1.0
        return 0.0

    network = nu.single_layer_conv2d_network(weight_fn, kernel_size=1)
    nu.verify_network(network, task_num, examples)


def batch_run(start=1, end=10):
    """批量处理多个任务"""
    for tid in range(start, end + 1):
        print(f"\n{'='*60}")
        print(f"Processing task {tid:03d}")
        print(f"{'='*60}")
        try:
            solve_and_verify(tid)
        except Exception as e:
            print(f"Task {tid:03d} failed: {e}")


def main():
    parser = argparse.ArgumentParser(description='NeuroGolf Local Runner')
    parser.add_argument('--task', type=int, help='单个任务编号')
    parser.add_argument('--batch', nargs=2, type=int, metavar=('START', 'END'),
                        help='批量处理范围')
    args = parser.parse_args()

    if args.task:
        solve_and_verify(args.task)
    elif args.batch:
        batch_run(args.batch[0], args.batch[1])
    else:
        print("用法示例:")
        print("  python tools/local_runner.py --task 1")
        print("  python tools/local_runner.py --batch 1 10")


if __name__ == '__main__':
    main()
