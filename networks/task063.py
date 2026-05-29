"""Task 063 — Flood-fill: fill 0-cells enclosed by wall-color (cannot
reach edge via 4-neighbor) with color 3.

Stub: Infeasible with simple Conv. Requires global flood-fill /
connectivity analysis. While iterative morphological dilation (3x3 Conv +
threshold) could approximate this, the number of iterations needed varies
per example (depends on cavity size), and the approach requires prohibited
Loop/Scan or runtime-variable iteration count. Opset 10 without control
flow cannot implement conditional iterative propagation.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 63
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
