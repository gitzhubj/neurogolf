# Task 027 规范

## 1. 核心规则

- 核心变换：蓝(1)形状左侧凹陷用红(2)填充：单元格上下方及同行右侧均存在蓝色。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：两个像素的列位置是否影响输出布局宽度。从样例看，列位置不影响。
- 当前采用的解释：列位置不影响，仅行位置决定区域划分。
- 风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 22 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Concat+Greater+Mul+Pad+ReduceSum+Slice+Sub+Sum+Where (22 nodes, 13 initializers)

## 5. 最终摘要

```yaml
task_id: 027
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 22 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Concat+Greater+Mul+Pad+ReduceSum+Slice+Sub+Sum+Where
actual_nodes: 22
```
