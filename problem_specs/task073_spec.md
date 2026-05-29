# Task 073 规范

## 1. 核心规则

- 输入/输出尺寸相同(5x5)，背景色为 0。
- 颜色仅涉及 1(蓝)和 5(灰)。输入最底行(行 4)全部为灰色(5)。
- 蓝色(1)像素出现在行 2(某些列)的正上方，其正下方行 3 为灰色(5)。
- 变换规则：蓝色(1)垂直向下"掉落"到最底行(行 4)，同时与最底行的灰色(5)交换位置。

```text
for each column c:
    if input[2][c] == 1:
        new row 2: all 0 (clear blue row)
        new row 4[c] = 1  (blue falls to bottom)
        # original gray at row 4[c] moves up to where blue was
        new row 2[c] = 5 if original row 4[c] == 5 else ...
    # row 3 unchanged (gray stays)
```

- 更简洁地描述：所有蓝色(1)像素从行 2 降至行 4(同列)，行 4 原有的灰色(5)被"顶替"到行 2 同列位置。行 3 的灰色(5)保持不变。

## 2. 关键证据

- 所有样例均为 5x5 固定尺寸，行 4 全部为 5。
- train[0]: 行 2 单蓝(1)→输出行 4 第 2 列变蓝；行 4 第 2 列原灰(5)移到行 2 第 2 列。
- train[1]: 行 2 两蓝(1,3)→输出行 4 第 1、3 列变蓝；行 4 第 1、3 列原灰移到行 2 对应列。
- train[2]: 行 2 两蓝(1,4)→输出行 4 第 1、4 列变蓝；同上交换。
- arc-gen 有 11 个确认样例(数量较少但仍支持该模式)。

## 3. 歧义与风险

- 蓝色(1)是否会出现在行 3？当前未观察到，但不确定。风险: `low`。
- 如果蓝色下方不是灰色(5)会怎样？未在样例中出现。风险: `low`。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: 0 (逐列操作)
- single_linear_conv_possible: no
- recommended_kernel: 1x1
- nonlinearity_needed: yes
- 核心是颜色 1 和 5 在同一列上的位置交换。可拆解为：
  1. 检测每列是否有蓝(1)
  2. 检测最底行同列是否为灰(5)
  3. 交换位置
- 可用 1x1 Conv 分离颜色 channel，再用 Reduce 或切片做位置交换。避免产生大量按列操作的中间张量。

## 5. 最终摘要

```yaml
task_id: 073
primitive_types: [vertical_swap, gravity, color_position_exchange]
input_shape_rule: 5x5
output_shape_rule: 5x5
formal_rule_short: Blue(1) in row 2 falls to bottom row, swapping with gray(5) in same column
locality: 0
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
memory_priority: Use per-channel masking instead of positional scatter/gather
fusion_hint: Combine blue detection and gray detection into single Conv, then swap via channel manipulation
main_risk: Blue might appear in other rows in unseen examples
confidence: medium
```
