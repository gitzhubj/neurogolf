# Task 292 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：周期性列变换：每第3列(c%3==0)中黄色(4)改为品红(6)。


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
- `fusion_hint`: Study baseline: 6 nodes, ops=Conv+Mul+Pad+Slice+Sum
- `approach`: Conv + supporting ops (Reduce/Where). Refer to baseline for exact op sequence.

Baseline 实际架构: **Conv + logic gates** — Conv+Mul+Pad+Slice+Sum (6 nodes, 9 initializers, 1411 bytes)

## 5. 最终摘要

```yaml
task_id: 292
train_samples: 5
test_samples: 1
arcgen_samples: 22
same_size: True
colors_in: [0, 4]
colors_out: [0, 4, 6]
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
recommended_kernel: 3x3
nonlinearity_needed: no
memory_priority: Conv + support ops (Reduce/Where/Mul/Sub). Minimize intermediate tensors.
fusion_hint: Study baseline: 6 nodes, ops=Conv+Mul+Pad+Slice+Sum
approach: Conv + supporting ops (Reduce/Where). Refer to baseline for exact op sequence.
main_risk: medium
confidence: high
baseline_pattern: Conv + logic gates
baseline_ops: Conv+Mul+Pad+Slice+Sum
baseline_nodes: 6
baseline_size_bytes: 1411
```
