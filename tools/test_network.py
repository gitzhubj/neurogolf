"""检查 ONNX 模型在测试数据上的正确性"""
import sys
import json
import argparse
from pathlib import Path


def test_onnx(onnx_path: str, task_json: str) -> dict:
    """在给定测试数据上验证 ONNX 模型"""
    # TODO: 实现 ONNX Runtime 推理 + 像素级比对
    return {"passed": 0, "total": 0, "status": "not_implemented"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--onnx', required=True)
    parser.add_argument('--task-json', required=True)
    args = parser.parse_args()
    result = test_onnx(args.onnx, args.task_json)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
