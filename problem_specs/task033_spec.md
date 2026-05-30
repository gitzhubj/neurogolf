# Task 033 规范

## 1. 核心规则

- 核心变换：十字分隔线分3x3区域，各区域图形沿分隔线镜像复制到相邻空白区，镜像用分隔线颜色。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：反射方向的具体映射（哪个格反射到哪个格）。
- 当前采用的解释：每个有形状的格关于中心（水平和垂直 L 线的交点）反射到对角格。
- 风险等级：`medium`

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 16 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Cast+Gather+Greater+Mul+Pad+ReduceMax+ReduceSum+Sub+Where (16 nodes, 6 initializers)

## 5. 最终摘要

```yaml
task_id: 033
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 16 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Cast+Gather+Greater+Mul+Pad+ReduceMax+ReduceSum+Sub+Where
actual_nodes: 16
```
