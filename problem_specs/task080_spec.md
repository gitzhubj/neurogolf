# Task 080 规范

## 1. 核心规则

- 输入/输出尺寸相同(可变: 24x24, 27x27, 29x29)，背景色为 0。
- 输入具有网格状结构：一种"结构色"(S)形成水平和垂直的线条，将网格划分为多个矩形单元格。
- 一些单元格内已有"填充色"(F)像素，另一些单元格为空(全 0)。
- 变换规则：将空单元格内所有背景(0)像素填充为填充色(F)。结构色(S)和其他已有颜色保持不变。

```text
# Identify the structural color S (most frequent non-zero color forming grid lines)
# Identify the fill color F (secondary non-zero color appearing inside cells)
# For each empty cell in the grid (entirely background 0 within S-bounded region):
#   fill all 0s in that cell with F
```

- 结构色 S 因样例而异: train[0] 为 8(天蓝), train[1] 为 3(绿), train[2] 为 8(天蓝)。
- 填充色 F 也因样例而异: train[0] 为 3(绿), train[1] 为 6(品红), train[2] 为 4(黄)。

## 2. 关键证据

- train[0]: 24x24。结构色 8 形成网格。填充色 3 填满空单元格。0→3(48px)。
- train[1]: 27x27。结构色 3 形成网格。填充色 6 填满空单元格。0→6(54px)。
- train[2]: 27x27。结构色 8 形成网格。填充色 4 填满空单元格。0→4(99px)。
- 所有样例中，已包含非零像素的单元格无变化。仅全 0 单元格被填充。
- arc-gen 含 262 个额外样例支持该规则。

## 3. 歧义与风险

- 如何自动确定结构色 S？通常是出现频率最高且形成连续行列的非零颜色。风险: `low`。
- 如何确定填充色 F？通常是频率第二高的非零颜色。风险: `low`。
- 单元格边界如何确定？由结构色 S 的连续行列划分。风险: `low`。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global (需感知网格结构)
- single_linear_conv_possible: no
- recommended_kernel: larger
- nonlinearity_needed: yes
- 核心挑战是检测出结构色 S 形成的网格线，从而定位"单元格"。
- 可能实现：(1) 统计每行/每列中 S 的出现确定网格线位置；(2) 对每个由 S 围成的矩形区域的内部置为 F。
- 可考虑用大核 Conv + row/col pooling 检测网格线的连续性。用 1x1 Conv 检测 S 后做行列方向上的 ReduceMax 来定位完整网格线。
- 填充操作可用固定 mask 实现(每个单元格位置预计算)，避免逐单元格切片。

## 5. 最终摘要

```yaml
task_id: 080
primitive_types: [grid_completion, cell_filling, structural_color_fill]
input_shape_rule: variable (24x24 to 29x29)
output_shape_rule: same as input
formal_rule_short: Fill empty grid cells (bounded by structural color S) with secondary fill color F
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
memory_priority: Use row/col pooling to detect grid lines; use precomputed fill mask per cell
fusion_hint: Detect structural grid lines via ReduceMax on Conv output; fill with static mask
main_risk: Identifying which color is structural vs fill automatically
confidence: high
```
