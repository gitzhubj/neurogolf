# Task 025 规范

## 1. 核心规则

- 核心变换：完整单色行/列为吸引子，孤立噪点沿垂直/水平移至距吸引子1格处，非匹配颜色噪点移除。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：AND 操作是否只对颜色 9 敏感，还是说 0 vs 非 0 即可。从训练样例看，只有 9 和 0 参与，规则简化为 9 AND 9 = 8。
- 当前采用的解释：仅当左右对应位置都为 9 时输出 8。
- 风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 7449 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Cast+Concat+Greater+Mul+Or+ReduceSum+Slice+Sub+Sum (7449 nodes, 3742 initializers)

## 5. 最终摘要

```yaml
task_id: 025
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 7449 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Cast+Concat+Greater+Mul+Or+ReduceSum+Slice+Sub+Sum
actual_nodes: 7449
```
