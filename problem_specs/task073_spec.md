# Task 073 规范

## 1. 核心规则

- 核心变换：蓝色(1)像素垂直下落至底部灰色(5)行，原位置变黑。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 蓝色(1)是否会出现在行 3？当前未观察到，但不确定。风险: `low`。
- 如果蓝色下方不是灰色(5)会怎样？未在样例中出现。风险: `low`。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `single_conv`
- `locality`: `k`
- `single_linear_conv_possible`: `yes`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Single Conv, bias-free. Keep kernel minimal.
- `fusion_hint`: All logic in one Conv weight tensor.

Baseline 实际架构: Conv (1 nodes, 2 initializers)

## 5. 最终摘要

```yaml
task_id: 073
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: yes
recommended_architecture: single_conv
memory_priority: Single Conv, bias-free. Keep kernel minimal.
fusion_hint: All logic in one Conv weight tensor.
main_risk: low
confidence: high
actual_ops: Conv
actual_nodes: 1
```
