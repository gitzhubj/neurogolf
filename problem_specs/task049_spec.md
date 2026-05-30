# Task 049 规范

## 1. 核心规则

- 核心变换：找面积最小的有色实心矩形块，以其外接矩形大小输出纯色块。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：如果有两个并列的、面积相同的"最内层"矩形，选哪一个？
  - 当前解释：不确定。train 中未出现并列最内层情况。
  - 风险等级：medium
- 歧义点：最内层是严格矩形还是可以是任意形状？
  - 当前解释：所有观测中均为完美矩形（边框规则、填充完整）。
  - 风险等级：low

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 29 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Add+ArgMax+Cast+Gather+Greater+Less+Neg+ReduceMax+ReduceSum+Reshape+Slice+Where (29 nodes, 12 initializers)

## 5. 最终摘要

```yaml
task_id: 049
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 29 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Add+ArgMax+Cast+Gather+Greater+Less+Neg+ReduceMax+ReduceSum+Reshape+Slice+Where
actual_nodes: 29
```
