# Task 015 规范

## 1. 核心规则

- 核心变换：红色(2)像素四角方向添加浅蓝(4)，蓝色(1)像素四邻域方向添加橙色(7)。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点: 扩展仅适用于颜色 1 和 2, 还是所有非零颜色都有某种扩展规则。
- 当前采用的解释: 颜色 1 正交扩展, 颜色 2 对角扩展。其他颜色保持原样(无扩展)。
- 风险等级: low

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `single_conv`
- `locality`: `k`
- `single_linear_conv_possible`: `yes`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Single Conv, bias-free. Keep kernel minimal.
- `fusion_hint`: All logic in one Conv weight tensor.

Baseline 实际架构: Conv (1 nodes, 1 initializers)

## 5. 最终摘要

```yaml
task_id: 015
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
