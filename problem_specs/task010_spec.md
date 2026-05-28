# Task 010 规范

## 1. 核心规则

- 输入固定 9x9，输出固定 9x9（同尺寸）。
- 背景色为 0。输入仅含 0 和 5。输出含 0、1、2、3、4。
- 核心变换：与 Task 008 相同——将输入中每个含颜色 5 的列按其首次出现 5 的行号（从顶至底）排序，按序替换为递增数字 1、2、3、4。
- 若两列首次出现 5 的行号相同，按列号升序 tie-break。
- 不含 5 的列在输出中保持全 0。

```text
columns_with_5 = []
for each column c where 5 appears:
    first_row = min r such that input[r][c] == 5
    columns_with_5.append((first_row, c))
sort columns_with_5 by (first_row, c) ascending
for i, (_, c) in enumerate(columns_with_5):
    for all r where input[r][c] == 5:
        output[r][c] = i + 1
```

## 2. 关键证据

- train 0（9x9）：5 列 col 5 首次行 0、col 1 首次行 1、col 3 首次行 5、col 7 首次行 7。输出对应列替换为 1..4，顺序与首次行一致。
- train 1（9x9）：不同 5 列首次行排列产生不同编号顺序（如 col 7 第一、col 3 第二），验证编号仅取决于首次行而非固定列位置。
- arc-gen 涵盖多种列排列，均支持首次出现排序编号规则。

## 3. 歧义与风险

- 歧义点：若首次行相同，tie-breaking 按列号还是其他规则。当前解释：按列号升序。风险等级：low。
- 歧义点：列中 5 若被 0 隔断是否为同一编号。当前解释：同列所有 5 统一编号。风险等级：low。
- 歧义点：编号上限是否为 4（列数是否可变）。当前解释：可见数据均为 4 列 5，编号 1..4。列数变化时编号范围相应变化（1..N）。风险等级：medium。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu（需按列检测首次非零行、列间排序、条件赋值）
- locality: global（序号分配需跨列比较）
- single_linear_conv_possible: no（排序逻辑非单层线性可表达）
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes

颜色映射表：

```text
input 5 -> output depends on column rank by first-row:
  rank 1 (earliest 5 from top): output 1
  rank 2: output 2
  rank 3: output 3
  rank 4: output 4
input 0 -> output 0
```

## 5. 最终摘要

```yaml
task_id: 010
primitive_types: [column_detection, ordering, color_reassignment]
input_shape_rule: fixed 9x9
output_shape_rule: fixed 9x9
formal_rule_short: replace each column of 5s with sequential numbers 1..N ordered by first row of appearance (top to bottom)
locality: global
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
main_risk: column count != 4 untested; same-first-row tie-breaking spec assumes column order
confidence: high
```
