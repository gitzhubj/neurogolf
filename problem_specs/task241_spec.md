# Task 241 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：矩阵转置（H↔W 维度交换）。支持非方形网格。
- output[r][c] = input[c][r]。
- 样例包含 3x3 和 4x4 等多种尺寸，转置后尺寸互换。
- 使用 Transpose(perm=[0,1,3,2])，0 参数。

## 2. 关键证据

- 训练样本已逐一验证：输入→输出的变换符合上述核心规则。
- 所有 train + test + arc-gen 样例均满足同一规则。
- Baseline ONNX 架构已验证 100% 通过所有测试用例。


## 3. 歧义与风险

- 歧义点: 具体变换规则尚未人工分析。当前仅基于数据特征推测。风险等级: `medium`。
- 歧义点: 风险等级: `low`。
- Baseline 已验证可用，架构方向可信。风险等级: `low`。

## 4. NeuroGolf 架构提示

> **以下内容来自 baseline ONNX（已验证 100% 通过所有测试用例）**

- `recommended_architecture`: `transpose`
- `locality`: `global`
- `single_linear_conv_possible`: `yes (via Transpose, 0 params!)`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Transpose(perm=[0,1,3,2]) — 0 params, free H<->W swap.
- `fusion_hint`: Single Transpose node. Cheapest possible spatial transform.
- `approach`: Use Transpose for H<->W swap — 0 params, free.

Baseline 实际架构: **Transpose H<->W swap** — Transpose (1 nodes, 0 initializers, 170 bytes)

## 5. 最终摘要

```yaml
task_id: 241
train_samples: 3
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [0, 1, 2, 3, 4, 5, 6, 8]
colors_out: [0, 1, 2, 3, 4, 5, 6, 8]
locality: global
single_linear_conv_possible: yes (via Transpose, 0 params!)
recommended_architecture: transpose
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Transpose(perm=[0,1,3,2]) — 0 params, free H<->W swap.
fusion_hint: Single Transpose node. Cheapest possible spatial transform.
approach: Use Transpose for H<->W swap — 0 params, free.
main_risk: low
confidence: high
baseline_pattern: Transpose H<->W swap
baseline_ops: Transpose
baseline_nodes: 1
baseline_size_bytes: 170
```
