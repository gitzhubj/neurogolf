# Task 041 规范

## 1. 核心规则

- 输入输出尺寸相同（10x10 或类似）。
- 背景色为 0 (black)，非零色构成离散的颜色组（每组的颜色相同且唯一）。
- 核心规则：对每一行，对每一种在该行出现的颜色，将该行中该颜色的最左和最右出现位置之间的所有单元格填充为该颜色。
- 形式化：

```text
for each row r:
    for each color c in unique colors in input[r]:
        left = min(col where input[r][col] == c)
        right = max(col where input[r][col] == c)
        if left < right:
            output[r][left ... right] = c
        else:
            output[r][left] = c
    cells without assignment remain as input
```

- 每个颜色组独立处理，颜色之间互不干扰。

## 2. 关键证据

- train 1：绿色(3)在 row 1 的 col 1 和 col 8，输出 row 1 的 col 1–8 全部为 3。row 4 的 col 4 和 col 5 相邻，无需填充。
- train 2：存在 3 种颜色 (1, 4, 及 row 0 和 row 6–9 中的 4)，每种颜色的最左/最右填充分别独立生效。
- train 3：颜色 6 和 8 同时存在于同一行但互不干扰，每色仅在其自身区间内填充。
- arc-gen 全部支持行内最左最右填充规则，不同颜色、不同物体形状均遵循此规则。

## 3. 歧义与风险

- 歧义点：如果某行中某颜色仅出现一次（left==right），是否应保持原样？
  - 当前解释：是，保持原样，不需要填充。
  - 风险等级：low
- 未发现主要歧义。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: global（需要知道每行每种颜色的全局最左最右位置）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：每行需要全局 argmin/argmax 定位每种颜色的左右边界，单层 Conv 无法直接用线性权重实现"填充区间"操作。需要逻辑判断或至少多层 ReLU Conv 来近似。

## 5. 最终摘要

```yaml
task_id: "041"
primitive_types: ["fill_between_per_row_per_color"]
input_shape_rule: "same as output, typically 10x10"
output_shape_rule: "same as input"
formal_rule_short: "per row, per color: fill between leftmost and rightmost occurrence"
locality: "global (per row)"
single_linear_conv_possible: "no"
recommended_architecture: "multi_layer_conv_relu"
main_risk: "单像素颜色是否填充已明确"
confidence: "high"
```
