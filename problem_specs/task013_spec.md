# Task 013 规范

## 1. 核心规则

- 核心变换：两非零种子像素决定填充方向(顶行水平/左列垂直)，以坐标差为步长交替放置两种颜色。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点: 长轴判定标准(如何从多个种子中选择主方向)。
- 当前采用的解释: 基于种子分布的 PCA 或几何主方向分析, 计算其最大扩展方向。
- 风险等级: medium(具体算法细节尚待验证, 但基于卷积的方案可规避精确几何推理)。

- 歧义点: 交替颜色的配对规则。
- 当前采用的解释: 颜色来自输入中种子的颜色及其配对色, 配对可能基于固定颜色表。
- 风险等级: medium

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 91 nodes: Cast+Concat+Conv+Greater+Mul+ReduceMax+ReduceSum+Slice+Sub+S. Study baseline for optimal op sequence.

Baseline 实际架构: Cast+Concat+Conv+Greater+Mul+ReduceMax+ReduceSum+Slice+Sub+Sum+Where (91 nodes, 16 initializers)

## 5. 最终摘要

```yaml
task_id: 013
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 91 nodes: Cast+Concat+Conv+Greater+Mul+ReduceMax+ReduceSum+Slice+Sub+S. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Cast+Concat+Conv+Greater+Mul+ReduceMax+ReduceSum+Slice+Sub+Sum+Where
actual_nodes: 91
```
