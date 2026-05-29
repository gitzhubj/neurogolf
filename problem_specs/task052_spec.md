# Task 052 规范

## 1. 核心规则

- 输入/输出均为 3×3，固定尺寸。
- 输入包含多种非零颜色（1-9），输出仅使用颜色 5 和 0。
- 核心变换：行均匀性检测。对于每一行，若该行所有 3 个单元格颜色完全相同（即该行全为同一颜色值），则输出该行为 5；否则输出该行为 0。
- 背景色 0 不参与输入的关键判断（全零行不会出现）。

```text
for each row r:
    if input[r][0] == input[r][1] == input[r][2]:
        output[r][:] = 5
    else:
        output[r][:] = 0
```

## 2. 关键证据

- train 0：row0=[4,4,4] 全同 → 输出 row0=5；其余行非全同 → 输出 0。
- train 1：仅 row1=[6,6,6] 全同 → 输出 row1=5。
- train 2：row1=[4,4,4] 全同，row2=[9,9,9] 全同 → 输出 row1=5, row2=5。
- train 3：仅 row2=[1,1,1] 全同 → 输出 row2=5。
- test 0：row0=[4,4,4] 和 row2=[8,8,8] 全同 → 输出 row0=5, row2=5。弧 gen 全部支持。

## 3. 歧义与风险

- 歧义点：若某行全为 0 是否填 5。当前解释：全零行在样例中不存在，推断全零行也符合"全同"规则但 0 不会被选为输出颜色（输出只有 0 和 5，全零行输出为 5 的概率低）。风险等级：low。
- 歧义点：是否存在全 5 输入。当前解释：5 不出现在输入中（cin 为 [1,2,3,4,6,7,9]），不会混淆。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_kxk_conv（至少 3×3 以跨列比较同行元素）
- locality: 1（同行相邻比较）
- single_linear_conv_possible: probably（可用 3×3 Conv 线性实现同行比较，配合阈值检测）
- recommended_kernel: 3x3
- nonlinearity_needed: yes（相等判断需要非线性，线性 Conv 只能做加权求和）
- memory_priority: 3×3 Conv 在 30×30 canvas 上中间张量有限，但需要非线性激活层会增加内存。

## 5. 最终摘要

```yaml
task_id: 052
primitive_types: [row_uniformity_detection, equality_test]
input_shape_rule: fixed 3x3
output_shape_rule: fixed 3x3
formal_rule_short: if all cells in a row have the same color, output 5 for that row, else 0
locality: 1
single_linear_conv_possible: probably
recommended_architecture: single_kxk_conv
main_risk: full-zero row handling unobserved
confidence: high
```
