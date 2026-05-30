# Task 031 规范

## 1. 核心规则

- 输入尺寸不固定（10x12 到 12x12），输出尺寸 = 非零像素的 minimal bounding box。
- 背景色为 0（黑色）。非零颜色（2, 1, 8, 6, 9, 5, 3, 4, 7 等）都被保留，不改变颜色值。
- 最核心规则：找到所有 `input[r,c] != 0` 的坐标，计算 min_row, max_row, min_col, max_col，然后 crop：
  ```text
  output = input[min_row:max_row+1, min_col:max_col+1]
  ```
- 颜色不变，只是空间裁剪。多个不连通的对象一并框入同一个 bounding box。
- 输出尺寸完全由输入中非零像素的分布决定。

## 2. 关键证据

- Train 0：输入 10x12，仅含颜色 2 的 L 形，输出 4x4，恰好框住所有 2。
- Train 1：输入 11x12，含颜色 1 的多块分散形状，输出 5x3，框住全部 1 的像素。
- Train 2：输入 12x12，含颜色 8 的分散图案，输出 3x5。
- Test：输入 12x12 含颜色 6，输出 4x6，符合 bounding box 裁剪规则。
- arc-gen 全部 25+ 样例均符合此规则，不同颜色和形状均一致。

## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 26 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Add+And+ArgMax+Cast+Gather+Greater+LessOrEqual+Pad+ReduceSum+Slice+Sub+Unsqueeze+Where (26 nodes, 13 initializers)

## 5. 最终摘要

```yaml
task_id: 031
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 26 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Add+And+ArgMax+Cast+Gather+Greater+LessOrEqual+Pad+ReduceSum+Slice+Sub+Unsqueeze+Where
actual_nodes: 26
```
