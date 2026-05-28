# Task 022 规范

## 1. 核心规则

- 输入 11x11，输出 3x3。
- 背景色为 0（黑色）。关键颜色：5（灰色）作为空间分隔标记，其他颜色为 4（黄色）、6（品红）、7（橙色）、2（红色）、3（绿色）等。
- 灰色（5）在输入中形成交叉轴或象限划分标记，通常有 3 个灰色像素。
- 灰色的位置将 11x11 网格划分为 9 个区域（3x3 逻辑分区）。每个区域内的非零、非灰色像素颜色填入输出对应 3x3 位置。
- 输出中心位置（1,1）固定为 5（灰色）。其他 8 个单元格按输入中各区域的颜色填充。如果区域内无颜色则填 0。
- arc-gen 样例全部支持该规则。

## 2. 关键证据

- train[0]: 输入 11x11 中有灰色在 (2,3)、(2,7)、(8,5)，非灰色分布在灰色划分的 9 个区域中；输出 3x3 中心为 5，其他位置对应各区域颜色。
- train[1-2]: 类似模式，不同颜色组合和灰色位置，均产生 3x3 输出，中心为 5。
- 所有 3 个训练样例输入均为 11x11，输出均为 3x3，且灰色始终位于输出中心。
- 测试样例同样为 11x11 -> 3x3。

## 3. 歧义与风险

- 歧义点：灰色标记的具体划分规则（是基于灰色连线形成的十字交叉，还是基于灰色 bounding box 的中心）。
- 当前采用的解释：灰色位置定义了一个坐标框架，将空间划分为 3x3 网格区域。
- 风险等级：medium。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：需要先检测灰色标记位置作为参考框架，然后根据每个颜色像素相对于灰色框架的位置分配到 3x3 输出。涉及坐标变换和区域划分，不是纯局部操作。

## 5. 最终摘要

```yaml
task_id: 022
primitive_types: [region_partition, color_extraction, coordinate_transform]
input_shape_rule: 11x11
output_shape_rule: 3x3
formal_rule_short: 以灰色(5)为坐标轴划分 11x11 为 3x3 区域，每区域颜色映射到输出对应格
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 灰色划分规则可能有多种解释
confidence: medium
```
