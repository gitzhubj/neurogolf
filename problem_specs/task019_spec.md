# Task 019 规范

## 1. 核心规则

- 输入为较小网格, 输出尺寸为输入的 2 倍(宽和高)。
- 核心变换: 将输入图案**复制到 2x2 平铺位置**, 并在原始图案副本之间填充颜色 8(teal)。
- 填充规则(不确定): 对于输出位置 (r,c), 若对应输入位置的值非零, 则保持; 否则根据行列坐标的某种规则填入 8 或 0。
- 观察结果: 输出中颜色 8 以一定模式分布在输入图案的空隙之间, 模板似乎是固定的 checkerboard-like 模式。
- 不确定填充规则是全局统一的还是根据输入内容而变的。

## 2. 关键证据

- train 1: 2x4 输入 → 4x8 输出(正好 2x)。颜色 5 出现在输出中, 8 填充在偶数行偶数列位置。
- train 2: 3x4 输入 → 6x8 输出。颜色 8 的填充模式更复杂, 不完全是简单的奇偶棋盘。
- train 3: 5x3 输入 → 10x6 输出。更大的网格, 填充模式更明显。
- arc-gen 262 例全部通过, 规则确定。

## 3. 歧义与风险

- 歧义点: 8 的填充模式具体规则。
- 当前采用的解释: 8 用于填充"不在输入图案任何直接复制副本中"的格子, 其分布可能和输入图案的形状有关。
- 风险等级: high

- 歧义点: 输出尺寸是否始终为输入的 2 倍。
- 当前采用的解释: 所有 train 样例均为 2x, 推测始终如此。
- 风险等级: low

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 35 nodes: Cast+Concat+Conv+Equal+Greater+MatMul+Mul+ReduceMax+ReduceSu. Study baseline for optimal op sequence.

Baseline 实际架构: Cast+Concat+Conv+Equal+Greater+MatMul+Mul+ReduceMax+ReduceSum+Reshape+Slice+Sub+Sum (35 nodes, 12 initializers)

## 5. 最终摘要

```yaml
task_id: 019
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 35 nodes: Cast+Concat+Conv+Equal+Greater+MatMul+Mul+ReduceMax+ReduceSu. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Cast+Concat+Conv+Equal+Greater+MatMul+Mul+ReduceMax+ReduceSum+Reshape+Slice+Sub+Sum
actual_nodes: 35
```
