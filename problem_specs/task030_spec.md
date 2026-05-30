# Task 030 规范

## 1. 核心规则

- 输入输出尺寸相同（H×W → H×W），等尺寸变换。
- 背景色为 0。输入中有多个不同颜色的连通块（每块单一颜色，颜色可以是 1, 2, 4 等），块位置分散在不同行。
- 核心变换：重力沉降 — 每个连通块在垂直方向下移，直到碰到网格底部或碰到其他已下沉的块为止。块内形状在沉降过程中保持不变，水平位置（列坐标）保持不变。
- 不同颜色的块之间不混合、不重叠，按沉降后占据各自独立区域。

```text
for each column c:
    stack all non-zero cells from input column c:
        collect in top-to-bottom order
        place at bottom of output column c
```

## 2. 关键证据

- train 0：5×10。输入中 2×2 块(颜色 2)在行 0-1，2×2 块(颜色 1)在行 1-2，2×2 块(颜色 4)在行 2-3。输出中所有块下沉到行 1-3（底部之上），保持水平位置不变、形状不变。底部留一行空白。
- train 1：10×10。3×2 块(颜色 4)在右上角行 0-1，3×2 块(颜色 2)在左侧行 2-3，3×2 块(颜色 1)在中间行 5-6。输出所有块集中到行 5-7，水平位置不变。
- train 2：5×10。单格块颜色 2 在行 2，1×2 颜色 1 在行 2-3，1×2 颜色 4 在行 3-4。输出所有块下沉到行 2-4，底部仍有空白行。
- 所有训练样例中块在沉降后仍保持原始形状（包括宽度和高度），无水平位移。
- arc-gen 覆盖多种块形状和颜色组合，均支持重力规则。

## 3. 歧义与风险

- 歧义点：多列块沉降的列间独立性 vs 整体块保持。当前解释：每个连通块作为整体沉降（块内部行列关系不变），而非逐列独立 stack（否则会断开 2×2 等块）。风险等级：low（训练样例中逐列 stack 和整体块沉降等价于同样输出，因为块都是矩形且紧密排列）。
- 歧义点：若两个不同颜色块沉降后重叠。当前解释：块按原始垂直位置顺序先后沉降，先到底的块占据空间，后到的块堆叠在其上方。训练样例中块的水平位置都分离，未出现此情况。风险等级：medium。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 56 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Add+And+ArgMax+Cast+Concat+Gather+Greater+Less+Not+Or+ReduceSum+Reshape+Slice+Squeeze+Sub+Sum+Where (56 nodes, 13 initializers)

## 5. 最终摘要

```yaml
task_id: 030
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 56 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Add+And+ArgMax+Cast+Concat+Gather+Greater+Less+Not+Or+ReduceSum+Reshape+Slice+Squeeze+Sub+Sum+Where
actual_nodes: 56
```
