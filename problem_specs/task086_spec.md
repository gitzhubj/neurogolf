# Task 086 规范

## 1. 核心规则

- 输入/输出尺寸相同。
- 输入中包含一个"相框"结构：外框颜色 A 包围内部颜色 B（如 A=4 框住 B=6，或 A=2 框住 B=7）。
- 核心变换：框向外膨胀 1 层，内部进行颜色交换——原框颜色进入内部中心，原内部颜色成为中间环。
- 输出结构（以 3×3 心+框为例）：
  - 最外层：颜色 A（膨胀后 +1 层）
  - 中间环：颜色 B（原内部颜色，现为 1 格宽的环）
  - 最内层：颜色 A（原框颜色）
- 多个框独立处理。不相邻的框各自膨胀。

## 2. 关键证据

- train 0：3×3 框 4 包围中心 6 → 膨胀为 5×5，外环 4、中环 6、中心 4。
- train 1：4×2 框 2 包围 2×2 的 7 → 膨胀后外环 2、中环 7、中心 2。
- train 2：类似 3×3 框 3 包围 1 → 膨胀为外环 3、中环 1、中心 3。
- test 0：两个框（一个 3×3 框 8 包围 3，一个 4×2 框 8 包围 3）各自膨胀并交换颜色。

## 3. 歧义与风险

- 歧义点：膨胀后两个相邻框重叠时的优先级。当前解释：test 中两个框不相邻，未出现重叠。风险等级：medium。
- 歧义点：框的识别算法（如何区分钟框颜色和内部颜色）。当前解释：颜色形成封闭边界且内部填充另一种颜色。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required（需识别框结构 + 膨胀 + 颜色交换）
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes

## 5. 最终摘要

```yaml
task_id: 086
primitive_types: [frame_dilation, color_swap, morphological_grow]
input_shape_rule: same as output
output_shape_rule: same as input
formal_rule_short: dilate the frame by 1 layer, swap frame and interior colors (frame→center, interior→ring)
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: overlapping frames handling undefined
confidence: high
```
