"""Show Tier 1/2 tasks with their baseline architecture and data characteristics."""
import sys
import json
import onnx
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]

# Tier mapping based on baseline architecture
TIER_MAP = {
    'gather_lookup': 'Tier1',
    'transpose': 'Tier1',
    'slice_pad': 'Tier1',
    'single_conv': 'Tier1',
    'gather_spatial': 'Tier2',
    'slice_based_multi_op': 'Tier2',
    'gather_based_multi_op': 'Tier2',
}


def get_tasks():
    tiers = defaultdict(list)
    for tid in range(1, 401):
        spec_path = REPO_ROOT / f'problem_specs/task{tid:03d}_spec.md'
        base_path = REPO_ROOT / f'baseline/task{tid:03d}.onnx'
        data_path = REPO_ROOT / f'input/task{tid:03d}.json'

        if not spec_path.exists() or not base_path.exists():
            continue

        spec = spec_path.read_text(encoding='utf-8')
        model = onnx.load(str(base_path))
        ops = [n.op_type for n in model.graph.node]

        with open(data_path) as f:
            data = json.load(f)

        trains = data.get('train', [])
        first = trains[0] if trains else {}
        in_grid = first.get('input', [])
        out_grid = first.get('output', [])
        in_h = len(in_grid)
        in_w = len(in_grid[0]) if in_grid else 0
        out_h = len(out_grid)
        out_w = len(out_grid[0]) if out_grid else 0

        # Extract architecture from spec
        arch = ''
        for line in spec.split('\n'):
            if 'recommended_architecture:' in line:
                parts = line.split('`')
                if len(parts) >= 2:
                    arch = parts[1]
                break

        tier = TIER_MAP.get(arch, 'Tier5')

        tiers[tier].append({
            'tid': tid,
            'arch': arch,
            'ops': '+'.join(sorted(set(ops))),
            'nodes': len(ops),
            'in': f'{in_h}x{in_w}',
            'out': f'{out_h}x{out_w}',
            'trains': len(trains),
            'tests': len(data.get('test', [])),
        })

    return tiers


def main():
    tiers = get_tasks()

    for tier_name in ['Tier1', 'Tier2']:
        tasks = tiers[tier_name]
        print(f'=== {tier_name} ({len(tasks)} tasks) ===')
        print(f'{"Task":<8} {"Arch":<25} {"Ops":<30} {"N":>3} {"In":>8} {"Out":>8} {"Tr":>3}')
        print('-' * 95)
        for t in tasks:
            print(f"task{t['tid']:03d}  {t['arch']:<25} {t['ops']:<30} {t['nodes']:>3} "
                  f"{t['in']:>8} {t['out']:>8} {t['trains']:>3}")
        print()

    # Summary
    for tier_name in ['Tier1', 'Tier2', 'Tier5']:
        print(f'{tier_name}: {len(tiers[tier_name])} tasks')


if __name__ == '__main__':
    main()
