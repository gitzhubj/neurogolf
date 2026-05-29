# Task 034 规范

## 1. 核心规则

- 输入与输出尺寸相同，均为 9x9。
- 关键颜色：0（背景），2（"锚点"/镜面标记），以及一种其他颜色 C ∈ {3,4,5,6,7,8,9,1}（"传播色"）。
- 核心规则：输入含一个 2x2 块，其中至少有一个格子值为 2。找到该 2x2 块中非 0 且非 2 的颜色 C，然后从该 2x2 块向外沿 45 度对角线方向画出宽度为 3 的"对角线带"（颜色为 C）。
- 形式化表达：设 2x2 块的左上角为 (r, c)，块内颜色 C 的位置决定了传播方向。
  - 若 C 在 2x2 块的"左上"或"右下"位置，沿主对角线方向（\）传播。
  - 若 C 在"右上"或"左下"位置，沿反对角线方向（/）传播。
- 传播模式：每个传播格子在两个对角方向上各生成一条由 3 个相同颜色 C 像素组成的短线（共 6 个像素），这些短线在 45 度方向上排列。

## 2. 关键证据

- Train 0：2x2 块为 [4,2]/[4,4]，C=4 在左上和左下，输出含 4 的两条对角带。
- Train 1：2x2 块为 [3,3]/[3,2]，C=3 在左上和右上，输出含 3 的对角带。
- Train 2：2x2 块为 [6,2]/[2,6]，C=6 在左上和右下，输出含 6 的对角带。
- Train 3：2x2 块为 [2,2]/[2,7]，C=7 在右下，输出含 7 的对角带。
- 所有 4 个 train 样例中输出均为 9x9，传播模式一致。arc-gen 样例支持该规则。

## 3. 歧义与风险

- 歧义点：传播方向的具体映射（C 在 2x2 块中哪个位置对应哪个对角方向）并非 100% 确定。
- 当前采用的解释：C 的位置决定传播沿主对角线还是反对角线。
- 风险等级：`medium`

## 4. NeuroGolf 架构提示

- `recommended_architecture`: `multi_layer_conv_relu`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_single_conv`
- `nonlinearity_needed`: `yes`
- 原因：需要检测 2x2 块的精确模式（含颜色 2 的配置），然后沿对角线方向生成传播图案。是模式检测 + 条件生成类任务，需要多步逻辑。

## 5. 最终摘要

```yaml
task_id: "034"
primitive_types: [pattern_detection, diagonal_propagation]
input_shape_rule: 9x9
output_shape_rule: 9x9
formal_rule_short: 从含 2 的 2x2 块沿对角线传播非 2 颜色 C
locality: global
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
main_risk: 传播方向映射规则不确定
confidence: medium
```
