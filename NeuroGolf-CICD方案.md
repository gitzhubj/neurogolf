# NeuroGolf — GitHub Actions CI/CD 流水线方案

## 一、整体架构

```
                        PR 提交
                          │
                          ▼
              ┌──────────────────────┐
              │  Validate PR         │  ONNX合规性 · 禁用算子 · 文件大小 · 正确性
              └──────────┬───────────┘
                         │
                    ┌────┴────┐
                    │ 通过?    │
                    └────┬────┘
                    ✗ 否  │  ✓ 是
                 评论失败  │
                   原因    ▼
              ┌──────────────────────┐
              │  Cost Comparison     │  与 task_registry.json 对比 cost
              └──────────┬───────────┘
                         │
                    ┌────┴────┐
                    │ 改善?    │
                    └────┬────┘
                    ✗ 否  │  ✓ 是
                 评论不改善 │
                   原因    ▼
              ┌──────────────────────┐
              │  Auto Merge          │  自动合并 PR
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Update Registry     │  更新 task_registry.json
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Package & Submit    │  打包 · Kaggle API 提交
              └──────────────────────┘
```

## 二、文件结构

```
.github/
├── workflows/
│   ├── pr-validate.yml        # PR 触发：验证 + 对比 cost
│   ├── merge-to-main.yml      # main 分支推送：更新注册表 + 提交 Kaggle
│   └── scheduled-submit.yml   # 定时任务：兜底提交（防遗漏）
│
├── scripts/
│   ├── validate_onnx.py       # ONNX 合规性检查
│   ├── test_network.py        # 在测试数据上验证正确性
│   ├── compute_cost.py        # 计算 cost = params + memory
│   ├── compare_cost.py        # 与注册表对比，判断是否改善
│   ├── update_registry.py     # 更新 task_registry.json
│   ├── kaggle_submit.py       # Kaggle API 提交封装
│   └── generate_report.py     # 生成 PR 评论报告
│
└── config/
    └── task_registry.json     # 每个任务当前最优 cost 登记
```

## 三、task_registry.json 版本注册表

```json
{
  "version": "1.0",
  "updated": "2026-05-27T12:00:00Z",
  "tasks": {
    "001": {
      "cost": 520,
      "params": 100,
      "memory_bytes": 420,
      "architecture": "Conv1x1_10ch_nobias",
      "onnx_file": "task001.onnx",
      "onnx_size_bytes": 1240,
      "last_updated": "2026-05-27T10:00:00Z",
      "commit": "abc1234",
      "author": "username"
    },
    "002": {
      "cost": 1340,
      "params": 900,
      "memory_bytes": 440,
      "architecture": "Conv3x3_10ch",
      "onnx_file": "task002.onnx",
      "onnx_size_bytes": 3800,
      "last_updated": "2026-05-26T08:00:00Z",
      "commit": "def5678",
      "author": "other-user"
    }
  }
}
```

这是整个系统的**唯一真相源**（single source of truth）。所有 cost 对比、自动合并判断、Kaggle 提交都依赖此文件。

## 四、Workflow 详解

### 4.1 PR 验证流水线 (`pr-validate.yml`)

