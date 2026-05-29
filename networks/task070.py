"""Task 070 — Fill 0-cells adjacent to color-8 walls inside enclosed
regions with color 3.

Stub: Infeasible with simple Conv. Requires: (1) detect color-8 wall
enclosures, (2) identify interior 0-cells adjacent to walls,
(3) conditional fill. Enclosure detection needs flood-fill from grid
edges to distinguish interior from exterior. Adjacency check needs
local neighborhood inspection. The combination of global connectivity
analysis + conditional local fill exceeds Conv capabilities.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 70
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
