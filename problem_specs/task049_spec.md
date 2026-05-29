# Task 049 规范

## 1. 核心规则

- 输入尺寸可变（从 10x10 到 20x20），输出是输入中某个单色矩形块的精确裁剪。
- 输入由多个嵌套的颜色层组成：每层是一个单色矩形区域，内部包含下一层。最外层往往是颜色 2 或类似色。
- 核心规则：找到被完全包围在最内层的最小单色矩形区域（即"最深的洞"），输出该矩形区域的所有单元格（保持原色）。
- "嵌套"指：一个颜色的连通矩形内部完全包含另一个不同颜色的连通矩形，依此类推。最内层没有内部包含其他颜色。
- 形式化：

```text
找到所有由非零色组成的矩形区域 R。
对每个 R，若其内部所有单元格均属于 R 的颜色或被其他更内层的矩形占据，
且 R 本身被某个不同颜色的矩形完全包围，则 R 是候选。
输出面积最小的候选矩形。
```

## 2. 关键证据

- train 1：2 框架(5x7) 包含 8 块(3x3)，输出 3x3 的 8 块。
- train 2：多层嵌套（3→2→4→1），最内层 1 块(2x2) 被输出。
- train 3：3 框架内包含 6 和 2 等，最内层 6 块(2x3) 被输出。
- train 4：2 框架包含 7 块(3x4)，输出 3x4 的 7 块。
- train 5：1 框架包含 4 块(2x2)，输出 2x2 的 4 块。
- arc-gen 全部支持：输出始终是最内层（最小）的被包围单色矩形。

## 3. 歧义与风险

- 歧义点：如果有两个并列的、面积相同的"最内层"矩形，选哪一个？
  - 当前解释：不确定。train 中未出现并列最内层情况。
  - 风险等级：medium
- 歧义点：最内层是严格矩形还是可以是任意形状？
  - 当前解释：所有观测中均为完美矩形（边框规则、填充完整）。
  - 风险等级：low

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：需要识别嵌套包围关系、提取最内层矩形，属于连通组件分析和树形包围关系推理。不可能用 Conv 逐像素实现。

## 5. 最终摘要

```yaml
task_id: "049"
primitive_types: ["nested_region_extraction", "innermost_crop"]
input_shape_rule: "variable, up to 20x20"
output_shape_rule: "cropped smallest enclosed monochrome rectangle"
formal_rule_short: "extract the innermost (smallest) fully-enclosed monochrome rectangle"
locality: "global"
single_linear_conv_possible: "no"
recommended_architecture: "object_logic_required"
main_risk: "并列最内层选择规则未定"
confidence: "medium"
```
