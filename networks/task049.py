"""Task 049 — ANALYSIS STUB.

From spec: Extract innermost enclosed monochrome rectangle. Input has
nested single-color rectangular regions. Find the innermost (smallest)
rectangle that is fully enclosed by another, and output its content.

Example: 2-frame(5x7) → 8-block(3x3) → output 3x3 8-block.

NOT CONV-AMENABLE: Requires nested rectangle detection, enclosure
relationship analysis (tree), and innermost region cropping.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 049: innermost rectangle extraction requires nesting "
        "analysis and region selection — not Conv-amenable."
    )


if __name__ == '__main__':
    task_num = 49
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
