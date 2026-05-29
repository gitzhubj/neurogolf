"""Task 060 — Horizontal fill: for rows with left/right color endpoints at
col 0 and col 10, fill left-half with left color, mid col 5 with gray(5),
right-half with right color.

Stub: Infeasible with simple Conv. Each output position depends on the
endpoint colors at cols 0 and 10 of the same row, which requires
non-local information. A single Conv (even 1x11 covering full width)
cannot encode position-dependent copying from specific columns because
the same kernel weights are applied at every position. While Slice+Tile+
Concat could broadcast endpoint colors, the approach requires conditional
logic (detecting whether endpoints exist) that exceeds opset 10 capabilities.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 60
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
