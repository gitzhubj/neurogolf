"""合并 PR 后更新 task_registry.json"""
import sys
import json
import argparse
import re
from pathlib import Path
from datetime import datetime, timezone
from compute_cost import compute_cost


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--registry', required=True)
    parser.add_argument('--files', required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--author', required=True)
    args = parser.parse_args()

    with open(args.registry) as f:
        registry = json.load(f)

    updated = False
    for onnx_path in args.files.split():
        onnx_path = onnx_path.strip()
        if not onnx_path:
            continue
        m = re.search(r'task(\d+)', Path(onnx_path).name)
        if not m:
            continue
        tid = m.group(1)

        result = compute_cost(onnx_path)
        new_cost = result['cost']
        old = registry['tasks'].get(tid, {})
        old_cost = old.get('cost', float('inf'))

        if new_cost < old_cost:
            onnx_file = Path(onnx_path).name
            registry['tasks'][tid] = {
                "cost": new_cost,
                "params": result['params'],
                "memory_bytes": result['memory_bytes'],
                "onnx_file": onnx_file,
                "onnx_size_bytes": Path(onnx_path).stat().st_size,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "commit": args.commit,
                "author": args.author,
            }
            updated = True
            print(f"OK task{tid}: cost {old_cost} -> {new_cost}")

    if updated:
        registry['updated'] = datetime.now(timezone.utc).isoformat()
        with open(args.registry, 'w') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        print("Registry updated.")
    else:
        print("No improvements — registry unchanged.")


if __name__ == '__main__':
    main()
