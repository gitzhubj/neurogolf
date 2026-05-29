"""Task 045 — ANALYSIS STUB.

From spec: Row fill if first and last columns match. 10x10 grid.
For each row: if input[r][0] == input[r][9] != 0, fill entire row
with that color. Otherwise keep original (only first/last columns).

Example: Row 5 first=4, last=4 → entire row 5 becomes 4.
Row 1 first=9, last=6 → row 1 unchanged (only cols 0 and 9 have values).

ATTEMPTED APPROACH: Use 3x3 Conv + broadcasting.
FAILED: The "first column == last column" check requires comparing
two distant pixels (cols 0 and 9) per row. Even with 30-wide Conv
kernels, the per-row comparison and subsequent row broadcasting
cannot be expressed as a convolutional filter.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 045: row-fill requires per-row comparison of two distant "
        "columns and row-level broadcasting — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 45
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