```yaml
name: PR Validate & Cost Check

on:
  pull_request:
    branches: [main]
    paths:
      - 'networks/**'
      - 'onnx_export/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    outputs:
      validation_passed: ${{ steps.validate.outputs.passed }}
      cost_report: ${{ steps.compare.outputs.report }}

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 需要 git diff 获取变更文件

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install onnx onnxruntime numpy

      - name: Detect changed ONNX files
        id: changed
        run: |
          CHANGED=$(git diff --name-only origin/main...HEAD -- onnx_export/*.onnx)
          echo "files=$CHANGED" >> $GITHUB_OUTPUT
          echo "count=$(echo "$CHANGED" | grep -c '.onnx' || echo 0)" >> $GITHUB_OUTPUT

      - name: Validate each ONNX file
        id: validate
        if: steps.changed.outputs.count > 0
        run: |
          FAILED=0
          for f in ${{ steps.changed.outputs.files }}; do
            echo "--- Validating $f ---"
            python .github/scripts/validate_onnx.py "$f" || FAILED=1
          done
          if [ $FAILED -eq 0 ]; then
            echo "passed=true" >> $GITHUB_OUTPUT
          else
            echo "passed=false" >> $GITHUB_OUTPUT
          fi

      - name: Compute cost & compare
        id: compare
        if: steps.validate.outputs.passed == 'true'
        run: |
          python .github/scripts/compare_cost.py \
            --registry .github/config/task_registry.json \
            --changed "${{ steps.changed.outputs.files }}" \
            --output report.md

      - name: Comment PR with report
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.existsSync('report.md') 
              ? fs.readFileSync('report.md', 'utf8') 
              : '验证失败，请检查 ONNX 文件合规性。';
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

### 4.2 自动合并 & 版本管理 & 提交 (`merge-to-main.yml`)

```yaml
name: Merge → Registry Update → Kaggle Submit

on:
  push:
    branches: [main]
    paths:
      - 'onnx_export/**'

