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

- recommended_architecture: single_1x1_conv（区域级颜色查表，基于坐标位置决定填充色）
- locality: 0
- single_linear_conv_possible: probably（1x1 Conv 可学习每个位置的投票权重）
- recommended_kernel: 1x1
- nonlinearity_needed: no（纯线性加权投票 + argmax，但需要 softmax/argmax）

## 5. 最终摘要

```yaml
task_id: 059
primitive_types: [region_voting, majority_color, block_fill]
input_shape_rule: fixed 11x11
output_shape_rule: fixed 11x11
formal_rule_short: for each 3x3 sub-region bounded by gray lines, fill with the dominant non-zero non-gray color or 0
locality: 0
single_linear_conv_possible: probably
recommended_architecture: single_1x1_conv
main_risk: tie-breaking rule for multi-color regions uncertain
confidence: medium
```
