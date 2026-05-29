"""Task 039 — ANALYSIS STUB.

From spec: Extract center 3x3 of nested symmetric pattern. 10x10 input
has concentric color layers. Output is the 3x3 center region of the pattern.

Example: Multi-layer pattern → output 3x3 at pattern center.

NOT CONV-AMENABLE: Requires finding the pattern center coordinates,
which vary per example. Conv operates equally on all positions and
cannot selectively crop to a dynamic center region.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 039: center crop requires pattern symmetry analysis "
        "to find the center — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 39
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
