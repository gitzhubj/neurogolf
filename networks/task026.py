"""Task 026 — ANALYSIS STUB.

From spec: Concavity detection — place color 8 where a 0-cell has >= 3 blue (1)
neighbors in its 8-neighborhood. Output is 5x3 crop at top-left.

EARLIER ATTEMPT: 3x3 Conv counting blue neighbors + ReLU + Clip + Mask.
FAILED: 0/267 pass. The actual transformation may involve:
- Different color channels (color 9 = pink may be the "shape" color, not color 1)
- Output 5x3 matches a fixed region, not a dynamic crop
- Rule may be more complex than simple neighbor counting

RECOMMENDED: Analyze the exact mapping by examining all train/test/arc-gen examples.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 026 transformation not yet implemented. "
        "The 3x3 neighbor-count approach failed 0/267. "
        "Need to analyze exact mapping between input 9/1-cells and output 8-cells."
    )


if __name__ == '__main__':
    task_num = 26
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    print("Stub — network not yet implemented.")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
