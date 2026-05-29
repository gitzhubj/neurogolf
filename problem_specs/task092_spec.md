# Task 092 规范

## 1. 核心规则

- 输入与输出尺寸相同（可变大小，如 30x20、20x10）。
- 背景色为 0。输入包含多种孤立颜色像素（每个颜色至少 2 个像素）。
- 核心规则：对于每种颜色，连接同行或同列的所有该色像素——在行方向上填充最左到最右之间的所有单元格，在列方向上填充最上到最下之间的所有单元格。原始像素保持不变。

```text
output = copy of input
for each color c present:
    for each row r:
        cols = all c where input[r,col] == c
        if len(cols) >= 2:
            fill output[r, min(cols):max(cols)+1] = c
    for each col col:
        rows = all r where input[r,col] == c
        if len(rows) >= 2:
            fill output[min(rows):max(rows)+1, col] = c
```

- 当横向填充与纵向填充在不同颜色间重叠时，纵向优先（即最后赋值的颜色获胜）。

## 2. 关键证据

- train[0]: color 2 像素 (2,6) 和 (13,6) → col 6 纵向填充 rows 2-13；color 3 像素 (6,3) 和 (6,11) → row 6 横向填充 cols 3-11。交点 (6,6) 显示 2（纵向优先）。
- train[0]: color 5 像素 (20,2) 和 (20,7) → row 20 横向填充 cols 2-7；color 6 像素 (18,4) 和 (27,4) → col 4 纵向填充 rows 18-27。交点 (20,4) 显示 6（纵向优先）。
- train[1]: 5 种颜色各自只有 2 个像素，均在同一行或同一列。
- 所有样例在填充时跨其他颜色像素覆盖，最终优先规则一致。
- arc-gen 含 262 个验证样例，均支持该连接规则。

## 3. 歧义与风险

- 歧义点：若某颜色在多个行或列各有配对。当前解释：所有行和所有列独立处理。风险等级：low。
- 歧义点：纵向/横向优先级在不同颜色间是否固定为纵向获胜。当前解释：是，纵向填充在横向之后执行（或其他等价机制）。风险等级：medium。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: global（需每行/每列的全局最值）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 类似于 task 050 的线填充，但扩展为多色且行+列方向均需填充。需按颜色通道分别计算每行/列的最值位置然后 broadcast 填充。纵向优先的冲突处理可通过执行顺序实现。

## 5. 最终摘要

```yaml
task_id: 092
primitive_types: [line_fill, per_row_col_interval, multicolor_connect]
input_shape_rule: variable size
output_shape_rule: same as input
formal_rule_short: for each color, draw horizontal lines between same-row pairs and vertical lines between same-col pairs; vertical wins on overlap
locality: global
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
memory_priority: compute min/max per row/col per color with Reduce, then broadcast fill; avoid per-pixel iteration
fusion_hint: vertical and horizontal fills can share the color-detection pass
main_risk: vertical override priority assumption may not hold for all color combinations
confidence: high
```
