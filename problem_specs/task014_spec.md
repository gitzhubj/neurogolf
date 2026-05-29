# Task 014 规范

## 1. 核心规则

- 输入为一组不同尺寸的小网格, 每个网格内有一种唯一的非零"面板颜色"。
- 输出为该唯一颜色面板的 bounding box 裁剪结果, 丢弃所有零值边框。
- 裁剪规则: 找到输入中该唯一非零颜色的最小 bounding box(包含所有该颜色像素的最小矩形), 输出为该矩形内的子网格。
- 输出中保留该非零颜色, 背景为零(不确定是否将框内零值保留或做其他处理)。

## 2. 关键证据

- 每个 train 样例的输入网格尺寸不同, 输出尺寸较小(裁剪后)。
- 每个输入网格只有一种非零颜色(如 4 例分别使用不同颜色)。
- 输出恰好包含输入中该唯一非零颜色对应的区域。
- with-spec 基线 4/4 train 通过, 1/1 test 通过, 262/262 arc-gen 通过。

## 3. 歧义与风险

- 歧义点: 裁剪边界的具体确定方式(最小矩形还是某种更复杂的形状)。
- 当前采用的解释: 最小矩形 bounding box。
- 风险等级: low

- 歧义点: 若输入中有多个不同非零颜色如何处理。
- 当前采用的解释: 输入中仅有一种非零颜色, 该场景不会出现。
- 风险等级: low

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 动态裁剪需要全局 bounding box 计算, 无法由固定卷积核实现。在 ONNX 中实现需借助全局 argmax / 坐标累加来确定边界, 然后用 gather/crop 操作提取子网格。

## 5. 最终摘要

```yaml
task_id: 014
primitive_types: [dynamic_crop, bounding_box]
input_shape_rule: variable
output_shape_rule: crop to bounding box of unique non-zero color
formal_rule_short: crop = bounding_box(only_non_background_color); output = input[crop]
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 边界确定方式
confidence: medium
```
