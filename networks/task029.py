"""Task 029 — ANALYSIS STUB.

From spec: Similar to Task 027 — two pixel positions define three regions.
Output is cropped (e.g., 23x21 input → 6x8 output).
Uses different color combinations than Task 027.

NOT CONV-AMENABLE: Same shape-generation logic as Task 027 plus cropping.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 029: same two-pixel region-splitting logic as 027 plus cropping. "
        "Not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 29
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
