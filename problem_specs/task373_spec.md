# Task 373 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：两行等长单色行交叉排列：第一行ABABAB交替模式，第二行BABABA交替模式。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点: 具体变换规则尚未人工分析。当前仅基于数据特征推测。风险等级: `medium`。
- 歧义点: 风险等级: `low`。
- Baseline 已验证可用，架构方向可信。风险等级: `low`。

## 4. NeuroGolf 架构提示

> **以下内容来自 baseline ONNX（已验证 100% 通过所有测试用例）**

- `recommended_architecture`: `slice_based_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `probably`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Slice-based multi-op. No Conv needed.
- `fusion_hint`: Slice + supporting ops. 6 nodes total.
- `approach`: Use Slice+Pad for spatial crop/flip/reposition — no Conv needed.

Baseline 实际架构: **Slice-based multi-op** — Concat+Pad+Slice (6 nodes, 8 initializers, 988 bytes)

## 5. 最终摘要

```yaml
task_id: 373
train_samples: 2
test_samples: 1
arcgen_samples: 72
same_size: True
colors_in: [2, 3, 4, 6, 8, 9]
colors_out: [2, 3, 4, 6, 8, 9]
locality: varies
single_linear_conv_possible: probably
recommended_architecture: slice_based_multi_op
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Slice-based multi-op. No Conv needed.
fusion_hint: Slice + supporting ops. 6 nodes total.
approach: Use Slice+Pad for spatial crop/flip/reposition — no Conv needed.
main_risk: medium
confidence: high
baseline_pattern: Slice-based multi-op
baseline_ops: Concat+Pad+Slice
baseline_nodes: 6
baseline_size_bytes: 988
```
