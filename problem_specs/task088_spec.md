# Task 088 规范

## 1. 核心规则

- 输入 H×W 包含两类颜色：标记色（成对出现，如颜色 4, 3, 6, 8）和图案色（颜色 2, 8, 4）。
- 输出为图案色的裁剪结果，尺寸为标记色对之间的矩形区域。
- 核心变换：找到标记色（在同列或同行对称出现的颜色对）的 bounding box，然后裁剪出该矩形内图案色的形状到输出网格。
- 输出网格尺寸 = 标记色 bounding box 的尺寸。
- 标记色在输出中被移除（替换为 0），仅保留图案色。

```text
marker_color = most frequent non-zero non-pattern color
bbox = bounding_box(cells with marker_color)
output = crop(input[bbox], pattern_color)
```

## 2. 关键证据

- train 0：7×7 → 3×3。标记色 4（四角对称分布），图案色 2（中间十字形），裁剪出 3×3 图案。
- train 1：12×9 → 3×5。标记色 3（左右对称对），图案色 2，裁剪出图案的 bounding box 内容。
- train 2：12×14 → 4×4。标记色 6（左右对称），图案色 8，裁剪输出 4×4。
- train 3：12×18 → 4×8。标记色 8（左右对称），图案色 4，裁剪输出 4×8。
- 所有样例中输出仅保留图案色，标记色不出现。

## 3. 歧义与风险

- 歧义点：如何区分标记色和图案色。当前解释：标记色为成对出现（左右或上下对称）且频次较少的非零色。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required（需检测标记色位置 + 裁剪）
- locality: global
- single_linear_conv_possible: no（动态裁剪非单层 Conv 可表达）
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes

## 5. 最终摘要

```yaml
task_id: 088
primitive_types: [marker_detection, crop_to_bbox, pattern_extraction]
input_shape_rule: HxW (varies)
output_shape_rule: marker_bbox size
formal_rule_short: find symmetric marker color pairs, crop pattern between them
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: marker vs pattern color ambiguity
confidence: medium
```
