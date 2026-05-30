# Task 040 规范

## 1. 核心规则

- 核心变换：绿色(3)替换为距离最近边框的颜色，按行列距离判断归属。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：当水平和垂直边界同时存在时（如 test 中），如何确定分界线。
- 当前采用的解释：按照最近边界的原则——若水平和垂直边界距离相等，可能有特定的优先级规则。
- 风险等级：`medium`

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 36 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: And+Equal+Less+Mul+Pad+ReduceMax+ReduceMin+ReduceSum+Slice+Sub+Where (36 nodes, 20 initializers)

## 5. 最终摘要

```yaml
task_id: 040
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 36 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: And+Equal+Less+Mul+Pad+ReduceMax+ReduceMin+ReduceSum+Slice+Sub+Where
actual_nodes: 36
```