jobs:
  update-and-submit:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GH_PAT }}  # PAT 以允许后续推送到 main

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install onnx onnxruntime numpy kaggle

      - name: Detect merged ONNX files
        id: changed
        run: |
          CHANGED=$(git diff --name-only HEAD~1..HEAD -- onnx_export/*.onnx)
          echo "files=$CHANGED" >> $GITHUB_OUTPUT

      - name: Update task registry
        id: registry
        run: |
          python .github/scripts/update_registry.py \
            --registry .github/config/task_registry.json \
            --files "${{ steps.changed.files }}" \
            --commit "${{ github.sha }}" \
            --author "${{ github.actor }}"

      - name: Commit registry update
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .github/config/task_registry.json
          git diff --staged --quiet || git commit -m "chore: update task registry [skip ci]"
          git push

      - name: Package & submit to Kaggle
        env:
          KAGGLE_USERNAME: ${{ secrets.KAGGLE_USERNAME }}
          KAGGLE_KEY: ${{ secrets.KAGGLE_KEY }}
        run: |
          python .github/scripts/kaggle_submit.py \
            --competition "neurogolf-2026" \
            --registry .github/config/task_registry.json \
            --message "Automated submission - $(git log -1 --pretty=%B | head -1)"
```

### 4.3 定时兜底提交 (`scheduled-submit.yml`)

防止 CI 流程中漏提。每天定时检查并提交。

```yaml
name: Scheduled Kaggle Submit (Fallback)

on:
  schedule:
    - cron: '17 3 * * *'   # 每天 03:17 UTC 执行
  workflow_dispatch:        # 允许手动触发

jobs:
  submit:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install kaggle

      - name: Check if submission needed
        id: check
        run: |
          python .github/scripts/kaggle_submit.py \
            --competition "neurogolf-2026" \
            --registry .github/config/task_registry.json \
            --message "Scheduled submission $(date -I)" \
            --dry-run
        env:
          KAGGLE_USERNAME: ${{ secrets.KAGGLE_USERNAME }}
          KAGGLE_KEY: ${{ secrets.KAGGLE_KEY }}
```

---

## 五、核心脚本说明

### 5.1 `validate_onnx.py` — ONNX 合规性检查

```python
"""检查单个 ONNX 文件的合规性"""
import sys
import os
import onnx

FORBIDDEN_OPS = {'Loop', 'Scan', 'NonZero', 'Unique', 'Script', 'Function'}
MAX_SIZE_MB = 1.44

def validate(onnx_path: str) -> bool:
    errors = []

    # 1. 文件存在 & 大小
    size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        errors.append(f"文件过大: {size_mb:.2f}MB > {MAX_SIZE_MB}MB")

    # 2. ONNX 加载
    try:
        model = onnx.load(onnx_path)
    except Exception as e:
        errors.append(f"无法加载 ONNX 文件: {e}")
        return _report(onnx_path, errors)

    # 3. 模型检查
    try:
        onnx.checker.check_model(model)
    except Exception as e:
        errors.append(f"ONNX check 失败: {e}")

    # 4. 形状推断（静态形状）
    try:
        onnx.shape_inference.infer_shapes(model)
    except Exception as e:
        errors.append(f"形状推断失败 (非静态形状?): {e}")

    # 5. 禁用算子扫描
    for node in model.graph.node:
        if node.op_type in FORBIDDEN_OPS:
            errors.append(f"禁止的算子: {node.op_type} (节点: {node.name})")

    return _report(onnx_path, errors)

def _report(path, errors):
    if errors:
        print(f"❌ {path} 验证失败:")
        for e in errors:
            print(f"   - {e}")
        return False
    print(f"✓ {path} 验证通过")
    return True

if __name__ == '__main__':
    ok = validate(sys.argv[1])
    sys.exit(0 if ok else 1)
```

### 5.2 `compute_cost.py` — Cost 计算

```python
"""计算 ONNX 网络的 cost = 参数量 + 内存占用"""
import sys
import numpy as np
import onnx

def compute_cost(onnx_path: str) -> dict:
    model = onnx.load(onnx_path)

    # 参数量
    total_params = 0
    for init in model.graph.initializer:
        total_params += int(np.prod(init.dims))

    # 内存占用 = 参数字节数 + 激活值字节数
    # 激活：假设 FP32，每层输出为 (1, H, W, C) × 4 bytes
    param_memory = total_params * 4
    activation_memory = _estimate_activation_memory(model)

    memory_bytes = param_memory + activation_memory
    cost = total_params + memory_bytes

    return {
        "params": total_params,
        "memory_bytes": memory_bytes,
        "cost": cost,
        "score": max(1, 25 - np.log(cost)),
    }

def _estimate_activation_memory(model) -> int:
    """估算中间激活的内存占用 (batch=1, FP32)"""
    inferred = onnx.shape_inference.infer_shapes(model)
    total = 0
    for vi in inferred.graph.value_info:
        shape = [d.dim_value for d in vi.type.tensor_type.shape.dim]
        if all(s > 0 for s in shape):
            total += int(np.prod(shape)) * 4  # FP32
    return total

if __name__ == '__main__':
    result = compute_cost(sys.argv[1])
    for k, v in result.items():
        print(f"{k}: {v}")
```

### 5.3 `compare_cost.py` — 对比注册表判断改善

```python
"""对比 PR 中的 ONNX 文件与注册表中的当前最优 cost"""
import sys
import json
import argparse
import re
from pathlib import Path
from compute_cost import compute_cost

def extract_task_id(filename: str) -> str:
    m = re.search(r'task(\d+)', Path(filename).name)
    return m.group(1) if m else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--registry', required=True)
    parser.add_argument('--changed', required=True)
    parser.add_argument('--output', default='report.md')
    args = parser.parse_args()

    with open(args.registry) as f:
        registry = json.load(f)

    improved = []
    regressed = []
    unchanged = []

    for onnx_path in args.changed.split():
        tid = extract_task_id(onnx_path)
        if not tid:
            continue

        result = compute_cost(onnx_path)
        new_cost = result['cost']
        old_entry = registry['tasks'].get(tid, {})
        old_cost = old_entry.get('cost', float('inf'))

        delta = old_cost - new_cost
        if delta > 0:
            improved.append((tid, old_cost, new_cost, delta, result))
        elif delta < 0:
            regressed.append((tid, old_cost, new_cost, -delta, result))
        else:
            unchanged.append((tid, new_cost, result))

    # 生成 Markdown 报告
    lines = ["## ONNX Cost 对比报告\n"]
    lines.append(f"| 任务 | 旧 Cost | 新 Cost | 变化 | 参数 | 内存 |")
    lines.append(f"|---|---:|---:|---:|---:|---:|")

    for tid, old, new, delta, r in improved:
        lines.append(f"| task{tid} | {old} | {new} | **-{delta}** ✓ | {r['params']} | {r['memory_bytes']} |")
    for tid, old, new, delta, r in regressed:
        lines.append(f"| task{tid} | {old} | {new} | **+{delta}** ✗ | {r['params']} | {r['memory_bytes']} |")
    for tid, cost, r in unchanged:
        lines.append(f"| task{tid} | {cost} | {cost} | 0 | {r['params']} | {r['memory_bytes']} |")

    # 结论
    lines.append("")
    if regressed:
        lines.append("### ⚠️ 有任务 cost 上升，请检查")
    elif improved:
        summary = ", ".join(f"task{t}" for t, _, _, _, _ in improved)
        lines.append(f"### ✓ {len(improved)} 个任务 cost 下降: {summary}")
        lines.append("此 PR 可自动合并。")
    else:
        lines.append("### Cost 无变化")

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    # 给 GitHub Actions 用的输出
    if improved and not regressed:
        with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write("improved=true\n")
            f.write(f"improved_count={len(improved)}\n")

    sys.exit(0 if improved and not regressed else 1 if regressed else 0)

if __name__ == '__main__':
    main()
```

### 5.4 `update_registry.py` — 更新版本注册表

```python
"""合并 PR 后更新 task_registry.json"""
import sys, json, argparse, re
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
        tid = re.search(r'task(\d+)', Path(onnx_path).name)
        if not tid:
            continue
        tid = tid.group(1)

        result = compute_cost(onnx_path)
        new_cost = result['cost']

        old = registry['tasks'].get(tid, {})
        if new_cost < old.get('cost', float('inf')):
            registry['tasks'][tid] = {
                "cost": new_cost,
                "params": result['params'],
                "memory_bytes": result['memory_bytes'],
                "onnx_file": Path(onnx_path).name,
                "onnx_size_bytes": Path(onnx_path).stat().st_size,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "commit": args.commit,
                "author": args.author,
            }
            updated = True
            print(f"✓ task{tid}: cost {old.get('cost', '∞')} → {new_cost}")

    if updated:
        registry['updated'] = datetime.now(timezone.utc).isoformat()
        with open(args.registry, 'w') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        print("Registry updated.")
    else:
        print("No improvements detected.")

if __name__ == '__main__':
    main()
```

### 5.5 `kaggle_submit.py` — Kaggle API 提交

```python
"""打包 ONNX 文件并通过 Kaggle API 提交"""
import sys, os, json, argparse, subprocess, tempfile, shutil
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--competition', required=True)
    parser.add_argument('--registry', required=True)
    parser.add_argument('--message', default='Automated submission')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    # 读取注册表，找到所有需提交的 ONNX 文件
    with open(args.registry) as f:
        registry = json.load(f)

    repo_root = Path(__file__).resolve().parents[2]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        files_to_pack = []

        for tid, info in registry['tasks'].items():
            onnx_path = repo_root / 'onnx_export' / info['onnx_file']
            if onnx_path.exists():
                dest = tmpdir / onnx_path.name
                shutil.copy2(onnx_path, dest)
                files_to_pack.append(dest.name)

        if not files_to_pack:
            print("No ONNX files to submit.")
            return

        # 打包
        zip_path = tmpdir / 'submission.zip'
        shutil.make_archive(str(zip_path.with_suffix('')), 'zip', tmpdir)

        if args.dry_run:
            print(f"[DRY RUN] Would submit: {args.competition}")
            print(f"[DRY RUN] Files: {files_to_pack}")
            print(f"[DRY RUN] Message: {args.message}")
            return

        # 提交
        cmd = [
            'kaggle', 'competitions', 'submit',
            '-c', args.competition,
            '-f', str(zip_path),
            '-m', args.message,
        ]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"Submission failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        print("Submission successful!")

if __name__ == '__main__':
    main()
```

---

## 六、GitHub Secrets 配置

需要在仓库 Settings → Secrets and variables → Actions 中配置：

| Secret 名称 | 说明 | 获取方式 |
|---|---|---|
| `KAGGLE_USERNAME` | Kaggle 账号名 | Kaggle Account 页面 |
| `KAGGLE_KEY` | Kaggle API Key | Kaggle Account → Create API Token |
| `GH_PAT` | GitHub Personal Access Token | GitHub Settings → Developer settings → PAT |
| `ARC_GEN_DATA` (可选) | ARC-GEN-100K 测试数据路径 | 如数据量大不适合入仓库 |

---

## 七、PR 自动合并机制

### 方案 A：GitHub Auto-merge（推荐）

在 compare_cost 脚本报告 cost 改善后，通过 GitHub Script 启用 auto-merge：

```yaml
- name: Enable auto-merge if improved
  if: steps.compare.outputs.improved == 'true'
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.pulls.merge({
        owner: context.repo.owner,
        repo: context.repo.repo,
        pull_number: context.issue.number,
        merge_method: 'squash'
      });
```

### 方案 B：条件性合并（更保守）

仅在满足所有条件时合并：
- 至少 1 个任务 cost 下降
- 0 个任务 cost 上升
- 所有 ONNX 合规性检查通过
- 正确性测试通过（如有）

### PR 标题规范

使用约定式 PR 标题便于自动判断：
```
feat(task042): reduce cost from 1520 to 980
fix(task007): fix validation error, cost unchanged
perf(task118,task133): optimize multiple tasks
```

---

## 八、完整 CI/CD 流程时序图

```
开发者                    GitHub Actions                     Kaggle
  │                           │                                │
  │  git push feat/task042    │                                │
  │  gh pr create             │                                │
  │ ─────────────────────────>│                                │
  │                           │ pr-validate.yml 触发           │
  │                           │ ├─ validate_onnx.py ✓         │
  │                           │ ├─ compute_cost.py             │
  │                           │ ├─ compare_cost.py (1520→980)  │
  │                           │ └─ 评论 PR 报告               │
  │  <── PR 评论: cost 改善 ──│                                │
  │                           │                                │
  │                           │ 自动合并 PR (squash merge)     │
  │                           │                                │
  │                           │ merge-to-main.yml 触发         │
  │                           │ ├─ update_registry.py          │
  │                           │ ├─ git commit registry.json    │
  │                           │ ├─ 打包所有 ONNX → .zip        │
  │                           │ └─ kaggle_submit.py ──────────>│
  │                           │                                │ 提交处理
  │                           │  <── submission ID ────────────│
  │                           │                                │
  │                           │ 评论 PR:                       │
  │  <── PR 已合并 + 提交 ───│ "Merged & submitted (ID: xxx)" │
  │                           │                                │
```

---

## 九、扩展考量

### 大规模协作
- 多人同时 PR 不同任务时，`task_registry.json` 可能冲突。建议使用 GitHub Merge Queue 串行化合并。
- 每个 PR 只修改少量任务，降低冲突概率。

### 本地开发闭环
```bash
# 本地一键验证 + 对比
python .github/scripts/validate_onnx.py onnx_export/task042.onnx && \
python .github/scripts/compute_cost.py onnx_export/task042.onnx && \
python .github/scripts/compare_cost.py \
  --registry .github/config/task_registry.json \
  --changed "onnx_export/task042.onnx"
```

### 私有测试集的安全处理
- 私有测试数据不应提交到仓库
- 使用 GitHub Secrets 存储数据路径或加密的数据文件
- 在 CI 中通过 `gpg` 解密或从私有存储下载
