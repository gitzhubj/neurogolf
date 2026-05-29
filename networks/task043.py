"""Task 043 — ANALYSIS STUB.

From spec: Conditional pattern copy from row 0. 10x10 grid.
Row 0 contains a 5-pattern. If a row's last column is 5, copy row 0's
5-pattern to that row as color 2 instead of 5. The last column stays 5.

Example: Row 0 = [5,0,0,5,0,0,0,5,0,0], rows 3 and 7 have last col = 5
→ rows 3 and 7 get [2,0,0,2,0,0,0,2,0,5].

NOT CONV-AMENABLE: Requires reading row 0 from arbitrary row positions.
The trigger check (last column of current row) and the source pattern
(row 0) are at distant spatial positions not reachable together by a
small Conv kernel without many layers.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def build():
    raise NotImplementedError(
        "Task 043: conditional pattern copy from row 0 requires "
        "cross-row access beyond small-kernel range."
    )


if __name__ == '__main__':
    task_num = 43
    examples = nu.load_examples(task_num)
    print(f"Task {task_num}: {len(examples['train'])} train, {len(examples['test'])} test, "
          f"{len(examples.get('arc-gen', []))} arc-gen")
    try:
        network = build()
        nu.verify_network(network, task_num, examples)
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
