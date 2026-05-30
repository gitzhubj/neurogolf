# Task 039 规范

## 1. 核心规则

- 核心变换：对称提取：找到对称图案最小外接矩形，输出左上角3x3子网格。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 14 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Add+ArgMax+Cast+Gather+Greater+Pad+ReduceSum+Slice (14 nodes, 9 initializers)

## 5. 最终摘要

```yaml
task_id: 039
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 14 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Add+ArgMax+Cast+Gather+Greater+Pad+ReduceSum+Slice
actual_nodes: 14
```
