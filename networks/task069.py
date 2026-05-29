"""Task 069 — Replace color-8 connected components with the pattern of
the non-8 source component, preserving shape.

Stub: Infeasible with simple Conv. Requires: (1) connected component
analysis to identify source (non-8) and targets (all-8), (2) shape
matching, (3) pattern transfer. Connected component labeling needs
iterative propagation or flood-fill, which exceeds Conv capabilities.
Pattern transfer requires copying source pixel values to each target's
spatial positions based on shape-matched offsets.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 69
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
