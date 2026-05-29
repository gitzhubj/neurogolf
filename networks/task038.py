"""Task 038 — ANALYSIS STUB.

From spec: Superpixel adjacency counting. 9x9 grid divided into 3x3
superpixels. Each superpixel may contain a 2x2 block of color 1 or 2.
Output is 1x5 binary vector indicating which adjacency patterns exist
between superpixels.

NOT CONV-AMENABLE AND DIFFERENT SHAPE: Input 9x9 → Output 1x5.
Requires superpixel partitioning, color detection in each block,
and adjacency relationship counting.

EVEN WITH NETWORK: Output 1x5 must be placed at top-left of 30x30 canvas
in (1,10,30,30) format with channel encoding. Complex structure.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 038: superpixel adjacency counting requires partition "
        "analysis and relation counting — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 38
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
