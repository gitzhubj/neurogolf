"""Task 055 — Fill grid regions delimited by color-8 gridlines with
position-dependent colors.

Stub: Infeasible with simple Conv. Region boundaries (color-8 grid lines)
appear at different positions across examples, and the fill color per
region varies by example. A single fixed-weight Conv cannot encode
the position-to-color mapping across all example configurations.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 55
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
