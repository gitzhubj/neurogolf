# Task 017 规范

## 1. 核心规则

- 核心变换：网格周期性模式自动补全，将零值恢复为对应周期相位的正确颜色。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点: 对称轴的具体位置(是网格的正中线还是图案自身的对称轴)。
- 当前采用的解释: 网格的几何中线, 或图案的"自然对称轴"(即图案到镜像的距离等于镜像到边界的距离)。
- 风险等级: medium

- 歧义点: 多个不相连的图案如何处理。
- 当前采用的解释: 每个独立图案分别做镜像, 互不影响。
- 风险等级: low

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 67 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: And+ArgMax+Cast+Concat+Equal+Gather+Greater+Pad+ReduceMax+ReduceSum+Reshape+Slice+Sum+Where (67 nodes, 27 initializers)

## 5. 最终摘要

```yaml
task_id: 017
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 67 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: And+ArgMax+Cast+Concat+Equal+Gather+Greater+Pad+ReduceMax+ReduceSum+Reshape+Slice+Sum+Where
actual_nodes: 67
```
