# Task 093 规范

## 1. 核心规则

- 输入与输出尺寸相同。背景色为 0。
- 输入包含一个颜色 5（灰色）的横条/竖条区域，以及分散在周围的少量其他颜色像素（如 2、3、1、4 等）。
- 核心规则：将分散的非-5 颜色像素"合并"到 5 区域中。对于每个非-5 像素，在 5 区域的边缘向该像素方向扩展 1 步（填上 5）；如果非-5 像素恰好在这一步位置，则该像素变为 5。所有非-5 像素本身最终被移除（变为 0 或变为 5）。

```text
output = copy of input
for each non-5, non-0 pixel at (r,c):
    if pixel is adjacent (4-dir) to any 5-cell:
        output[r,c] = 5   // 合并进区域
    else:
        // 向 5 区域边缘投影：在 5 区域边缘对应方向填一个 5
        find nearest 5-cell on same row/col and fill the cell between
        output[r,c] = 0   // 移除原像素
```

- 5 区域的原有像素保持不变。区域仅向外扩展，不会向内收缩。

## 2. 关键证据

- train[0]: 水平 5-条（rows 5-8, 全宽）。上方 2-像素 (0,8),(2,2),(3,10) 在 row 4 投影出 5；下方 2-像素在 row 9 投影出 5。所有 2 最终消失。
- train[1]: 垂直 5-条（cols 4-8, 全高）。相邻 3-像素 (1,9) 和 (2,3) 直接变为 5；距离 2 步的 (6,10) 也变为 5（中间格 (6,9) 被填补）。远处 3-像素被移除。
- train[2]: 水平 5-条（rows 7-8, 全宽）。远处 1-像素被移除，row 6 和 row 9 上投影出新的 5。
- 非-5 像素被移除后，输出只包含 0 和 5。
- arc-gen 含 261 个样例，均支持该合并规则。

## 3. 歧义与风险

- 歧义点：扩展距离上限不明确。部分样例扩展 1 步，部分可扩展 2 步。当前解释：扩展至多 2 步（先填补中间格，再替换非-5 像素）。风险等级：medium。
- 歧义点：横向条和纵向条情况下扩展逻辑是否对称。当前解释：对称（均为向非-5 像素方向扩展）。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required（需要定位 5-区域边界并计算方向扩展）
- locality: k（依赖局部邻域判定是否邻近 5-区域）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 可用形态学膨胀操作模拟扩展：对 5 区域做 1-2 步 dilation，然后与原 5 区域取并集。非-5 像素被移除等同于只保留 5 通道。

## 5. 最终摘要

```yaml
task_id: 093
primitive_types: [region_growth, projection, morphological_dilation]
input_shape_rule: variable size
output_shape_rule: same as input
formal_rule_short: expand color-5 region outward toward scattered non-5 pixels, converting them to 5 or removing them
locality: k (local neighborhood of 5-region edge)
single_linear_conv_possible: no
recommended_architecture: object_logic_required
memory_priority: use repeated 3x3 max-pool (dilation) on color-5 channel; avoid per-pixel path finding
fusion_hint: successive dilations can be unrolled into a single larger kernel if step count fixed
main_risk: expansion step count may vary (1 or 2) depending on input; arc-gen may disambiguate
confidence: medium
```
