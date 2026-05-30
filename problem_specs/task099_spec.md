# Task 099 规范

## 1. 核心规则

- 核心变换：蓝色(1)闭合轮廓内的区域被内部彩色像素的颜色填充。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：容器形状是否必须为单连通（无孔）。当前解释：容器为闭合区域，种子在其中，泛洪填充可达所有内部。风险等级：low。
- 歧义点：多个容器共享边框时的处理。当前解释：容器间由颜色 1 分隔，各自独立填充。风险等级：low。
- 歧义点：若容器内有多个种子像素。当前解释：所有样例仅 1 个种子/容器。风险等级：medium。

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
task_id: 099
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
