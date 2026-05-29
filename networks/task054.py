"""Task 054 — Crosshair drawing from special-colored cells to boundary color.

Stub: Infeasible with simple Conv. Requires: (1) region/boundary detection,
(2) ray casting in 4 directions, (3) color priority at intersections.
All need global object-level processing beyond Conv opset 10 capability.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 54
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
