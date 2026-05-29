"""Task 040 — ANALYSIS STUB.

From spec: Nearest boundary fill. 10x10 grid. Color 3 cells are replaced
by the color of the nearest boundary marker (from edge rows/columns).
Boundary markers are non-zero, non-3 colors at grid edges.

Example: Left column=1, right column=2, internal 3s → nearest side's color.

NOT CONV-AMENABLE: Requires distance computation from each 3-cell to each
boundary marker, selecting the minimum. This is a global Voronoi-like
operation over the entire grid.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 040: nearest boundary fill requires global distance "
        "computation — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 40
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
