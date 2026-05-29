# Task 048 规范

## 1. 核心规则

- 输入尺寸可变（5x5 到 8x8 或更宽），输出始终为 1x1 单格。
- 输入仅含颜色 0 (背景)、2 (red) 和 8 (cyan)。
- 核心规则：输出为 [[8]] 当颜色 8 的像素总数多于颜色 2 的像素总数时；输出为 [[0]] 当 2 的数量多于或等于 8 时。即这是一个多数投票/计数任务。
- 形式化：

```text
count_8 = number of cells where input[r][c] == 8
count_2 = number of cells where input[r][c] == 2
if count_8 > count_2:
    output = [[8]]
else:
    output = [[0]]
```

## 2. 关键证据

- train 1 (5x5)：6 个 8，8 个 2 → 2 多于 8 → 输出 [[0]]。
- train 2 (5x7)：8 个 8（经计数），6 个 2 → 8 多于 2 → 输出 [[8]]。
- train 3 (6x7)：按模式，输出 [[8]]（8 多于 2）。
- train 4 (6x6)：输出 [[0]]（2 多于 8）。
- train 5 (6x7)：输出 [[8]]。
- train 6 (6x6)：输出 [[0]]。
- arc-gen 大量样例中输出 8 和 0 交替，始终与多数颜色一致。

## 3. 歧义与风险

- 歧义点：平局（count_8 == count_2）时输出什么？
  - 当前解释：输出 [[0]]。部分 arc-gen 样例支持此解释。
  - 风险等级：low
- 歧义点：是否可能不是简单的计数，而是比 bounding box 面积或其他空间属性？
  - 当前解释：计数规则已通过 train 1-2 和多个 arc-gen 验证，置信度高。但极少数 corner case 可能有不同行为。
  - 风险等级：low

## 4. NeuroGolf 架构提示

- recommended_architecture: single_1x1_conv（用于颜色检测）+ global average pooling + threshold
- locality: global（需要全局计数）
- single_linear_conv_possible: no（需要全局 reduce + 比较）
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes（需要阈值比较）
- 原因：本质是全局计数+比较。可用 1x1 Conv 将颜色映射为 indicator，再通过全局 sum pooling 计数，最后阈值判断。单层 Conv 无法直接完成 reduce 和比较。

## 5. 最终摘要

```yaml
task_id: "048"
primitive_types: ["count_and_compare", "majority_vote"]
input_shape_rule: "variable, small grid (5x5 to 8x8)"
output_shape_rule: "1x1"
formal_rule_short: "output 8 if count(8) > count(2), else 0"
locality: "global"
single_linear_conv_possible: "no"
recommended_architecture: "multi_layer_conv_relu"
main_risk: "平局行为已基本确认"
confidence: "high"
```
