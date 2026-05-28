# Task 027 规范

## 1. 核心规则

- 输入/输出尺寸相同（10x10）。
- 背景色为 0（黑色）。输入中仅有 2 个非零像素，颜色分别为 C1 和 C2（如 6=品红和 7=橙色）。
- 两个彩色像素的位置定义了一个结构布局：
  - 顶部区域（row 0 到 row_C1）：用颜色 C1 绘制外框（首行、末行、首列、末列填 C1，内部为 0）。
  - 中部区域（row_C1+1 到 row_C2-1）：用颜色 C2 绘制垂直条带（首列和末列填 C2）。
  - 底部区域（row_C2 到 末行）：用颜色 C2 绘制实心块（整行 C2 间隔排列）。
- 形式化表达：
  ```text
  设 C1 像素位于 (r1, c1)，C2 像素位于 (r2, c2)，且 r1 < r2。
  区域 1 (rows 0..r1): 用 C1 画框
  区域 2 (rows r1+1..r2-1): 用 C2 画两侧竖条
  区域 3 (rows r2..H-1): 用 C2 画满行块
  ```
- arc-gen 样例支持该规则，不同颜色组合均产生相应的三段式布局。

## 2. 关键证据

- train[0]：C1=6 在 (2,2)，C2=7 在 (7,7)。输出：rows 0-2 为 6 框，rows 3-6 为 7 竖条，rows 7-9 为 7 满行。
- train[1]：C1=1 在 (2,6)，C2=4 在 (7,5)。输出布局相同。
- 测试样例：C1=2 在 (2,4)，C2=8 在 (7,6)。同布局。

## 3. 歧义与风险

- 歧义点：两个像素的列位置是否影响输出布局宽度。从样例看，列位置不影响。
- 当前采用的解释：列位置不影响，仅行位置决定区域划分。
- 风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：需要先定位两个彩色像素的行坐标，然后根据坐标划分三个区域分别生成不同模式。这需要全局坐标信息和条件逻辑，不是纯局部卷积能实现的。

## 5. 最终摘要

```yaml
task_id: 027
primitive_types: [pixel_detection, region_split, pattern_generation]
input_shape_rule: 10x10 (可能变化)
output_shape_rule: same as input
formal_rule_short: 两个彩色像素行坐标划分三段，每段生成不同图案（框/竖条/满行）
locality: global
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
main_risk: 列位置可能在某些变体中影响输出
confidence: medium
```
