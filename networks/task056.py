"""Task 056 — 3x3 pattern (X, cross, L) classification → output 1x1 color.

Stub: Infeasible with simple Conv. Requires: (1) shape classification of
3x3 non-zero mask (X-shape, cross, L-shape), (2) shape-to-color lookup.
Shape classification is inherently non-linear and pattern-dependent,
not expressible by Conv under opset 10 constraints.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 56
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
