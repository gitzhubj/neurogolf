# Task 051 规范

## 1. 核心规则

- 输入输出尺寸相同（H×W → H×W），等尺寸变换。
- 背景色为 0。输入中包含一个菱形/箭头形状的图案（由单一颜色构成，通常为 2、8、3 等），菱形中心有一个不同颜色的"核心"格。
- 核心变换：方向检测 + 投影。菱形的形状指示了方向（如向右的箭头、向上的箭头、向下的箭头），将核心格的颜色沿该方向投影/延伸到网格边界。
- 输入中除核心格外，菱形整体保留不变；核心格颜色被延伸成一条直线（水平或垂直），覆盖原为 0 的区域。
- 延伸线从菱形边界开始，沿指示方向直到网格边缘；不覆盖菱形自身的格子。

```text
direction = detect_arrow_orientation(diamond_shape)
line_color = center_cell_color
for each cell along direction from diamond edge to border:
    if cell == 0:
        output[cell] = line_color
```

## 2. 关键证据

- train 0：10×15。颜色 2 构成开口朝右的菱形，核心格颜色 1 在 (4,3)。输出在 row 4 的 col 5-14 填满颜色 1（向右延伸）。
- train 1：12×12。颜色 8 构成开口朝上的菱形，核心格颜色 3 在 (8,6)。输出在 col 6 的 row 0-4 填满颜色 3（向上延伸）。
- train 2：15×12。颜色 3 构成开口朝下的菱形，核心格颜色 2 在 (2,4)。输出在 col 4 的 row 5-14 填满颜色 2（向下延伸）。
- 所有样例中，延伸方向与菱形的开口方向一致，延伸颜色等于核心格颜色。
- arc-gen 261 例覆盖多种方向组合，均支持该规则。

## 3. 歧义与风险

- 歧义点：菱形方向检测的具体算法（如何从网格形状判断方向）。当前解释：菱形最宽的部分指示了垂直/水平方向，开口侧为延伸方向。风险等级：medium（所有可见样例菱形方向明确）。
- 歧义点：若存在多个菱形/多核心格。当前解释：每例仅一个核心格和一组方向指示。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 57 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: And+ArgMax+Cast+Concat+Equal+Greater+Less+Mul+Or+ReduceMax+ReduceSum+Slice+Sub+Unsqueeze+Where (57 nodes, 13 initializers)

## 5. 最终摘要

```yaml
task_id: 051
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 57 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: And+ArgMax+Cast+Concat+Equal+Greater+Less+Mul+Or+ReduceMax+ReduceSum+Slice+Sub+Unsqueeze+Where
actual_nodes: 57
```
