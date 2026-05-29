"""Task 057 — Crop non-zero content to bounding box, duplicate horizontally.

Stub: Infeasible with simple Conv. Requires: (1) bounding-box detection
(min/max row/col of non-zero pixels), (2) crop, (3) horizontal tiling.
All three are global, shape-changing operations not expressible by
fixed-weight Convs under opset 10.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 57
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
