# Task 065 规范

## 1. 核心规则

- 输入是一个被"十"字形(完整的一行加一列)分割的网格;输出是十字分割出的**某个象限**。
- 十字由单一颜色组成,贯穿整行和整列,将网格划分为四个矩形象限。
- 存在一个"异色像素"(颜色不同于背景和十字颜色),出现在某个象限中。
- 核心规则:找到包含这个异色像素的象限,将其作为输出。

```text
cross_color = a color C such that a full row R and full column Col are all C
quadrants = 4 sub-rectangles formed by removing row R and col Col
anomaly = the unique pixel whose color is not background and not C
output = quadrant containing the anomaly pixel
```

- 输出大小 = `(max(R, H-1-R)) × (max(Col, W-1-Col))` 或固定为该象限的实际大小。

## 2. 关键证据

- train[0]:5×5,十字色 3 在行 2/列 2,背景 8,异色 4 在(4,0)左下象限,输出 2×2 左下象限。
- train[1]:7×7,十字色 2 在行 3/列 3,背景 4,异色 1 在(1,5)右上象限,输出 3×3 右上象限。
- train[2]:11×11,十字色 1 在行 5/列 5,背景 3,异色 8 在(2,1)左上象限,输出 5×5 左上象限。
- test[0]:13×13,十字色 0 在行 6/列 6,背景 1,异色 2 在(3,8)右上象限,输出 6×6 右上象限。
- 象限大小等于十字划分出的四个区域中最大的尺寸(或完全匹配该象限尺寸)。arc-gen 262 个样例全部一致。

## 3. 歧义与风险

- 十字的检测条件:十字必须是完整的一整行加上一整列颜色完全相同,且该颜色只出现在十字线上(或主要出现在十字线上)。风险:low。
- 异色像素的唯一性:每个样例中恰好有一个像素颜色既不是背景也不是十字色。风险:low。
- 输出尺寸:该象限的原始尺寸,不含十字行/列。风险:low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 36 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Add+And+Cast+Div+Gather+Greater+Less+Mul+Pad+ReduceMax+ReduceSum+Slice+Squeeze+Sub+Where (36 nodes, 12 initializers)

## 5. 最终摘要

```yaml
task_id: 065
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 36 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Add+And+Cast+Div+Gather+Greater+Less+Mul+Pad+ReduceMax+ReduceSum+Slice+Squeeze+Sub+Where
actual_nodes: 36
```
