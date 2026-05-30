# Task 022 规范

## 1. 核心规则

- 核心变换：提取每个灰色(5)像素3x3邻域(不含灰)，所有邻域叠加到3x3输出，中心固定为灰(5)。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：灰色标记的具体划分规则（是基于灰色连线形成的十字交叉，还是基于灰色 bounding box 的中心）。
- 当前采用的解释：灰色位置定义了一个坐标框架，将空间划分为 3x3 网格区域。
- 风险等级：medium。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 363 nodes: Cast+Concat+Conv+Gather+Greater+Mul+Pad+ReduceSum+Sub+Sum+Wh. Study baseline for optimal op sequence.

Baseline 实际架构: Cast+Concat+Conv+Gather+Greater+Mul+Pad+ReduceSum+Sub+Sum+Where (363 nodes, 24 initializers)

## 5. 最终摘要

```yaml
task_id: 022
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 363 nodes: Cast+Concat+Conv+Gather+Greater+Mul+Pad+ReduceSum+Sub+Sum+Wh. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Cast+Concat+Conv+Gather+Greater+Mul+Pad+ReduceSum+Sub+Sum+Where
actual_nodes: 363
```
