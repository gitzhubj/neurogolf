# Task 050 规范

## 1. 核心规则

- 输入输出尺寸相同（可变，3x3 到 13x7 等）。
- 背景色为 0，关键颜色：8 (cyan) 和 3 (green)。
- 核心规则：对于每一对同行或同列的两个 8-像素，用颜色 3 填充它们之间的所有单元格。
  - 如果两个 8 在同一行 r，且列分别为 c1 < c2，则 output[r][c1+1 ... c2-1] = 3。
  - 如果两个 8 在同一列 c，且行分别为 r1 < r2，则 output[r1+1 ... r2-1][c] = 3。
  - 如果某行只有一个 8 或某列只有一个 8，则无填充发生。
  - 如果某单元格同时被横向填充和纵向填充覆盖，保持颜色 3（无冲突）。
- 形式化：

```text
for each row r:
    cols = [c for c where input[r][c] == 8]
    if len(cols) >= 2:
        fill output[r][min(cols)+1 : max(cols)] = 3
for each col c:
    rows = [r for r where input[r][c] == 8]
    if len(rows) >= 2:
        fill output[min(rows)+1 : max(rows)][c] = 3
```

- 8 像素本身在输出中保持不变。

## 2. 关键证据

- train 1：同一行有两个 8，之间填充为 3。
- train 2：两个 8 在同一列，垂直填充为 3。
- train 3：多个行各有 8 对，各自行内横向填充 3。此外还有列方向上的 8 对，垂直填充 3。
- train 5（3x3 单 8）：无配对，输出与输入相同（无填充）。
- arc-gen 全部支持此规则：任何同行或同列的 8-对都会产生 3-填充线段。

## 3. 歧义与风险

- 歧义点：如果某行有 3 个以上 8 像素，是否所有相邻对之间都要填充？
  - 当前解释：不，仅填充最左和最右之间的区间（一整段），而不是分段填充。
  - 风险等级：low
- 歧义点：横向和纵向填充在同一单元格重叠时，颜色优先级？
  - 当前解释：两者均为 3，重叠无冲突。
  - 风险等级：low

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: global（需要每行/每列的全局最值位置）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：需要对每行/每列定位 8-像素并填充区间，类似 task 041 但仅在 8-色上操作且方向为行+列。需要全局 min/max per row/column，单 Conv 层无法直接完成。

## 5. 最终摘要

```yaml
task_id: "050"
primitive_types: ["fill_between_paired_pixels", "per_row_col_interval"]
input_shape_rule: "same as output, variable size"
output_shape_rule: "same as input"
formal_rule_short: "for each row/col with 2+ 8-pixels, fill between leftmost and rightmost with 3"
locality: "global (per row/col)"
single_linear_conv_possible: "no"
recommended_architecture: "multi_layer_conv_relu"
main_risk: "行内多 8 时仅填充最外区间（非分段）已确认"
confidence: "high"
```
