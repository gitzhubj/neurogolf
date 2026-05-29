# Task 096 规范

## 1. 核心规则

- 输入与输出尺寸不同：输入为 17x17~19x19 不等，输出为固定 7x7~11x11 的方形嵌套图案。
- 背景色因样例而异（4、8、3、1 等），关键颜色：1（蓝色）形成内嵌框架，其他颜色（3、6、8 等）为外框或填充色。
- 核心规则：将输入中多个"空心框架"对象（由颜色 1 勾勒）以层叠方式整合为一个对称的嵌套方形图案。每个输入框架对应输出中的一层环，框架内部颜色和背景色被提取并排列为同心方形。

```text
input has N frame-like objects (color-1 outlines + interior colors)
output is a concentric square pattern where:
- outermost ring = outermost frame's outer color (or background)
- inner rings = interior colors of successive frames
- center = innermost frame's interior color
```

- 输出始终为中心对称的方形嵌套结构（类似靶心图案），最外层和最内层可能有额外色彩层。

## 2. 关键证据

- train[0]: 输入 17x17，含 1-矩形框（内部颜色 1 边框 + 4 背景 + 3/6 区域），输出 7x7 嵌套方（6→1→3→4→3→1→6 的同心结构）。
- train[1]: 输入 18x18，含 1-矩形框、8 背景、0、2、4 等，输出 7x7（1→2→4→0→4→2→1 同心结构）。
- train[2]: 输入 18x18，含 1-矩形框和多个其他颜色，输出 11x11（4→1→2→8→7→6→7→8→2→1→4 同心结构）。
- test[0]: 输入 19x19，输出 11x11 嵌套方。
- 输出图案总是奇数边长（7 或 11），最小环宽度为 1 像素。

## 3. 歧义与风险

- 歧义点：输入中嵌套对象的排序规则（如何确定哪个在最外层）。当前解释：按对象 bounding box 大小排序，最大的在最外层。风险等级：medium。
- 歧义点：输出尺寸（7 或 11）的决定因素。当前解释：取决于有效对象数量（N 个对象产生 2N±1 环）。风险等级：high。
- 歧义点：颜色映射规则——输入中的哪个颜色对应输出中的哪一环。当前解释：取决于对象的"边框色"和"填充色"。风险等级：high。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global（需全局分析所有对象并排序）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 此任务极难用 Conv 网络直接实现。需要对象检测、排序、颜色提取和同心图案生成。建议考虑查找表式或硬编码模板方案。

## 5. 最终摘要

```yaml
task_id: 096
primitive_types: [object_detection, concentric_arrangement, color_extraction, ordering]
input_shape_rule: variable, 17x17 to 19x19
output_shape_rule: odd-sized square (7x7 or 11x11)
formal_rule_short: arrange detected frame objects into concentric square rings ordered by size
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
memory_priority: use pre-computed constant templates for each possible output size; avoid dynamic slice/concat
fusion_hint: this task likely benefits from a lookup-table approach mapping input object features to output template
main_risk: object ordering and color mapping to rings are not fully specified
confidence: low
```
