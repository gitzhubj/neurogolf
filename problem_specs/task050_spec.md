# Task 050 规范

## 1. 核心规则

- 核心变换：每行/列中成对浅蓝(8)端点之间用绿(3)画水平/垂直线。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：如果某行有 3 个以上 8 像素，是否所有相邻对之间都要填充？
  - 当前解释：不，仅填充最左和最右之间的区间（一整段），而不是分段填充。
  - 风险等级：low
- 歧义点：横向和纵向填充在同一单元格重叠时，颜色优先级？
  - 当前解释：两者均为 3，重叠无冲突。
  - 风险等级：low

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Multi-op custom architecture (19 nodes). Study baseline directly.
- `fusion_hint`: Ops used: And+Cast+Concat+CumSum+Or+Pad+Slice+Xor...

Baseline 实际架构: And+Cast+Concat+CumSum+Or+Pad+Slice+Xor (19 nodes, 9 initializers)

## 5. 最终摘要

```yaml
task_id: 050
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
memory_priority: Multi-op custom architecture (19 nodes). Study baseline directly.
fusion_hint: Ops used: And+Cast+Concat+CumSum+Or+Pad+Slice+Xor...
main_risk: high — complex architecture, refer to baseline
confidence: medium
actual_ops: And+Cast+Concat+CumSum+Or+Pad+Slice+Xor
actual_nodes: 19
```
