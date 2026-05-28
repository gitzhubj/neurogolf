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

- `recommended_architecture`: `object_logic_required`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_single_conv`
- `nonlinearity_needed`: `yes`
- 原因：需要全局搜索非零像素的 min/max 坐标，无法用单层 Conv 实现。需要 argmax/where 等非卷积操作来确定 bounding box，然后执行 crop。属于对象检测+裁剪类任务。

## 5. 最终摘要

```yaml
task_id: "031"
primitive_types: [crop, bounding_box]
input_shape_rule: 任意矩形（≤30x30），含至少一个非零像素
output_shape_rule: (max_row - min_row + 1) x (max_col - min_col + 1)
formal_rule_short: output = input[bb(nonzero_cells)]
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 无
confidence: high
```
