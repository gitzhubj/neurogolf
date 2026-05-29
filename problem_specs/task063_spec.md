# Task 063 规范

## 1. 核心规则

- 输入/输出尺寸相同(各样例尺寸不同:12x12,12x12,10x10,14x14)。
- 输入有三种值:背景色(出现最多的非零色)、墙色(第二种非零色)、0(空洞)。
- 核心规则:将 0 区域中**被墙色完全包围**(无法通过四连通路径到达网格边缘)的子区域填充为 3(绿色);连通到边缘的 0 保持 0。

```text
background = majority_nonzero_color
wall = the_other_nonzero_color
for every 0-cell:
    if flood_fill(cell, avoiding wall) reaches grid_edge:
        output = 0
    else:
        output = 3
other cells (background, wall) unchanged
```

- 背景色和墙色在不同样例中互换(背景色可为 2 或 8,墙色相反)。

## 2. 关键证据

- train[0]:背景 2(红),墙 8(浅蓝)。右下有一块被 8 包围的 0 区域→填充为 3;左上与边缘连通的 0 保持不变。
- train[1]:背景 8,墙 2。中间的 0 空腔被 2 包围→填充为 3。
- train[2]:背景 8,墙 2。左下的 0 区域被 2 包围→填充为 3。
- test[0]:背景 8,墙 2。多处被 2 包围的 0 区域→全部填充为 3。
- arc-gen 有 262 个样例,全部支持 flood-fill 解释。

## 3. 歧义与风险

- 四连通 vs 八连通:当前使用四连通(上下左右),所有样例一致。风险:low。
- 背景/墙的区分:出现最多的非零色为背景,另一种为墙。验证所有样例均成立。风险:low。
- 如果 0 区域通过狭窄通道连通到边缘:只有完全封闭的才填充,狭窄通道也算连通到边缘。风险:low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global(需要 flood fill 全图连通性)
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 经典 flood-fill/连通组件标记问题。单层 Conv 无法表达全局连通性检测。
- memory_priority: 建议通过迭代形态学膨胀或连通组件标记实现,避免存储每个像素的 flood fill 中间状态。
- fusion_hint: 如果使用迭代膨胀(从边缘 0 向内传播标记),可将多次迭代融合进循环实现,只需 1 个 mask 张量。

## 5. 最终摘要

```yaml
task_id: 063
primitive_types: [flood_fill, connectivity, enclosed_region, hole_filling]
input_shape_rule: varies (10-14)x(10-14)
output_shape_rule: same as input
formal_rule_short: fill 0-cells enclosed by wall-color (cannot reach edge via 4-neighbor) with color 3
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 4- vs 8-connectivity, background/wall distinction
confidence: high
```
