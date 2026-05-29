# Task 044 规范

## 1. 核心规则

- 输入输出尺寸相同（均为 10x10）。
- 背景色为 0，颜色 5 构成矩形"框架"(containers)，其他非零颜色（如 8,6,7,1,3,9 等）构成被包围在框架内部的"内容块"。
- 核心规则：在多个 5-框架之间，找出形状（bounding box 尺寸）相同的成对内容块，将它们互换（swap）。不匹配的内容块保持原位。
- 框架本身（5）在输出中保持不变。
- 互换时保持内容块的形状不变，仅改变其颜色和目标框架位置。

## 2. 关键证据

- train 1：8-块(2x2) 和 6-块(2x2) 形状相同、出现在两个不同 5-框架内，输出中两个块互换位置。7-散点没有匹配，保持原位。
- train 2：1-块(形状特定) 与 3-块互换，9-块与其匹配对象互换，框架保持。
- train 3：2-块 与 8-块互换，4-散点保持。
- arc-gen 全部支持基于形状匹配的内容互换规则：大小相同的两个块（即使颜色不同）会在各自的 5-框架之间交换。

## 3. 歧义与风险

- 歧义点：如果存在 3 个或更多相同形状的块，互换顺序是什么？
  - 当前解释：不确定，可能需要循环互换或按位置排列。
  - 风险等级：medium
- 歧义点：形状匹配的定义是严格的 bounding box 全等，还是仅宽高相同？
  - 当前解释：采用 bounding box 宽高相同即可，不要求内部像素排列全等。
  - 风险等级：low
- 歧义点：框架之外的散点如何处理？
  - 当前解释：保持不变，不参与交换。
  - 风险等级：low

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：需要识别 5-框架边界、提取每个框架内的内容块、计算其 bounding box、匹配相同形状的块、执行互换——这需要连通组件分析+物体操作，单层 Conv 完全无法实现。

## 5. 最终摘要

```yaml
task_id: "044"
primitive_types: ["object_swap", "bounding_box_match", "container_extraction"]
input_shape_rule: "same as output, 10x10"
output_shape_rule: "same as input"
formal_rule_short: "swap same-shaped content blocks between 5-frame containers"
locality: "global"
single_linear_conv_possible: "no"
recommended_architecture: "object_logic_required"
main_risk: "多于 2 个相同形状块时的互换顺序不确定"
confidence: "medium"
```
