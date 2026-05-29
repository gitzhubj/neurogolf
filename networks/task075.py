"""Task 075 — Copy 3x3 source pattern to each blue(1) marker location in
the right-side paste area.

Stub: Infeasible with Conv-only in opset 10. Requires: (1) detect each
blue(1) marker pixel, (2) for each marker, copy the 3x3 source pattern
(rows 0-2, cols 0-2) centered at the marker position. The source pattern
varies per example (cannot be hardcoded). Marker positions also vary.
Steps (1)-(2) need dynamic detection of marker count and positions, then
conditional pattern pasting — requiring Loop/NonZero/Scatter operations
which are all prohibited under opset 10.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 75
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
