"""Task 051 — Direction detection + line projection from diamond shape.

Stub: Infeasible with simple Conv. Requires: (1) detect diamond/arrow
orientation from shape, (2) find center cell color, (3) project line
along the direction to grid edge. All three steps are global object-level
operations that exceed what Conv+element-wise can express under opset 10.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 51
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
