# Task 059 规范

## 1. 核心规则

- 输入/输出均为 11×11。灰线（颜色 5）将网格分为 9 个区域（3×3 布局，灰线在 row/col 3 和 7）。
- 灰度线在输出中保持不变。
- 核心变换：区域填充。对每个被灰线分隔的子区域（3×3 或 3×4 等），统计该区域内出现的非零、非灰颜色的数量。该子区域在输出中被整体填充为该区域中出现次数最多的颜色（或其他基于全局的投票规则）。
- 若区域内无非零非灰颜色，输出保持为零。
- 注意：输出中每个区域要么全为某颜色，要么全为零，不会出现部分填充。
- 区域之间独立决定，但颜色选择可能受全局统计影响（train 中某些区域有多色但最终选出一种）。

## 2. 关键证据

- train 0：颜色 1 分布在右上和左下区域。输出右上区域填 1，左下区域填 1，其余区域为零。
- train 1：颜色 2 分布在多个区域。输出左侧区域填 2，右侧中区填 2。
- train 2：颜色 3 分布，输出右下区域填 3，左中区域填 3。
- 所有样例中，每个区域要么全填充该颜色的"胜出"色，要么全零。

## 3. 歧义与风险

- 歧义点：区域内多种颜色时如何决定填充色（多数票 vs 全局优先 vs 位置权重）。当前解释：多数票规则，平局时可能以全局出现最多的颜色为准。风险等级：medium。
- 歧义点：区域边界的确切位置（灰线所在行列属于哪个区域）。当前解释：灰线不属于任何区域，仅作分隔符。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 20 nodes: Cast+Conv+Greater+MatMul+Mul+Pad+ReduceMax+ReduceSum+Reshape. Study baseline for optimal op sequence.

Baseline 实际架构: Cast+Conv+Greater+MatMul+Mul+Pad+ReduceMax+ReduceSum+Reshape+Slice+Sub+Sum+Where (20 nodes, 19 initializers)

## 5. 最终摘要

```yaml
task_id: 059
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 20 nodes: Cast+Conv+Greater+MatMul+Mul+Pad+ReduceMax+ReduceSum+Reshape. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Cast+Conv+Greater+MatMul+Mul+Pad+ReduceMax+ReduceSum+Reshape+Slice+Sub+Sum+Where
actual_nodes: 20
```
