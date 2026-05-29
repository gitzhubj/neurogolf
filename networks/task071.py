"""Task 071 — Remove one of two adjacent coloured objects; boundary pixels
become the other object's colour, rest become background.

Stub: Infeasible with simple Conv. Requires: (1) identify which of two
colours should be removed (based on object morphology relationship),
(2) detect boundary pixels (4-adjacent to the kept colour),
(3) conditionally recolor. Step (1) needs global object analysis.
Steps (2)-(3) are local but the decision (which colour to remove) varies
per example, so fixed Conv weights cannot encode the rule uniformly.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 71
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
