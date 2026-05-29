"""Task 062 — Symmetry completion: fill background with color 3, mirror
sparse shape to form symmetric closed pattern, merge secondary into primary.

Stub: Infeasible with simple Conv. Requires: (1) identify primary and
secondary colors (frequency analysis), (2) detect shape boundaries and
symmetry axes, (3) mirror the shape across the axis, (4) fill background.
All steps require object-level reasoning and non-local operations.
The symmetry axis and mirror pattern vary per example, making fixed
Conv weights insufficient.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 62
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
