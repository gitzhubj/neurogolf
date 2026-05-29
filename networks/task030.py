"""Task 030 — ANALYSIS STUB.

From spec: Gravity simulation. Colored connected blocks fall vertically
until they hit the bottom or another block. Blocks preserve shape and
horizontal position. Same input/output size.

Example: 5x10 input. Blocks (2,2), (1,1), (4,4) at various rows.
Output: all blocks fall down to bottom rows, preserving shape.

NOT CONV-AMENABLE: Requires connected component detection, object-level
physics simulation (gravity + collision), and vertical translation.
Each block's fall distance depends on the block below it.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 030: gravity simulation requires connected component analysis "
        "and object-level translation — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 30
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
