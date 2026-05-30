# Task 032 规范

## 1. 核心规则

- 核心变换：所有非零像素列内垂直下落到底部(重力效果)，保持列内相对顺序。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 19 nodes: Cast+Conv+CumSum+Equal+Greater+Mul+Pad+ReduceSum+ScatterElem. Study baseline for optimal op sequence.

Baseline 实际架构: Cast+Conv+CumSum+Equal+Greater+Mul+Pad+ReduceSum+ScatterElements+Sign+Slice+Sqrt+Sub+Sum+Where (19 nodes, 10 initializers)

## 5. 最终摘要

```yaml
task_id: 032
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 19 nodes: Cast+Conv+CumSum+Equal+Greater+Mul+Pad+ReduceSum+ScatterElem. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Cast+Conv+CumSum+Equal+Greater+Mul+Pad+ReduceSum+ScatterElements+Sign+Slice+Sqrt+Sub+Sum+Where
actual_nodes: 19
```
