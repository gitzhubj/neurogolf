"""Task 047 — ANALYSIS STUB.

From spec: L-shape line drawing from two pixels. 9x9 grid.
From pixel 8 (cyan): draw line up to row 0, then right to meet pixel 7's column.
From pixel 7 (orange): draw line left to meet pixel 8's column, then down to bottom
Intersection at (r8, c7) = color 2.

Pattern:
- 8: up line in col c8 (rows 0..r8), right line in row r8 (cols c8..c7)
- 7: left line in row r7 (cols c7..c8 going left), down line in col c7 (rows r7..8)
- Intersection of 8's right line and 7's left line at (r8, c7) = 2

NOT CONV-AMENABLE: Requires detecting exact positions of pixels 8 and 7,
then drawing axis-aligned lines from each. Line drawing requires knowing
pixel coordinates globally, not achievable with local kernels.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 047: L-shape line drawing requires pixel detection and "
        "coordinate-based line drawing — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 47
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
