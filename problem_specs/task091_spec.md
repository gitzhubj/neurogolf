# Task 091 规范

## 1. 核心规则

- 核心变换：灰色(5)竖线为墙天蓝(8)为端点标记，提取紧凑外框结构输出。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：当 color=5 不存在时规则如何定义。当前解释：所有可见样例均有 5。风险等级：low。
- 歧义点：扩展方向为何仅垂直扩展而不水平扩展。当前解释：5-像素组件有 8-像素附着在上下方形成"边框"，水平方向无此类附件。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 43 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Add+And+ArgMax+Cast+Gather+Greater+Less+Mul+ReduceMax+Reshape+Slice+Sub+Where (43 nodes, 14 initializers)

## 5. 最终摘要

```yaml
task_id: 091
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 43 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Add+And+ArgMax+Cast+Gather+Greater+Less+Mul+ReduceMax+Reshape+Slice+Sub+Where
actual_nodes: 43
```
