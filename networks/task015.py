"""Task 015 - Color[1] orthogonal expansion as Color[7], Color[2] diagonal expansion as Color[4]

Architecture: single 3x3 Conv with ch0 cancellation via negative weights.

Rule:
  - Color 1 (blue, ch1): keep identity at (0,0) AND expand orthogonally
    (up/down/left/right) as color 7 (orange, ch7)
  - Color 2 (red, ch2): keep identity at (0,0) AND expand diagonally
    (4 corners) as color 4 (yellow, ch4)
  - All other foreground colors (ch3,5,6,8,9): pass through unchanged
  - Background (ch0): set to 0 wherever ANY foreground color exists
    (using negative weights from each foreground channel)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import neurogolf_utils as nu


def weight_fn(ch_out, ch_in, kernel_coord):
    # Expansion offsets for color 1 -> color 7 (orthogonal)
    ORTHO = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    # Expansion offsets for color 2 -> color 4 (diagonal)
    DIAG = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    if ch_out == 0:
        # Background channel: identity minus all foreground contributions
        if ch_in == 0 and kernel_coord == (0, 0):
            return 1.0  # keep background by default
        # Subtract background at positions where ANY foreground color exists
        # (including expansion positions)
        if ch_in in range(1, 10) and kernel_coord == (0, 0):
            return -1.0  # subtract bg at identity positions
        if ch_in == 1 and kernel_coord in ORTHO:
            return -1.0  # subtract bg at color-1 expansion positions
        if ch_in == 2 and kernel_coord in DIAG:
            return -1.0  # subtract bg at color-2 expansion positions
        return 0.0

    # Foreground channels
    if kernel_coord == (0, 0) and ch_out == ch_in:
        # Identity for all foreground channels
        if ch_in in range(1, 10):
            return 1.0

    # Color 1: orthogonal expansion as color 7
    if ch_in == 1 and ch_out == 7 and kernel_coord in ORTHO:
        return 1.0

    # Color 2: diagonal expansion as color 4
    if ch_in == 2 and ch_out == 4 and kernel_coord in DIAG:
        return 1.0

    return 0.0


def build():
    return nu.single_layer_conv2d_network(weight_fn, kernel_size=3)


if __name__ == '__main__':
    task_num = 15
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
