# Task 098 规范

## 1. 核心规则

- 输入与输出尺寸相同。背景色为 0。
- 输入包含多个实心矩形块（颜色为 8、3、6、7、5、4、2 等）。输出只保留每个矩形的边框（外轮廓），内部填充为 0。
- 核心规则：对于每个非零像素，如果它在 4-方向上（上下左右）都被同色像素包围（即位于矩形内部），则将其设为 0。否则保留。

```text
for each non-zero cell (r,c) with color k:
    left   = input[r, c-1] if c > 0 else different
    right  = input[r, c+1] if c < W-1 else different
    top    = input[r-1, c] if r > 0 else different
    bottom = input[r+1, c] if r < H-1 else different
    if left == k and right == k and top == k and bottom == k:
        output[r,c] = 0    // interior of rectangle
    else:
        output[r,c] = k    // border or isolated
```

- 不同颜色的矩形独立处理。背景 0 不变。

## 2. 关键证据

- train[0]: 8-矩形 (1:3,1:4) 内部 (2,2)-(2,3) 被清空，边框保留。3-矩形 (3:7,6:12) 内部被清空。6-矩形和 7-矩形同理。
- train[1]: 2-矩形 (1:4,1:5) 内部被清空，边框保留。
- train[2]: 5-矩形和 4-矩形分别被"空心化"。
- test[0]: 多个矩形（8、6、4、1、3）全部正确空心化。
- 所有矩形均为轴对齐实心形状，无空洞。边框保持原色。

## 3. 歧义与风险

- 歧义点：L 形或非矩形形状的处理。当前解释：规则仅对矩形内部有效；非矩形形状的"内部"可能只有部分被清空。风险等级：medium（所有样例均为标准矩形）。
- 歧义点：边界像素判定（4 方向需全部为同色）。当前解释：只要 4 方向中有一方向出界或颜色不同，即为边框，保留。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_kxk_conv
- locality: 1（3x3 足以检查四邻域）
- single_linear_conv_possible: probably
- recommended_kernel: 3x3
- nonlinearity_needed: yes
- 实现：对每个颜色通道用 3x3 Conv，kernel 设为检测四方向是否全为同色（如 [[0,1,0],[1,0,1],[0,1,0]] 模式）。当邻域和 >= 4 时判定为内部（自身+4 个同色邻居），置 0。

## 5. 最终摘要

```yaml
task_id: 098
primitive_types: [hollow_out, rectangle_interior_removal, morphological_operation]
input_shape_rule: variable size
output_shape_rule: same as input
formal_rule_short: set interior pixels (surrounded by same color on all 4 sides) to 0, keeping borders
locality: 1
single_linear_conv_possible: probably
recommended_architecture: single_kxk_conv
memory_priority: single 3x3 Conv per color channel; very efficient
fusion_hint: a fixed kernel detecting full 4-neighbor coverage can be applied to all color channels simultaneously
main_risk: non-rectangular shapes may produce unexpected results
confidence: high
```
