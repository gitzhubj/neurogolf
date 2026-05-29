# Task 033 规范

## 1. 核心规则

- 输入与输出尺寸相同，均为 17x17。
- 关键颜色：0（背景），L（分界线颜色，如 8, 2, 1, 3），以及其他形状颜色 S（如 2, 1, 3）。
- 核心规则：输入被 L 颜色的十字线（第 5 行、第 11 行为全 L；第 5 列、第 11 列为全 L）划分为 9 个 5x5 单元格。每个单元格中可能有 S 颜色的形状。输出中，每个单元格中的形状被沿 L 线"反射"到空单元格中——即形状被复制到关于 L 线对称的位置，但反射副本使用 L 颜色，原形状保留 S 颜色。
- 形式化描述：对于坐标为 (r, c) 的形状像素（颜色为 S），找到其关于最近 L 线的镜像位置 (r', c')。若输出对应单元格为空，则填充该镜像形状，颜色为 L。

## 2. 关键证据

- Train 0：L=8，S=2。输入有 2 形在左上、中右、左下格。输出在这三格的镜面位置出现 8 形。
- Train 1：L=2，S=1。输入有 1 形（3x3 块）。输出在镜面位置出现 2 形。
- Train 2：L=1，S=3。输入有 3 形（对角斜线）。输出镜面位置出现 1 形。
- 所有 train 样例均为 17x17 入出，规则一致。
- arc-gen 样例支持该反射规则。

## 3. 歧义与风险

- 歧义点：反射方向的具体映射（哪个格反射到哪个格）。
- 当前采用的解释：每个有形状的格关于中心（水平和垂直 L 线的交点）反射到对角格。
- 风险等级：`medium`

## 4. NeuroGolf 架构提示

- `recommended_architecture`: `object_logic_required`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_single_conv`
- `nonlinearity_needed`: `yes`
- 原因：需要检测 L 线的位置、识别各单元格中的形状、计算镜面位置并复制形状。涉及分区检测和几何变换，远超单层 Conv 能力。

## 5. 最终摘要

```yaml
task_id: "033"
primitive_types: [reflection, symmetry, grid_partition]
input_shape_rule: 17x17
output_shape_rule: 17x17
formal_rule_short: 形状沿 L 色分界线反射到对角空单元格，反射副本用 L 色
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 反射映射方向不完全确定
confidence: medium
```
