# Task 008 规范

## 1. 核心规则

- 输入固定 9x9，输出固定 9x9（同尺寸）。
- 背景色为 0。输入仅含 0 和 5。输出含 0、1、2、3、4。
- 核心变换：将每个由 5 组成的"列段"（一列中连续或整体的 5 像素）按列首次出现（最顶行序号）的先后顺序，替换为递增数字 1、2、3、4。
- 第 1 个出现 5 的列（最顶行最小）全部 5 替换为 1，第 2 个出现的列替换为 2，依此类推。不同列的 5 段互不干扰。

```text
columns_with_5 = []
for each column c where input contains color 5:
    first_row = min row where input[r][c] == 5
    columns_with_5.append((first_row, c))

sort columns_with_5 by first_row ascending
for i, (_, c) in enumerate(columns_with_5):
    for all rows r where input[r][c] == 5:
        output[r][c] = i + 1   # 1-indexed
```

- 输入中无 5 的位置在输出保持 0。

## 2. 关键证据

- train 0（9x9）：5 出现在 col 5（首次行 0）、col 1（首次行 1）、col 3（首次行 3）、col 7（首次行 6）。输出对应列分别替换为 1、2、3、4，其余位保持 0。
- train 1（9x9）：5 出现在 col 7（行 1）、col 3（行 4）、col 5（行 5）、col 1（行 7）。输出按首次出现行序替换为 1..4，验证规则与列位置无关，仅取决于首次出现的垂直顺序。
- test：5 列按首次出现行序（col 1 行 1、col 5 行 2、col 7 行 4、col 3 行 6）替换为 1..4。
- arc-gen 涵盖不同列组合和首次行排列，均支持首次出现序编号规则。

## 3. 歧义与风险

- 歧义点：若两列的首次 5 出现在同一行如何处理。当前解释：按列号升序 tie-break（左列优先）。可见数据无此情况。风险等级：low。
- 歧义点：编号使用 1..N 还是固定 1..4。当前解释：可见样例均为 4 列 5，编号 1..4。若列数不同（如 3 列或 5 列），编号范围相应变化（1..N）。风险等级：medium（未覆盖非 4 列情况）。
- 歧义点：同列中 5 有间断（被 0 隔开）是否视为同一列段。当前解释：同列所有 5 统一编号，不论是否连续。可见数据未出现间断情况。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 78 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: And+Cast+Clip+Concat+Gather+Greater+Less+Mul+Not+Or+Pad+ReduceMax+ReduceMin+ReduceSum+Reshape+Slice+Sub+Sum+Where (78 nodes, 21 initializers)

## 5. 最终摘要

```yaml
task_id: 008
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 78 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: And+Cast+Clip+Concat+Gather+Greater+Less+Mul+Not+Or+Pad+ReduceMax+ReduceMin+ReduceSum+Reshape+Slice+Sub+Sum+Where
actual_nodes: 78
```
