# Task 090 规范

## 1. 核心规则

- 输入/输出尺寸相同（3×30 到 4×24 不等）。
- 输入主要由颜色 1 和 0 组成，部分样例包含 5 作为分隔标记。
- 核心变换：在网格中找到跨多行的连续零列区间（"垂直空隙"），将该空隙区域填充为颜色 6。
- 零列区间的选择规则：在多个行中同一列范围内全为 0 的最宽连续区间。该区间的所有行（在该列范围内）均填充为 6。
- 颜色 5 为固定分隔符，不参与变换。

## 2. 关键证据

- train 0：3×30。空隙在 col 15-18（4 列宽）rows 1-2，填充为 6。
- train 1：4×20。空隙在 col 14-16（3 列宽）rows 0-1，填充为 6。
- train 2：2×20。空隙在 col 2-6（5 列宽）rows 0-1，填充为 6。
- train 3：4×20。空隙在 col 17-19（3 列宽）rows 0-2，填充为 6。
- test 0：空隙在 col 1-3（3 列宽）rows 0-2，填充为 6。

## 3. 歧义与风险

- 歧义点：空隙选择的精确规则（最长连续零段 vs 满足某些位置条件）。当前解释：在所有行中同一列范围均为零的最宽区间。风险等级：low。
- 歧义点：多个不相连的空隙时选哪个。当前解释：选最宽的，或都填充。风险等级：low（所有样例仅一个目标空隙）。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `yes`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 246 nodes: Cast+Conv+ConvTranspose+Gather+Max+Mul+Pad+ReduceMax+Relu+Sl. Study baseline for optimal op sequence.

Baseline 实际架构: Cast+Conv+ConvTranspose+Gather+Max+Mul+Pad+ReduceMax+Relu+Slice+Sub+Sum (246 nodes, 41 initializers)

## 5. 最终摘要

```yaml
task_id: 090
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 246 nodes: Cast+Conv+ConvTranspose+Gather+Max+Mul+Pad+ReduceMax+Relu+Sl. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Cast+Conv+ConvTranspose+Gather+Max+Mul+Pad+ReduceMax+Relu+Slice+Sub+Sum
actual_nodes: 246
```
