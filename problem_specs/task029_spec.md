# Task 029 规范

## 1. 核心规则

- 输入/输出尺寸相同（10x10）。
- 背景色为 0（黑色）。输入中仅有 2 个非零像素，颜色分别为 C1 和 C2（如 6=品红和 7=橙色，或 1=蓝和 4=黄）。
- 与 task027 相同的模式：两个彩色像素的行坐标 r1, r2（r1 < r2）将输出分为三个区域：
  - 区域 1 (rows 0..r1)：用 C1 绘制外框（首行满 C1，两侧竖线 C1）。
  - 区域 2 (rows r1+1..r2-1)：用 C2 绘制两侧竖条。
  - 区域 3 (rows r2..H-1)：用 C2 绘制间隔满行。
- 该任务与 task027 属于同一模板的不同实例（不同颜色组合）。
- arc-gen 样例支持该规则。

## 2. 关键证据

- train[0] 和 train[1] 均显示两像素输入 -> 三段式框架输出。
- 与 task027 的结构完全一致，仅颜色不同。
- 测试样例同样为两像素输入 -> 框架输出。

## 3. 歧义与风险

- 歧义点：与 task027 的区别是什么（可能仅颜色不同）。
- 当前采用的解释：与 task027 相同规则，仅颜色不同。
- 风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：与 task027 相同——需要定位于像素坐标并生成条件性区域图案。

## 5. 最终摘要

```yaml
task_id: 029
primitive_types: [pixel_detection, region_split, pattern_generation]
input_shape_rule: 10x10 (可能变化)
output_shape_rule: same as input
formal_rule_short: 同 task027——两像素行坐标划分三段，生成框/竖条/满行图案
locality: global
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
main_risk: 可能存在不同于 task027 的变体
confidence: medium
```
