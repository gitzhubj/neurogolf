"""ONNX 合规性检查"""
import sys
import os
import onnx

FORBIDDEN_OPS = {'Loop', 'Scan', 'NonZero', 'Unique', 'Script', 'Function'}
MAX_SIZE_MB = 1.44


def validate(onnx_path: str) -> bool:
    errors = []

    size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        errors.append(f"文件过大: {size_mb:.2f}MB > {MAX_SIZE_MB}MB")

    try:
        model = onnx.load(onnx_path)
    except Exception as e:
        errors.append(f"无法加载 ONNX 文件: {e}")
        return _report(onnx_path, errors)

    try:
        onnx.checker.check_model(model)
    except Exception as e:
        errors.append(f"ONNX check 失败: {e}")

    try:
        onnx.shape_inference.infer_shapes(model)
    except Exception as e:
        errors.append(f"形状推断失败 (非静态形状?): {e}")

    for node in model.graph.node:
        if node.op_type in FORBIDDEN_OPS:
            errors.append(f"禁止的算子: {node.op_type} (节点: {node.name})")

    return _report(onnx_path, errors)


def _report(path, errors):
    if errors:
        print(f"FAIL {path}")
        for e in errors:
            print(f"  - {e}")
        return False
    print(f"PASS {path}")
    return True


if __name__ == '__main__':
    ok = validate(sys.argv[1])
    sys.exit(0 if ok else 1)
