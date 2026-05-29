"""Task 028 — ANALYSIS STUB.

From spec: Two colored pixels (C1 at (r1,c1), C2 at (r2,c2) with r1<r2)
define a three-region layout in 10x10 output:
- Region 1 (rows 0..r1): C1 draws a frame (top row = C1, sides = C1, row r1 = C1)
- Region 2 (rows r1+1..r2-1): C2 draws vertical side bars
- Region 3 (rows r2..H-1): C2 draws filled rows + side bars

Example: C1=6 at (2,2), C2=7 at (7,7). Output rows 0-2 have 6-frame,
rows 3-6 have 7 side bars, rows 7-9 have 7 full rows.

NOT CONV-AMENABLE: Requires global detection of two pixel positions,
which define region boundaries. No local kernel can compute this.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 028 requires detecting two pixel positions and drawing "
        "region-specific patterns — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 28
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
