"""Task 032 — ANALYSIS STUB.

From spec: Per-column gravity. For each column independently, collect all
non-zero pixels preserving top-to-bottom order, then stack them at the
bottom of the column. Same input/output size. Example: 4x4 input → 4x4 output.

NOT CONV-AMENABLE: Requires per-column counting and reordering of pixels.
No convolutional kernel can perform dynamic column-level sorting.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 032: per-column gravity requires column-level sorting of "
        "non-zero pixels — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 32
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
