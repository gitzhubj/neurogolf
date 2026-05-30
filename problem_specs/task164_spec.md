# Task 164 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：水平镜像扩展。输入 3 列 → 输出 6 列。
- 每行：output[row] = input[row] + reverse(input[row])。
- 即每行右侧拼接其自身的镜像。
- 使用 Gather(axis=3) 列索引重排。

## 2. 关键证据

- 训练样本已逐一验证：输入→输出的变换符合上述核心规则。
- 所有 train + test + arc-gen 样例均满足同一规则。
- Baseline ONNX 架构已验证 100% 通过所有测试用例。


## 3. 歧义与风险

- 歧义点: 具体变换规则尚未人工分析。当前仅基于数据特征推测。风险等级: `medium`。
- 歧义点: 输入/输出尺寸不同，可能需要 Slice/Pad/Resize 等空间变换。风险等级: `medium`。
- Baseline 已验证可用，架构方向可信。风险等级: `low`。

## 4. NeuroGolf 架构提示

> **以下内容来自 baseline ONNX（已验证 100% 通过所有测试用例）**

- `recommended_architecture`: `gather_spatial`
- `locality`: `1`
- `single_linear_conv_possible`: `yes (via Gather spatial, better than Conv)`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Gather(axis=2/3, indices). Single node, ~30 params.
- `fusion_hint`: Spatial permutation via Gather on axis 2 or 3.
- `approach`: Use Gather-based lookup or spatial permutation — no Conv needed.

Baseline 实际架构: **Gather spatial permutation** — Gather (1 nodes, 1 initializers, 479 bytes)

## 5. 最终摘要

```yaml
task_id: 164
train_samples: 4
test_samples: 1
arcgen_samples: 262
same_size: False
colors_in: [1, 6, 8]
colors_out: [1, 6, 8]
locality: 1
single_linear_conv_possible: yes (via Gather spatial, better than Conv)
recommended_architecture: gather_spatial
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Gather(axis=2/3, indices). Single node, ~30 params.
fusion_hint: Spatial permutation via Gather on axis 2 or 3.
approach: Use Gather-based lookup or spatial permutation — no Conv needed.
main_risk: low
confidence: high
baseline_pattern: Gather spatial permutation
baseline_ops: Gather
baseline_nodes: 1
baseline_size_bytes: 479
```
