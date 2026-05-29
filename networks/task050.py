"""Task 050 — ANALYSIS STUB.

From spec: Fill between paired 8s per row and column. Variable size grid.
For each row with 2+ 8-pixels: fill between leftmost and rightmost 8 with 3.
For each column with 2+ 8-pixels: fill between topmost and bottommost 8 with 3.
Original 8s preserved.

Example: Row has 8 at col 3 and col 9 → fill cols 4-8 with 3.
Column has 8 at row 2 and row 7 → fill rows 3-6 with 3.

ATTEMPTED APPROACH: 1x30 Conv kernel to detect 8-pair extents per row.
FAILED: Per-row min/max computation of 8 positions and subsequent fill
require global reductions per row dimension. The fill pattern (all cells
between two endpoints) cannot be represented as a Conv kernel.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 050: fill between paired 8s requires per-row/per-col "
        "min/max of 8 positions — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 50
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
