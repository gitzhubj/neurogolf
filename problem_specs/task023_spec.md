# Task 023 规范

## 1. 核心规则

- 输入/输出尺寸相同（变化尺寸，例如 9x9、8x10、11x10）。
- 背景色为 0（黑色）。输入中只有少数离散像素，颜色为 1（蓝色）、2（红色）、3（绿色）。
- 颜色 2（红色）：将其所在列整列填充为 2。
- 颜色 1（蓝色）和 3（绿色）：将其所在行整行填充为该颜色。
- 行颜色和列颜色在交点处：行颜色覆盖列颜色（即行优先）。
- arc-gen 样例多数支持该规则，但偶有不同颜色组合，颜色角色（行 vs 列）可能随颜色变化。

## 2. 关键证据

- train[0]（9x9）：2 在 (2,2) 产生全列 2；3 在 (4,7) 产生全行 3；1 在 (6,3) 产生全行 1。交点 (4,2) 处行为 3（行优先），(6,2) 处行为 1。
- train[1]（8x10）：3 在两行产生全行，1 在一行产生全行，2 产生全列。规则一致。
- train[2]（11x10）：1 产生全行，3 在多个行产生全行，2 在两个列产生全列。规则一致。
- 测试样例同样为投影模式。

## 3. 歧义与风险

- 歧义点：颜色与方向（行/列）的映射关系是否固定（2=列，1/3=行 vs 可能与具体颜色值有关）。
- 当前采用的解释：颜色 2 始终对应列投影，颜色 1、3 对应行投影。此结对所有 train 样例有效。
- 风险等级：medium（如果测试中引入新颜色，角色不确定）。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：需要先定位离散像素的坐标，然后广播到整行/整列。这需要全局信息（行/列广播）。1x1 Conv 无法实现行广播。

## 5. 最终摘要

```yaml
task_id: 023
primitive_types: [projection, row_fill, column_fill]
input_shape_rule: variable, same as output
output_shape_rule: same as input
formal_rule_short: 对颜色 2 填列，对颜色 1/3 填行，行优先于列
locality: global
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
main_risk: 颜色-方向映射在新颜色上不确定
confidence: medium
```
