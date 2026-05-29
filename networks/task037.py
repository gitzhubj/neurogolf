"""Task 037 — ANALYSIS STUB.

From spec: Diagonal sliding. 10x10 grid. Each non-zero pixel slides along
the SW diagonal (dr=+1, dc=-1) until it hits the grid boundary or another
non-zero pixel. Different colors can cross each other.

Example: (0,2)=2 slides to (2,0). (0,5)=6 slides to (5,0).

NOT CONV-AMENABLE: Each pixel's slide distance depends on obstacles
along the diagonal path. Requires iterative or recursive logic.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 037: diagonal sliding is path-dependent per pixel, "
        "requires iterative collision detection — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 37
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
