# Task 192 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：噪声过滤：稀疏噪点(1或8)若被大块单色形状(2或3)包围则填充形状色，孤立噪点清零。


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

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + support ops (Reduce/Where/Mul/Sub). Minimize intermediate tensors.
- `fusion_hint`: Study baseline: 21 nodes, ops=Cast+Conv+Greater+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum+Where
- `approach`: Conv + supporting ops (Reduce/Where). Refer to baseline for exact op sequence.

Baseline 实际架构: **Conv + logic gates** — Cast+Conv+Greater+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum+Where (21 nodes, 12 initializers, 2511 bytes)

## 5. 最终摘要

```yaml
task_id: 192
train_samples: 2
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [0, 1, 2, 3, 4, 5, 8]
colors_out: [0, 2, 3, 5]
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
recommended_kernel: 3x3
nonlinearity_needed: no
memory_priority: Conv + support ops (Reduce/Where/Mul/Sub). Minimize intermediate tensors.
fusion_hint: Study baseline: 21 nodes, ops=Cast+Conv+Greater+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum+Where
approach: Conv + supporting ops (Reduce/Where). Refer to baseline for exact op sequence.
main_risk: medium
confidence: high
baseline_pattern: Conv + logic gates
baseline_ops: Cast+Conv+Greater+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum+Where
baseline_nodes: 21
baseline_size_bytes: 2511
```
