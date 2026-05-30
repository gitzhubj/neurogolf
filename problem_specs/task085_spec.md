# Task 085 规范

## 1. 核心规则

- 输入/输出尺寸相同。
- 输入中包含若干水平矩形块（高度精确为 3 行），每块由单一颜色填充（如 4, 1, 7, 8）。
- 核心变换：对每个 3 行高的矩形块，保持上下两行不变，将中间行改为交替模式（每隔一列置零）。
- 交替模式：中间行从块起始列开始，col, col+1, col+2,... 对应 `[color, 0, color, 0, ...]` 或 `[0, color, 0, color, ...]`。
- 具体相位（从 color 开始还是从 0 开始）取决于块在整个行中的位置（左起首个保留颜色）。

## 2. 关键证据

- train 0：8×30。颜色 4 的块（row 1-3, col 0-28）→ row 2 交替 4/0。颜色 8 的块（row 5-7, col 12-24）→ row 6 交替 8/0。
- train 1：8×20。颜色 1 的块（row 1-3, col 0-8）→ row 2 交替。颜色 7 的块（row 5-7, col 7-16）→ row 6 交替。
- test 0：11×20。颜色 5（row 1-3）、4（row 5-7）、8（row 8-10）三块分别交替化中间行。
- 所有样例中只有 3 行高的块受到交替化变换。

## 3. 歧义与风险

- 歧义点：交替模式的起始列是否总是以块颜色开头。当前解释：以块颜色开头（奇数位置为 0）。风险等级：low。
- 歧义点：高度不为 3 的块如何处理。当前解释：不变。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 20 nodes: Cast+Conv+Floor+Mul+Pad+ReduceSum+Slice+Sub+Sum. Study baseline for optimal op sequence.

Baseline 实际架构: Cast+Conv+Floor+Mul+Pad+ReduceSum+Slice+Sub+Sum (20 nodes, 14 initializers)

## 5. 最终摘要

```yaml
task_id: 085
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 20 nodes: Cast+Conv+Floor+Mul+Pad+ReduceSum+Slice+Sub+Sum. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Cast+Conv+Floor+Mul+Pad+ReduceSum+Slice+Sub+Sum
actual_nodes: 20
```
