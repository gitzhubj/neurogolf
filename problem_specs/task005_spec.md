# Task 005 规范

## 1. 核心规则

- 输入固定 3x7，输出固定 3x3。
- 输入第 3 列（0-indexed，col=3）全为 5，作为左右分隔符。左半（cols 0..2）和右半（cols 4..6）各为一个 3x3 的二值图案（仅含 0 和 1）。
- 核心变换：对左右两个 3x3 图案做逐像素逻辑 AND。输出 3x3，仅当左右对应位置均为 1 时输出 2，否则输出 0。
- 输出颜色集为 {0, 2}。颜色 2 是新增输出色（输入中未出现）。

```text
for r in 0..2, c in 0..2:
    left = input[r][c]
    right = input[r][c + 4]
    output[r][c] = 2 if left == 1 and right == 1 else 0
```

## 2. 关键证据

- train 0：左 [[1,0,0],[0,1,0],[1,0,0]]，右 [[0,1,0],[1,1,1],[0,0,0]]。仅 (1,1) 位置左右均为 1，输出仅中间格为 2，其余为 0。
- train 1：左 [[1,1,0],[0,0,1],[1,1,0]]，右 [[0,1,0],[1,1,1],[0,1,0]]。AND 结果在 (0,1)、(1,2)、(2,1) 为 2，输出与之完全吻合。
- train 2：左 [[0,0,1],[1,1,0],[0,1,1]]，右 [[0,0,0],[1,0,1],[1,0,1]]。AND 仅在 (1,0) 和 (2,2) 为 2，排除 OR/XOR 等替代解释。
- test：左 [[1,0,1],[0,1,0],[1,0,1]]，右 [[1,0,1],[1,0,1],[0,1,0]]。AND 结果为 (0,0)、(0,2)、(2,1) 有 2，无左右同时为 1 处为 0。
- arc-gen 全面覆盖各种二值组合，均支持 AND 规则。

## 3. 歧义与风险

- 歧义点：若左右图案包含 0 和 1 之外的颜色如何处理。当前解释：所有可见输入左右仅含 0 和 1，未观测到其他颜色。风险等级：medium。
- 歧义点：分隔列的值始终为 5，若改用其他值是否仍为分隔符。当前解释：固定 col=3 为分隔位置，颜色 5 仅为标记。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_1x1_conv 或固定坐标路由（左右半部 AND 可用 fixed-weight 1x1 Conv 实现）
- locality: 9（每个输出格依赖两个固定偏移的输入格：同 col 和 col+4）
- single_linear_conv_possible: probably（如果允许以固定稀疏权重选取左右对应位置并相乘，1x1 Conv 可近似实现，但严格的 AND 非线性（1 AND 1 = 2 而非 1）可能需要非线性映射）
- recommended_kernel: 1x1（颜色映射层面）
- nonlinearity_needed: yes（AND 运算需要非线性；且输出颜色 2 不是简单的线性组合）

极简颜色映射：

```text
output_channel_2 = input_channel_1_left * input_channel_1_right  (AND 逻辑)
output_channel_0 = 1 - output_channel_2                         (背景)
```

## 5. 最终摘要

```yaml
task_id: 005
primitive_types: [pattern_split, logical_AND, pixelwise_color_mapping]
input_shape_rule: fixed 3x7 with col 3 = 5 as separator
output_shape_rule: fixed 3x3
formal_rule_short: split input at col 3, AND left 3x3 with right 3x3, output 2 for AND=1 and 0 otherwise
locality: 9
single_linear_conv_possible: probably (fixed sparse linear + nonlinear)
recommended_architecture: single_1x1_conv (with post-Conv nonlinear map)
main_risk: output color 2 mapping might require nonlinear activation
confidence: high
```
