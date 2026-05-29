"""Task 031 — ANALYSIS STUB.

From spec: Bounding box crop. Find min_row, max_row, min_col, max_col of
all non-zero pixels, then crop input to that bounding box. Colors unchanged.
Input sizes vary (10x12, 11x12, 12x12), output size = bounding box.

Example: 10x12 input with color-2 L-shape → 4x4 output exactly framing the shape.

NOT CONV-AMENABLE: Requires global argmin/argmax over non-zero positions
to determine dynamic crop bounds. Conv operates symmetrically on all
spatial positions and cannot compute bounding boxes.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 031: bounding box crop requires global min/max of non-zero "
        "positions — cannot be done with Conv."
    )


if __name__ == '__main__':
    task_num = 31
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
