# Task 075 规范

## 1. 核心规则

- 核心变换：以蓝色(1)像素为中心复制左上角灰色(5)分隔线左侧的3x3图案。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 蓝色标记是否一定位于目标 3x3 块的正中心？所有样例均如此。风险: `low`。
- 如果两个蓝色标记距离过近导致 3x3 块重叠会怎样？未在样例中出现。风险: `low`。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 46 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Concat+Mul+Pad+ReduceSum+Relu+Slice+Sub+Sum (46 nodes, 30 initializers)

## 5. 最终摘要

```yaml
task_id: 075
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 46 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Concat+Mul+Pad+ReduceSum+Relu+Slice+Sub+Sum
actual_nodes: 46
```
