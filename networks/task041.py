"""Task 041 — ANALYSIS STUB.

From spec: Per-row, per-color fill between extremes. 10x10 grid.
For each row r and each color C present in that row:
  left = min(col where input[r][col] == C)
  right = max(col where input[r][col] == C)
  if left < right: output[r][left..right] = C

Example: Row 1 has 3 at cols 1 and 8 → output row 1 cols 1-8 all 3.

NOT CONV-AMENABLE: Requires per-row min/max computation for each color,
which is a global reduction per row dimension. No local kernel captures
information across the full row width.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 041: per-row per-color fill requires global row-level "
        "min/max — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 41
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
