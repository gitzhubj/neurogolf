"""Task 033 — ANALYSIS STUB.

From spec: Reflection along divider lines. 17x17 grid divided into 9
cells (5x5 each) by L-colored lines at rows 5, 11 and cols 5, 11.
For each cell containing a shape of color S, reflect the shape to
the diagonally opposite cell using color L for the reflected copy.

NOT CONV-AMENABLE: Requires detecting cell boundaries, identifying
shape positions, and computing cell-to-cell reflection mappings.
This is a multi-step geometric transformation.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 033: cell-to-cell reflection requires partition detection "
        "and geometric reflection mapping — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 33
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
