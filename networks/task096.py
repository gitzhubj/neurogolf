"""Task 096 ¡ª STUB (baseline analysis)

Complex transformation requiring global/object-level operations beyond simple Conv.
See problem_specs/task096_spec.md for the full specification.

TODO: Design multi-layer or custom ONNX architecture.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu


def weight_fn(ch_out, ch_in, kernel_coord):
    if kernel_coord == (0, 0) and ch_out == ch_in:
        return 1.0
    return 0.0


def build():
    return nu.single_layer_conv2d_network(weight_fn, kernel_size=1)


if __name__ == '__main__':
    task_num = 96
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
