# Task 034 规范

## 1. 核心规则

- 核心变换：2x2色块红(2)角指示对角线生长方向，另一色沿该方向延伸形成45度梯形。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：传播方向的具体映射（C 在 2x2 块中哪个位置对应哪个对角方向）并非 100% 确定。
- 当前采用的解释：C 的位置决定传播沿主对角线还是反对角线。
- 风险等级：`medium`

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 87 nodes: Abs+And+Cast+Concat+Conv+Gather+Greater+Less+Mul+Not+Or+Redu. Study baseline for optimal op sequence.

Baseline 实际架构: Abs+And+Cast+Concat+Conv+Gather+Greater+Less+Mul+Not+Or+ReduceMax+ReduceSum+Sub+Sum+Where (87 nodes, 16 initializers)

## 5. 最终摘要

```yaml
task_id: 034
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 87 nodes: Abs+And+Cast+Concat+Conv+Gather+Greater+Less+Mul+Not+Or+Redu. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Abs+And+Cast+Concat+Conv+Gather+Greater+Less+Mul+Not+Or+ReduceMax+ReduceSum+Sub+Sum+Where
actual_nodes: 87
```
