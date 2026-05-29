"""Task 048 — ANALYSIS STUB.

From spec: Count compare — output [[8]] if count(8) > count(2), else [[0]].
Input: variable small grid (5x5-8x8) with colors 0, 2, 8.
Output: 1x1.

ATTEMPT: ReduceSum + Sub + Clip(Relu) comparison.
RESULT: 161/267 pass (some correct). However careful analysis reveals:
- train[3]: count8=13, count2=8, expected [[0]] (not [[8]] as count rule predicts)
- train[5]: count8=11, count2=8, expected [[0]] (not [[8]] as count rule predicts)
The simple count comparison rule is INCORRECT for some examples.

POSSIBLE EXPLANATIONS:
1. Rule involves connected component count, not pixel count
2. Rule involves bounding box area or other spatial property
3. The output for some cases has a specific override not captured by simple counting

The actual transformation rule is not simple count comparison.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 048: count-comparison approach fails on train[3] and train[5] "
        "where count8 > count2 but expected output is [[0]]. "
        "The true rule is not simple count comparison."
    )


if __name__ == '__main__':
    task_num = 48
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
