# Task 024 规范

## 1. 核心规则

- 输入输出尺寸相同（H×W → H×W），等尺寸变换。
- 背景色为 0。输入中仅有点状锚点像素（颜色 1, 2, 3），每种颜色最多出现若干个但位置任意。
- 核心变换：颜色 1 和 3 的锚点填充其所在整行；颜色 2 的锚点填充其所在整列。行填充（1, 3）优先于列填充（2）。
- 若多个同色锚点共存，每个触发各自的整行/列填充，效果叠加（同色无冲突）。

```text
output[r, c] = 0  (默认)
for each anchor at (r0, c0) with color k:
    if k in {1, 3}:
        output[r0, :] = k   (整行覆盖)
    elif k == 2:
        for each row r where no row-anchor exists:
            output[r, c0] = 2
```

## 2. 关键证据

- train 0：9×9。锚点 2@(2,2)、3@(4,7)、1@(6,3)。输出中 column 2 全部为 2（在非锚点行），row 4 全 3，row 6 全 1。行锚点行中的 col 2 也被覆盖为 3 或 1，证明行优先于列。
- train 1：10×8。锚点 3@(1,1) 和 (4,3)、1@(6,1)、2@(7,5)。输出 row 1/4 全 3，row 6 全 1，column 5 在其他行全 2。匹配规则。
- train 2：10×11。锚点 1@(1,1)、3@(3,8) 和 (6,2)、2@(8,3) 和 (9,9)。输出 row 1 全 1，row 3/6 全 3，col 3 和 col 9 在其他行全 2。同一行两个 3 锚点、同一列两个 2 锚点均向上兼容。
- arc-gen 263 样例均支持此规则，覆盖不同网格尺寸和锚点组合。

## 3. 歧义与风险

- 歧义点：若同一行既有 1 又有 3 锚点如何处理。当前解释：两者均试图填充该行，但未在训练数据中观测到。风险等级：medium。
- 歧义点：若同一列有多个 2 锚点，效果相同（整列填充 2），无歧义。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 27 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: And+Cast+Concat+Not+Or+Pad+ReduceMax+Slice (27 nodes, 11 initializers)

## 5. 最终摘要

```yaml
task_id: 024
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 27 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: And+Cast+Concat+Not+Or+Pad+ReduceMax+Slice
actual_nodes: 27
```
