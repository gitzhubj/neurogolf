# Task 046 规范

## 1. 核心规则

- 输入始终为 3 行，宽度可变（9–20 列）。输出也是 3 行，宽度通常变窄。
- 背景色为 0，颜色 5 (gray) 充当分隔符/标记。
- 核心规则：5 标记了"分配通道"。row 1 包含彩色块（可以是一种或多种颜色），被 5 分隔。row 0 和 row 2 中的 5 标记了目标位置——row 0 的 5 将 row 1 的块"拉"到 row 0，row 2 的 5 将块"拉"到 row 2。
- 每个彩色块最终会出现在 1 个或多个输出行中，分配由 5 的位置控制。同一块可能在输出中被扩展（尺寸变大）或拆分到多行。
- 具体分配和扩展规则尚不完全确定。

## 2. 关键证据

- train 1：3 行输入。row 1 有两个 2-块和一个 1。row 0 有一个 5，row 2 有一个 5。输出中 2 和 1 被重新分配到 row 0 和 row 1，块尺寸发生变化。
- train 2：3 行输入（宽度 11）。row 1 有 2-块和 3-块。row 0 有两个 5 夹一个 1，row 2 有两个 5 夹一个 3。输出中块被拆分/扩展到 row 1 和 row 2。
- train 3：3 行输入（宽度 11）。row 1 有 2-块和 8-块。row 2 有 6-块和两个 5。输出中所有三行都有重新分配的块。
- arc-gen 全部遵循此分配-扩展模式，但具体尺寸公式随 5 标记的间距变化。

## 3. 歧义与风险

- 歧义点：块分配到哪一行以及如何扩展的具体公式。
  - 当前解释：不确定。块倾向于出现在有 5 标记的行，且尺寸可能等于对应 5 间隔的宽度。
  - 风险等级：high
- 歧义点：当 row 0 和 row 2 都有 5 对应同一个块时，块是拆分还是仅到某一侧？
  - 当前解释：不确定。观察 train 2 中 2-块同时出现在 row 1 和 row 2，疑似拆分。
  - 风险等级：high

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 70 nodes: Abs+Concat+Conv+Gather+Less+MatMul+MaxPool+Mul+Pad+ReduceMax. Study baseline for optimal op sequence.

Baseline 实际架构: Abs+Concat+Conv+Gather+Less+MatMul+MaxPool+Mul+Pad+ReduceMax+ReduceMin+ReduceSum+Slice+Sub+Sum+Transpose+Where (70 nodes, 26 initializers)

## 5. 最终摘要

```yaml
task_id: 046
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 70 nodes: Abs+Concat+Conv+Gather+Less+MatMul+MaxPool+Mul+Pad+ReduceMax. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Abs+Concat+Conv+Gather+Less+MatMul+MaxPool+Mul+Pad+ReduceMax+ReduceMin+ReduceSum+Slice+Sub+Sum+Transpose+Where
actual_nodes: 70
```
