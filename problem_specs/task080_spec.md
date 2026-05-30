# Task 080 规范

## 1. 核心规则

- 核心变换：以少数色为中心向四邻域填充十字形多数色，灰色(5)分隔线保持。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 如何自动确定结构色 S？通常是出现频率最高且形成连续行列的非零颜色。风险: `low`。
- 如何确定填充色 F？通常是频率第二高的非零颜色。风险: `low`。
- 单元格边界如何确定？由结构色 S 的连续行列划分。风险: `low`。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 93 nodes: And+ArgMax+Cast+Clip+Concat+Conv+Equal+Gather+Greater+Mul+Or. Study baseline for optimal op sequence.

Baseline 实际架构: And+ArgMax+Cast+Clip+Concat+Conv+Equal+Gather+Greater+Mul+Or+ReduceMax+ReduceSum+Reshape+Sub+Sum+Where (93 nodes, 31 initializers)

## 5. 最终摘要

```yaml
task_id: 080
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 93 nodes: And+ArgMax+Cast+Clip+Concat+Conv+Equal+Gather+Greater+Mul+Or. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: And+ArgMax+Cast+Clip+Concat+Conv+Equal+Gather+Greater+Mul+Or+ReduceMax+ReduceSum+Reshape+Sub+Sum+Where
actual_nodes: 93
```
