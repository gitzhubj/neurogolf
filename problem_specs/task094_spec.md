# Task 094 规范

## 1. 核心规则

- 核心变换：每个蓝色(1)空心矩形框中心行画品红(6)贯穿水平线，中心列画品红贯穿竖直线。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：框架定义——必须是完整闭合的矩形 1-边框，还是任意 1-像素轮廓？当前解释：闭合矩形边框。风险等级：low（所有样例均为清晰闭合矩形）。
- 歧义点：多个框架的十字叠加区域颜色？当前解释：全部为 6，无冲突。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 35 nodes: Concat+Conv+Min+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum. Study baseline for optimal op sequence.

Baseline 实际架构: Concat+Conv+Min+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum (35 nodes, 21 initializers)

## 5. 最终摘要

```yaml
task_id: 094
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 35 nodes: Concat+Conv+Min+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Concat+Conv+Min+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum
actual_nodes: 35
```
