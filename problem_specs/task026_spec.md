# Task 026 规范

## 1. 核心规则

- 核心变换：蓝(1)竖线分左右各3列，比较对应位：均为黑(0)则输出天蓝(8)，否则黑(0)。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：精确的邻居计数阈值（2、3 或其他）未完全确定。
- 当前采用的解释：8 邻域内蓝色邻居数 >= 3 时填 2。
- 风险等级：medium（阈值可能随输入变化）。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Multi-op custom architecture (11 nodes). Study baseline directly.
- `fusion_hint`: Ops used: Concat+Mul+Pad+Slice+Sub+Sum...

Baseline 实际架构: Concat+Mul+Pad+Slice+Sub+Sum (11 nodes, 8 initializers)

## 5. 最终摘要

```yaml
task_id: 026
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
memory_priority: Multi-op custom architecture (11 nodes). Study baseline directly.
fusion_hint: Ops used: Concat+Mul+Pad+Slice+Sub+Sum...
main_risk: high — complex architecture, refer to baseline
confidence: medium
actual_ops: Concat+Mul+Pad+Slice+Sub+Sum
actual_nodes: 11
```
