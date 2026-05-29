"""Task 046 — ANALYSIS STUB.

From spec: 3-row redistribution. Input always has 3 rows, width varies.
Color 5 marks "channels" for redistribution. Middle row (row 1) has color
blocks separated by 5s. Top (row 0) and bottom (row 2) have 5-markers
that pull blocks from row 1. Blocks may be resized or split.

Example: 3x9 input → 3x7 output. 5-markers control which blocks go where.

NOT CONV-AMENABLE: Requires parsing 5-marker topology, identifying blocks,
and redistributing them based on marker positions. Output size varies.
Complex object-level transformation with unclear exact rules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 046: 3-row redistribution requires marker parsing and "
        "block redistribution — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 46
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
