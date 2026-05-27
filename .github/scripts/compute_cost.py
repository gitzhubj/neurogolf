"""计算 ONNX 网络的 cost = 参数量 + 内存占用"""
import sys
import json
import numpy as np
import onnx


def compute_cost(onnx_path: str) -> dict:
    model = onnx.load(onnx_path)

    total_params = 0
    for init in model.graph.initializer:
        total_params += int(np.prod(init.dims))

    param_memory = total_params * 4

    try:
        inferred = onnx.shape_inference.infer_shapes(model)
    except Exception:
        inferred = model

    activation_memory = 0
    for vi in inferred.graph.value_info:
        dims = [d.dim_value for d in vi.type.tensor_type.shape.dim]
        if all(s > 0 for s in dims):
            activation_memory += int(np.prod(dims)) * 4

    memory_bytes = param_memory + activation_memory
    cost = total_params + memory_bytes

    return {
        "params": total_params,
        "memory_bytes": memory_bytes,
        "cost": cost,
        "score": round(max(1.0, 25.0 - np.log(max(cost, 1))), 4),
    }


def main():
    result = compute_cost(sys.argv[1])
    if '--json' in sys.argv:
        print(json.dumps(result))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")


if __name__ == '__main__':
    main()
