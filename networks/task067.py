"""Task 067 — Find horizontal periodicity, output first period block.

Stub: Infeasible with simple Conv. Requires: (1) scan columns to find
minimum period N such that col[i] == col[i+N] for all i, (2) slice to
output first N columns. Period detection requires pairwise column
comparison across the full width, which is a global operation not
expressible by Conv with fixed spatial kernel.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 67
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
