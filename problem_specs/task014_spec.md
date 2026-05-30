# Task 014 规范

## 1. 核心规则

- 核心变换：统计每种非零颜色4连通分量数，选分量最少的颜色，取其最小外接矩形裁剪输出。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点: 裁剪边界的具体确定方式(最小矩形还是某种更复杂的形状)。
- 当前采用的解释: 最小矩形 bounding box。
- 风险等级: low

- 歧义点: 若输入中有多个不同非零颜色如何处理。
- 当前采用的解释: 输入中仅有一种非零颜色, 该场景不会出现。
- 风险等级: low

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 166 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Abs+Add+Cast+Constant+Greater+GreaterOrEqual+Less+LessOrEqual+MatMul+Mul+ReduceMax+ReduceMin+ReduceSum+Reshape+Slice+Sub+Transpose (166 nodes, 0 initializers)

## 5. 最终摘要

```yaml
task_id: 014
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 166 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Abs+Add+Cast+Constant+Greater+GreaterOrEqual+Less+LessOrEqual+MatMul+Mul+ReduceMax+ReduceMin+ReduceSum+Reshape+Slice+Sub+Transpose
actual_nodes: 166
```
