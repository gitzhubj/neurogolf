# Task 100 规范

## 1. 核心规则

- 输入与输出尺寸不同：输入为 10x10 左右，输出固定 2x2。
- 背景色为 0。输入包含 2 个空心矩形框架（颜色不同，如 7 与 8、6 与 7、4 与 2、3 与 9）。
- 核心规则：找出较大的矩形框架（以 bounding box 面积计），输出一个 2x2 的纯色方块，颜色为该较大框架的颜色。

```text
find all hollow rectangular frames (closed border of a single color, interior all background 0)
for each frame:
    compute bbox area = (max_r - min_r + 1) * (max_c - min_c + 1)
select frame with largest bbox area
output = 2x2 block filled with that frame's color
```

- 框架定义为：同一颜色的连续外边框形成的闭合矩形，内部为 0（或与边框颜色不同）。

## 2. 关键证据

- train[0]: 7-框架面积 4x4=16，8-框架面积 4x5=20。较大为 8，输出 2x2 全 8。
- train[1]: 6-框架面积 4x5=20，7-框架面积 4x6=24。较大为 7，输出 2x2 全 7。
- train[2]: 4-框架面积 7x6=42，2-框架面积 3x3=9。较大为 4，输出 2x2 全 4。
- test[0]: 3-框架面积 9x5=45，9-框架面积 10x4=40。较大为 3，输出 2x2 全 3。
- 面积相当时的结果未在数据中出现。arc-gen 有 262 个验证样例。

## 3. 歧义与风险

- 歧义点：当两个框架面积相等时的选择规则。当前解释：未覆盖，可能按颜色值大小或位置。风险等级：medium。
- 歧义点：框架定义——边框厚度是否为 1 像素？当前解释：是，框架为单像素厚度的空心矩形。风险等级：low。
- 歧义点：输出为何是 2x2 而非其他尺寸。当前解释：固定输出格式，所有样例一致。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global（需要检测每个框架并计算面积比较）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 需要检测颜色连续的矩形边框。可用 Conv 检测边框像素，然后对每个颜色计算 bbox 面积。输出为固定 2x2 像素，可通过常量张量实现。最终输出与输入尺寸无关。

## 5. 最终摘要

```yaml
task_id: 100
primitive_types: [frame_detection, size_comparison, constant_output]
input_shape_rule: variable, ~10x10
output_shape_rule: fixed 2x2
formal_rule_short: output 2x2 block of the color of the larger hollow rectangular frame
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
memory_priority: output is tiny (2x2); main cost is frame detection; avoid unnecessary intermediate tensors
fusion_hint: frame detection can share a single border-detection Conv across all color channels
main_risk: tie-breaking for equal-area frames not specified
confidence: high
```
