# Task 060 规范

## 1. 核心规则

- 输入/输出均为 5×11。
- 输入中在某一行（如 row 1 或 row 3）的最左列和最右列各有一个非零颜色（形成一对颜色端点）。
- 核心变换：对每一对有颜色端点的行，从左端点的颜色开始，填充该行左半部分（col 0 到 col 4）；在正中间列（col 5）填充颜色 5（灰色分隔符）；从 col 6 到 col 10 填充右端点的颜色。
- 如果某行的端点是不同颜色对（如 train[0] row1 有 1 和 2，test[0] 还有多行），每行独立处理。
- 没有颜色端点的行保持全零。
- 多对颜色可以出现在不同行中（如 test 有两行有颜色对）。

```text
for each row r:
    left_color = leftmost non-zero cell in row r
    right_color = rightmost non-zero cell in row r
    if left_color and right_color exist:
        for each col c:
            if c < mid: output[r][c] = left_color
            elif c == mid: output[r][c] = 5
            else: output[r][c] = right_color
```

## 2. 关键证据

- train 0：row 1 有左端点颜色 1（col 0）和右端点颜色 2（col 10）。输出 row 1：col 0-4 为 1，col 5 为 5，col 6-10 为 2。
- train 1：row 3 有左端点颜色 3 和右端点颜色 7。输出 row 3 同理填充。
- test 0：有两对端点（row 1 有 4 和 8，row 3/4 有 6 和 9），每行独立填充，中线 col 5 为灰色 5。

## 3. 歧义与风险

- 歧义点：若同一行有多个非零颜色（非仅左右端点）。当前解释：取最左和最右的非零格颜色作为端点。风险等级：low。
- 歧义点：中线颜色始终为 5。当前解释：5 是固定的分隔符，不依赖端点颜色。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_1x1_conv（每行独立颜色映射，依赖行内左右端点位置）
- locality: 1（需要同行内跨列查找左右端点）
- single_linear_conv_possible: probably（可用 1x1 Conv 处理，因为每个位置的输出仅依赖该位置的输入颜色和列索引）
- recommended_kernel: 1x1
- nonlinearity_needed: no
- memory_priority: 1×1 Conv 可直接实现：对每个 (row, col)，若该行有左右颜色且 col 在相应范围内，则输出对应颜色。

## 5. 最终摘要

```yaml
task_id: 060
primitive_types: [horizontal_fill, color_pair_expansion, row_wise]
input_shape_rule: fixed 5x11
output_shape_rule: fixed 5x11
formal_rule_short: for each row with left/right color endpoints, fill left half with left color, mid with 5, right half with right color
locality: 1
single_linear_conv_possible: probably
recommended_architecture: single_1x1_conv
main_risk: none
confidence: high
```
