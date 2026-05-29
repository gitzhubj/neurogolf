"""Task 068 — Find the unique color appearing exactly once, draw a 3x3
red(2) box centered on that pixel.

Stub: Infeasible with simple Conv. Requires: (1) global color histogram
to identify the color with count=1, (2) locate its coordinates,
(3) draw a 3x3 box. Step (1) needs ReduceMin over per-channel counts
(global), step (2) needs Where-like coordinate extraction, step (3)
needs position-dependent value assignment. All exceed what opset 10
Conv+element-wise can express without Scatter/NonZero/Unique.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 68
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
