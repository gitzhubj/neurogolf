# Task 072 规范

## 1. 核心规则

- 核心变换：黄色(4)分隔线上下两个区域逐像素异或(XOR)，结果输出绿色(3)。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

> 未发现主要歧义。规则明确，所有样例严格一致。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Multi-op custom architecture (9 nodes). Study baseline directly.
- `fusion_hint`: Ops used: Abs+Concat+Pad+Slice+Sub...

Baseline 实际架构: Abs+Concat+Pad+Slice+Sub (9 nodes, 8 initializers)

## 5. 最终摘要

```yaml
task_id: 072
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
memory_priority: Multi-op custom architecture (9 nodes). Study baseline directly.
fusion_hint: Ops used: Abs+Concat+Pad+Slice+Sub...
main_risk: high — complex architecture, refer to baseline
confidence: medium
actual_ops: Abs+Concat+Pad+Slice+Sub
actual_nodes: 9
```
