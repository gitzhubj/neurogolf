# Task 095 规范

## 1. 核心规则

- 输入与输出尺寸相同（固定 9x9）。
- 背景色为 0。输入仅含颜色 5（灰色）的孤立像素。输出包含颜色 1（蓝色）和 5。
- 核心规则：每个颜色 5 的像素扩展为一个 3x3 的"加号块"——以该像素为中心的 3x3 区域内，边框为 1、中心为 5。

```text
for each cell (r,c) where input[r,c] == 5:
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < H and 0 <= nc < W:
                if dr == 0 and dc == 0:
                    output[nr,nc] = 5   // center
                else:
                    output[nr,nc] = 1   // border
```

- 若多个 5-块的 3x3 区域发生重叠，颜色 5 优先于颜色 1（中心覆盖边框）。

## 2. 关键证据

- train[0]: 三个 5 分别在 (1,6),(4,3),(7,1)。每个周围生成 3x3 方块（中心 5、边框 1），无重叠。
- train[1]: 四个 5 分别在 (1,7),(2,3),(5,7),(7,3)。所有 3x3 块不重叠。
- train[2] 与 test[0]: 更多 5-像素，块间距足够大，无重叠或仅有中心-边框重叠（用中心 5 覆盖）。
- 所有样例的 5-像素间距始终 >= 3 行或 3 列，确保 3x3 块互不冲突。
- arc-gen 含 262 个验证样例。

## 3. 歧义与风险

- 歧义点：当两个 5-像素距离 < 3 时，重叠区域颜色规则。当前解释：5 为中心时优先保留，1 为边框且重叠则按 5 优先。风险等级：medium（当前数据无此类冲突）。
- 歧义点：靠近边界的 5 其 3x3 块被截断。当前解释：边界附近只绘制有效区域内的部分。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_kxk_conv
- locality: 1（3x3 邻域）
- single_linear_conv_possible: probably（可用 3x3 Conv 实现膨胀，但双色映射需要额外处理）
- recommended_kernel: 3x3
- nonlinearity_needed: yes（需要区分中心与边框）
- 实现思路：用固定 3x3 权重检测 5-像素位置并膨胀。输出层可用两个 channel 分别生成 1 和 5，再通过 ArgMax 合并。或者直接用固定 mask 的 Conv 做膨胀，配合条件赋值。

## 5. 最终摘要

```yaml
task_id: 095
primitive_types: [dilation, local_pattern, color_mapping]
input_shape_rule: fixed 9x9
output_shape_rule: fixed 9x9
formal_rule_short: each color-5 pixel becomes a 3x3 block with 1-border and 5-center
locality: 1
single_linear_conv_possible: probably
recommended_architecture: single_kxk_conv
memory_priority: single 3x3 Conv layer is very memory efficient; avoid splitting into per-pixel operations
fusion_hint: 3x3 max-pool on color-5 channel produces the border, combine with original 5-channel via weighted sum
main_risk: close-proximity 5-pixels not observed; overlap behavior assumed but untested
confidence: high
```
