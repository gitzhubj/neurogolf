"""Task 064 — Draw horizontal/vertical lines from block edge to seeds
sharing the same row or column.

Stub: Infeasible with simple Conv. Requires: (1) detect rectangular block
boundaries (min/max row/col), (2) locate seed pixels, (3) for each seed,
check row/column overlap with block, (4) draw lines from block edge to
seed. Steps (1)-(3) need global object detection and coordinate comparison.
Step (4) requires line drawing at specific positions determined by runtime
seed coordinates, which cannot be encoded in fixed Conv weights.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 64
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
