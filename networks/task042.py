"""Task 042 — ANALYSIS STUB.

From spec: Object reflection. 10x10 grid. For each 3-colored connected
component, an 8-colored component is added at the 180-degree rotated
position about the component's center.

Example: Two diagonal 3-pixels at (3,3)/(4,4) and (6,7)/(7,6).
Output adds 8-pixels at (2,4)/(5,5) and (5,1)/(8,8).

NOT CONV-AMENABLE: Requires connected component analysis, center
computation, and shape copy at rotated position. All global operations.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 042: object reflection requires component analysis and "
        "rotation — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 42
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
