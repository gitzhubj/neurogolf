"""Task 061 — Modular multiplication table: output[r,c] = (r*c+1) mod M
(with 0→M), where M = max non-zero color in input. Fill 0 cells only.

Stub: Infeasible with simple Conv. Requires: (1) global ReduceMax to find
M, (2) multiplication and modulo operations per cell, (3) conditional
fill (only where input is 0). Steps (1) and (2) require global statistics
and arithmetic beyond Conv capabilities. While step (1) can use ReduceMax,
step (2) needs per-pixel (r,c) computation dependent on M, which varies
per example (M=5,6,7,8,9 in train+test). 9 possible M's would need 9x
pre-computed patterns with selection logic, violating the single-fixed-weight
constraint across examples.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 61
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
