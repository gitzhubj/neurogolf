"""Task 034 — ANALYSIS STUB.

From spec: Diagonal propagation from a 2x2 block. 9x9 grid. A 2x2 block
contains color 2 (anchor) and another color C. From the 2x2 block,
propagate color C along the diagonal direction (determined by C's position
in the 2x2 block) creating a 3-wide diagonal band.

Example: 2x2 block [[4,2],[4,4]] → color 4 propagates NE in a 3-wide band.

ATTEMPTED APPROACH: Multi-layer 3x3 Conv with diagonal kernel offsets.
FAILED: The propagation requires global pattern recognition — which
diagonal direction depends on C's position in the 2x2 block. 3x3 Conv
can propagate one step at a time but cannot recognize direction from
pattern.

NOT CONV-AMENABLE: Requires detecting the 2x2 pattern to determine
propagation direction, then conditional line drawing.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 034: diagonal propagation requires 2x2 pattern detection "
        "and conditional band drawing — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 34
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
