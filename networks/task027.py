"""Task 027 — ANALYSIS STUB.

From spec: Complex shape generation. Two non-zero color pixels define three regions:
1. Top (rows 0..r1): Draw C1 frame (filled top row, side columns, filled C1 row)
2. Middle (rows r1+1..r2-1): Draw C2 vertical side bars
3. Bottom (rows r2..H-1): Draw C2 filled rows + side bars

Actual data shows 10x10 grids with blue(1) shapes, output adds red(2) pixels
forming a bottom border/frame around the shape.

NOT CONV-AMENABLE: Requires detecting shape boundaries and region splitting,
which are global operations. Single pixel positions don't exist in actual data.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 027 requires shape detection and region-based pattern generation, "
        "not achievable with simple Conv networks."
    )


if __name__ == '__main__':
    task_num = 27
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
