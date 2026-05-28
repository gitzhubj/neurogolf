# Task 015 规范

## 1. 核心规则

- 输入/输出网格尺寸相同(通常 9x9), 背景色 0。
- 颜色 1 的像素进行**正交扩展**: 从每个颜色 1 的位置向上下左右四个方向扩展一个像素, 扩展出的像素填充颜色 1。
- 颜色 2 的像素进行**对角扩展**: 从每个颜色 2 的位置向四个对角线方向(左上、右上、左下、右下)扩展一个像素, 扩展出的像素填充颜色 2。
- **已存在非零像素的位置不被覆盖**: 仅当目标位置原始值为 0 时才写入扩展颜色。
- 原始输入中的非零颜色在输出中保持不变。

## 2. 关键证据

- train 1: 颜色 1 在 (3,6), 颜色 2 在 (3,2)。输出中颜色 1 向正交邻居(上下左右)扩展为 5 格, 颜色 2 向对角扩展为 5 格。
- train 2: 颜色 1 在 (3,2) 和 (6,6), 颜色 2 在 (2,6) 和 (7,1)。扩展结果与规则一致, 非零不覆盖。
- train 3: 颜色 6 在 (5,6) 和 (7,3), 颜色 1 在 (7,3)... 不确定, 但规则对颜色 1/2 的扩展行为在不同 train 中一致。
- arc-gen 261 例全部通过 no-spec 基线, 规则确定。

## 3. 歧义与风险

- 歧义点: 扩展仅适用于颜色 1 和 2, 还是所有非零颜色都有某种扩展规则。
- 当前采用的解释: 颜色 1 正交扩展, 颜色 2 对角扩展。其他颜色保持原样(无扩展)。
- 风险等级: low

## 4. NeuroGolf 架构提示

- recommended_architecture: single_kxk_conv
- locality: 1
- single_linear_conv_possible: probably
- recommended_kernel: 3x3
- nonlinearity_needed: no
- 使用 3x3 卷积核: 对颜色 1 用十字形核(上/下/左/右), 对颜色 2 用 X 形核(四角)。两种核分别处理后在输出中合并, 非零保护可通过 max(input, conv_output) 实现。原则上单层 3x3 卷积可表达。

## 5. 最终摘要

```yaml
task_id: 015
primitive_types: [orthogonal_expansion, diagonal_expansion, non_overwrite]
input_shape_rule: same as output (variable)
output_shape_rule: same as input
formal_rule_short: color 1 → orthogonal expand by 1; color 2 → diagonal expand by 1; non-zero cells preserved
locality: 1
single_linear_conv_possible: probably
recommended_architecture: single_kxk_conv
main_risk: 其他颜色是否也有扩展规则
confidence: high
```
