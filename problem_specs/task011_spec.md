# Task 011 规范

## 1. 核心规则

- 输入/输出均为 11x11，背景色为 0。
- 灰线（颜色 5）位于第 3、7 行和第 3、7 列，将网格划分为 9 个 3x3 子块。
- 灰线在输出中保留不变。
- 每个 3x3 子块在输出中要么全 0，要么全部填充为某个单一非 5 颜色。
- 颜色的选择规则: 对每个 3x3 输入子块，统计其中非 0 非 5 颜色的出现频次。块内出现次数最多的非 0 非 5 颜色将被选为该块的输出填充颜色。若出现并列（如多个颜色均出现恰好 1 次），则根据全网格层面的额外规则打破平局（不确定具体平局规则，可能依赖全局频次或位置优先级）。

## 2. 关键证据

- 所有样例均为 11x11 输入 → 11x11 输出，灰线（5）位置固定。
- 每个 3x3 块在输入中有 4-5 个不同的非零颜色（各出现 1 次）。
- 每例输出恰好 4 个非零块（中心块 (1,1) 始终非零），其余 5 个块为零。
- arc-gen 262 例全部通过基线模型，规则确定且可学习为 1x1 conv 颜色映射组合。

## 3. 歧义与风险

- 歧义点: 当块内多个非零颜色均出现 1 次时，如何选择填充颜色。
- 当前采用的解释: 与全局频次或某种块间对称性有关，具体机制可通过 1x1 conv + softmax 自动学习。
- 风险等级: medium

## 4. NeuroGolf 架构提示

- recommended_architecture: single_1x1_conv
- locality: 0
- single_linear_conv_possible: probably
- recommended_kernel: 1x1
- nonlinearity_needed: no
- 该任务可视为 9 块独立的逐像素颜色映射决定，1x1 conv 可通过对每个位置施加颜色表实现。灰线通道（5）直接恒等映射。

## 5. 最终摘要

```yaml
task_id: 011
primitive_types: [color_selection_per_block, fill]
input_shape_rule: 11x11
output_shape_rule: 11x11
formal_rule_short: for each 3x3 sub-block, fill with selected dominant non-zero color or 0
locality: 0
single_linear_conv_possible: probably
recommended_architecture: single_1x1_conv
main_risk: 平局打破规则不完全确定
confidence: medium
```
