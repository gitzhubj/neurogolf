# Task 036 规范

## 1. 核心规则

- 核心变换：统计所有非零颜色像素总数，选像素最少的颜色，取其最小外接矩形裁剪输出。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：如果多个颜色都有连通组件怎么办（train 中未出现）。
- 当前采用的解释：取第一个检测到的连通色。
- 风险等级：`low`

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 56 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Add+ArgMax+Cast+Div+Equal+Gather+Greater+Less+Mul+ReduceMax+ReduceSum+Reshape+Sub+Where (56 nodes, 17 initializers)

## 5. 最终摘要

```yaml
task_id: 036
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 56 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Add+ArgMax+Cast+Div+Equal+Gather+Greater+Less+Mul+ReduceMax+ReduceSum+Reshape+Sub+Where
actual_nodes: 56
```
