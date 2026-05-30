# Task 066 规范

## 1. 核心规则

- 核心变换：绿色(3)像素经过空白格形成路径连接绿色和红色(2)两个簇。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 当存在多条等长最短路径时:未指定选择规则。风险:medium(不同路径选择可能导致输出不同)。
- 路径终点:路径末端是紧邻 2 的 0 单元格,而不是覆盖 2 本身。风险:low。
- 目标(2)可能在路径完成后仍然保留 2,不会变为 3。风险:low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 1642 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Abs+Add+And+Cast+Clip+Concat+CumSum+Einsum+Gather+Greater+Less+LessOrEqual+MatMul+Mul+ReduceMax+ReduceMin+ReduceSum+Sub+Unsqueeze+Where (1642 nodes, 29 initializers)

## 5. 最终摘要

```yaml
task_id: 066
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 1642 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Abs+Add+And+Cast+Clip+Concat+CumSum+Einsum+Gather+Greater+Less+LessOrEqual+MatMul+Mul+ReduceMax+ReduceMin+ReduceSum+Sub+Unsqueeze+Where
actual_nodes: 1642
```
