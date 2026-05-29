"""Task 035 — ANALYSIS STUB.

From spec: Color projection. 10x10 grid. An 8-colored rectangle sits in
the middle. "Probe" pixels outside the rectangle project their color onto
the rectangle's boundary along the row or column direction.

Example: probe 9 above rectangle → rectangle top boundary becomes 9.
Probe 6 to the left → left boundary becomes 6.

NOT CONV-AMENABLE: Requires rectangle boundary detection, probe position
analysis, and row/column projection logic. Multiple global operations.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 035: color projection requires rectangle detection and "
        "probe-to-boundary mapping — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 35
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
