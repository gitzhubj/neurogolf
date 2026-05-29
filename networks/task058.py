"""Task 058 — Generate spiral maze pattern from all-zero input.

Stub: Input is all zeros (color 0 across the whole grid). The maze output
depends on the grid dimensions (H×W), which varies per example (5x5 up to
20x20). Since the (1,10,30,30) input encoding differs per grid size
(channel 0 = 1.0 spans different areas), the network must detect
dimensions and algorithmically generate the maze. This requires iterative
spiral generation logic that is infeasible with Conv+element-wise ops
in opset 10 (no Loop/Scan allowed).

A Constant-based output cannot handle varying grid sizes. A single
network with fixed weights cannot generate different maze patterns for
different H×W combinations without prohibited control flow.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 58
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
