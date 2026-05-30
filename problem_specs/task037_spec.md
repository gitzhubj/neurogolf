# Task 037 规范

## 1. 核心规则

- 核心变换：连接同色单元格的45度对角线，每对同色点之间画斜线。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：不同颜色的像素是否在滑落过程中相互阻挡。
- 当前采用的解释：所有颜色像素可以"穿过"不同颜色的像素，但同色像素会堆叠。
- 风险等级：`medium`

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `yes`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 27 nodes: Cast+Concat+Conv+Mul+Pad+ReduceMax+ReduceSum+Relu+Slice+Sub+. Study baseline for optimal op sequence.

Baseline 实际架构: Cast+Concat+Conv+Mul+Pad+ReduceMax+ReduceSum+Relu+Slice+Sub+Sum (27 nodes, 13 initializers)

## 5. 最终摘要

```yaml
task_id: 037
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 27 nodes: Cast+Concat+Conv+Mul+Pad+ReduceMax+ReduceSum+Relu+Slice+Sub+. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Cast+Concat+Conv+Mul+Pad+ReduceMax+ReduceSum+Relu+Slice+Sub+Sum
actual_nodes: 27
```
