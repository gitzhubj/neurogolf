"""Task 036 — ANALYSIS STUB.

From spec: Connected component extraction. 30x30 input contains scattered
noise pixels (isolated single pixels) and one color that forms a connected
component. Extract the connected component's bounding box as output.

NOT CONV-AMENABLE: Requires per-color connectivity analysis (8-neighborhood),
distinguishing noise from signal, computing bounding box, and cropping.
All are global operations beyond Conv capabilities.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 036: connected component extraction requires connectivity "
        "analysis and dynamic cropping — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 36
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
