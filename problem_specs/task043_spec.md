# Task 043 规范

## 1. 核心规则

- 核心变换：取首行灰色(5)列位置，在每行最右列有灰(5)的行上红(2)填充相同列位置。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：如果行已有非零内容（2 或 5）且最右列为 5，模式复制是否会覆盖原有内容？
  - 当前解释：是，模式复制覆盖整行，原内容被替换。
  - 风险等级：low
- 未发现主要歧义。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Multi-op custom architecture (9 nodes). Study baseline directly.
- `fusion_hint`: Ops used: Cast+Greater+Mul+Pad+Slice+Where...

Baseline 实际架构: Cast+Greater+Mul+Pad+Slice+Where (9 nodes, 14 initializers)

## 5. 最终摘要

```yaml
task_id: 043
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
memory_priority: Multi-op custom architecture (9 nodes). Study baseline directly.
fusion_hint: Ops used: Cast+Greater+Mul+Pad+Slice+Where...
main_risk: high — complex architecture, refer to baseline
confidence: medium
actual_ops: Cast+Greater+Mul+Pad+Slice+Where
actual_nodes: 9
```
