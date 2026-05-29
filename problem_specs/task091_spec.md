# Task 091 规范

## 1. 核心规则

- 输入输出尺寸不同：输出是输入中"主角"所在区域的裁剪。尺寸由主角 bounding box 决定。
- 背景色为 0。关键颜色：5（灰色）和 8（浅蓝）。此外可能有少量其他零散颜色 8 作为"噪声"。
- 核心规则：找出所有颜色为 5 的像素，计算其最小外接矩形（bounding box），然后向上下各扩展 1 行，以此矩形区域裁剪输入即为输出。

```text
find all (r,c) where input[r,c] == 5
r_min = min(r), r_max = max(r)
c_min = min(c), c_max = max(c)
crop_rows = r_min-1 .. r_max+1
crop_cols = c_min .. c_max
output = input[crop_rows, crop_cols]
```

- 裁剪区域内保留原始所有颜色（5、8 及背景 0），不做颜色映射。裁剪区域外的所有像素被丢弃。

## 2. 关键证据

- train[0]: 5-像素 bbox 为 rows 2-4, cols 1-5。上下各扩展 1 行得到 rows 1-5, cols 1-5 → 5x5 输出，与输出匹配。
- train[1]: 5-像素 bbox rows 4-6, cols 2-8。扩展后 rows 3-7, cols 2-8 → 5x7，匹配。
- train[2]: 5-像素 bbox rows 3-6, cols 3-7。扩展后 rows 2-7, cols 3-7 → 6x5，匹配。
- test[0]: 5-像素 bbox rows 4-11, cols 0-3。扩展后 rows 3-12, cols 0-3 → 10x4，匹配输出。
- arc-gen 覆盖 262 个样例，全部支持该规则。

## 3. 歧义与风险

- 歧义点：当 color=5 不存在时规则如何定义。当前解释：所有可见样例均有 5。风险等级：low。
- 歧义点：扩展方向为何仅垂直扩展而不水平扩展。当前解释：5-像素组件有 8-像素附着在上下方形成"边框"，水平方向无此类附件。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global（需找到所有 5-像素的全局坐标极值）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes（需要 argmax/min 来定位 bbox）
- 需要通过 ReduceMax/ReduceMin 操作找到 5-像素通道的边界，然后执行 Slice。尽量避免逐像素展开为大量中间张量。

## 5. 最终摘要

```yaml
task_id: 091
primitive_types: [cropping, bounding_box, color_detection]
input_shape_rule: variable size, 9x9 to 14x13
output_shape_rule: bounding box of color-5 pixels expanded vertically by 1
formal_rule_short: crop input to (min_r5-1..max_r5+1, min_c5..max_c5)
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
memory_priority: avoid per-pixel expansion; use ReduceMin/ReduceMax then single slice
fusion_hint: combine color-5 detection and bbox computation into a single pass
main_risk: no explicit rule for inputs without color 5
confidence: high
```
