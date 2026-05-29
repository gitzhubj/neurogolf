"""Task 066 — Shortest Manhattan path from source(3) to target(2), avoiding
obstacles(8).

Stub: Infeasible with simple Conv. Requires BFS/Dijkstra shortest-path
search with obstacle avoidance. This is a global graph algorithm that
cannot be implemented with Conv+element-wise ops alone. Iterative
morphological dilation could approximate wavefront propagation, but the
number of iterations equals the path length (varies per example) and
requires dynamic control flow (Loop prohibited).
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 66
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
