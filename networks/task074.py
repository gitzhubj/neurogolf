"""Task 074 — Replace maroon(9) rectangular patches with mirror-reflected
content from surrounding area.

Stub: Infeasible with Conv-only in opset 10. Requires: (1) detect the
bounding box of each maroon(9) region, (2) compute reflection-mapped
coordinates for every pixel inside the 9-region, (3) copy the reflected
pixel values into the output. Step (2) needs coordinate transforms
(position-dependent logic), and step (3) needs a gather/scatter operation
to index and place pixel values — both are unavailable under opset 10
(no Scatter, NonZero, or dynamic indexing). Conv kernels are spatially
uniform and cannot express per-pixel coordinate remapping.
"""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def build():
    return nu.single_layer_conv2d_network(lambda o, i, kc: 1.0 if kc == (0,0) and o == i else 0.0, kernel_size=1)

if __name__ == '__main__':
    task_num = 74
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
