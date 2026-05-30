# Task 097 规范

## 1. 核心规则

- 核心变换：孤立移除：去除8邻域连通分量大小小于2的孤立像素，仅保留连通分量>=2的像素。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：8-连通 vs 4-连通。当前解释：8-连通（对角算邻居）。风险等级：low（已验证多个对角对保留）。
- 歧义点：是否执行多轮迭代（移除孤立后产生新的孤立）。当前解释：仅一轮，基于原始输入判断。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 11 nodes: Cast+Concat+Conv+Greater+ReduceSum+Slice+Where. Study baseline for optimal op sequence.

Baseline 实际架构: Cast+Concat+Conv+Greater+ReduceSum+Slice+Where (11 nodes, 6 initializers)

## 5. 最终摘要

```yaml
task_id: 097
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 11 nodes: Cast+Concat+Conv+Greater+ReduceSum+Slice+Where. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Cast+Concat+Conv+Greater+ReduceSum+Slice+Where
actual_nodes: 11
```
