# Task 098 规范

## 1. 核心规则

- 核心变换：每个单色实心矩形镂空，仅保留1像素宽的边框。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：L 形或非矩形形状的处理。当前解释：规则仅对矩形内部有效；非矩形形状的"内部"可能只有部分被清空。风险等级：medium（所有样例均为标准矩形）。
- 歧义点：边界像素判定（4 方向需全部为同色）。当前解释：只要 4 方向中有一方向出界或颜色不同，即为边框，保留。风险等级：low。

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
task_id: 098
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
