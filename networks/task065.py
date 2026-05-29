"""Task 065 — Detect full-row + full-column cross, extract quadrant
containing the unique contrasting pixel.

Stub: Infeasible with simple Conv. Requires: (1) scan rows/cols to
detect uniform-color cross line, (2) locate the unique anomaly pixel,
(3) determine which of 4 quadrants contains it, (4) crop that quadrant
as output. Steps (1)-(3) require global scans and position comparison.
Step (4) produces a variably-sized output, which cannot be expressed
with a fixed (1,10,30,30) output shape constraint.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 65
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
