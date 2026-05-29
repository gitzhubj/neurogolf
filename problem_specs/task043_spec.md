# Task 043 规范

## 1. 核心规则

- 输入输出尺寸相同（均为 10x10）。
- 背景色为 0，关键颜色：5 (gray) 和 2 (red)。
- 核心规则：第 0 行（最顶行）包含一个由 5 组成的模式（pattern）。对于每一行 r，如果该行最右列为 5，则将该行的模式复制自第 0 行的模式，但将颜色 5 替换为 2。即：
  - 若 input[r][W-1] == 5，则 output[r][c] = 2 if input[0][c] == 5 else 0。
  - 若 input[r][W-1] != 5，则该行不变（保持原 input 内容，其中任何 5 保持 5，2 保持为 0）。
- 形式化：

```text
pattern_row = input[0]
for each row r:
    if input[r][W-1] == 5:
        for each col c:
            output[r][c] = 2 if pattern_row[c] == 5 else 0
    else:
        output[r][c] = input[r][c]
```

## 2. 关键证据

- train 1：row 0 模式为 "5,0,0,5,0,0,0,5,0,0"；row 3 和 row 7 最右列为 5，输出 row 3 和 row 7 出现对应位置的 2。
- train 2：row 0 模式为 "0,5,0,5,5,0,0,5,0,0"；row 2/4/7/9 最右列有 5，这些行获得模式替换。
- train 3：row 0 模式为 "0,0,5,5,0,5,0,5,5,0"；row 2/3/6/8/9 最右列为 5，获得模式替换。
- arc-gen 全部支持此规则，模式复制+颜色替换一致。

## 3. 歧义与风险

- 歧义点：如果行已有非零内容（2 或 5）且最右列为 5，模式复制是否会覆盖原有内容？
  - 当前解释：是，模式复制覆盖整行，原内容被替换。
  - 风险等级：low
- 未发现主要歧义。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_1x1_conv + logic
- locality: global（需要读取第 0 行模式并广播到其他行）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：需要条件判断（最右列是否为 5）来决定是否复制模式，1x1 Conv 无法实现条件分支。但如果将"条件复制"建模为两个 1x1 Conv（一个做模式广播、一个做 mask），配合逐元素乘法可实现。

## 5. 最终摘要

```yaml
task_id: "043"
primitive_types: ["conditional_pattern_copy", "color_remap"]
input_shape_rule: "same as output, 10x10"
output_shape_rule: "same as input"
formal_rule_short: "if row's last col is 5, copy row0's 5-pattern as 2s"
locality: "global (per row)"
single_linear_conv_possible: "no"
recommended_architecture: "multi_layer_conv_relu"
main_risk: "覆盖行为已明确"
confidence: "high"
```
