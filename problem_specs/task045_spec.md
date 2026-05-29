# Task 045 规范

## 1. 核心规则

- 输入输出尺寸相同（均为 10x10）。
- 背景色为 0。每行仅在首列（col 0）和末列（col 9）可能有非零颜色值。
- 核心规则：对于每一行，若首列和末列的颜色相同且非零，则将该行整行填充为该颜色。否则该行保持不变（仅首尾两像素保留原色，中间全为 0）。
- 形式化：

```text
for each row r:
    if input[r][0] == input[r][W-1] and input[r][0] != 0:
        output[r][:] = input[r][0]
    else:
        output[r][:] = input[r][:]
```

- 不涉及任何对象识别或全局操作，纯逐行规则。

## 2. 关键证据

- train 1：row 5 首尾均为 4 → 整行变 4。row 1 首 9 尾 6 → 不变。row 7 首 6 尾 8 → 不变。
- train 2：row 1 首尾均为 8 → 整行 8。row 7 首尾均为 1 → 整行 1。其他行首尾不同 → 不变。
- train 3：row 3 首尾均为 3 → 整行 3。row 7 首尾均为 6 → 整行 6。row 5 首尾不同 → 不变。
- arc-gen 全部支持：首尾同色即全行填充，否则保持。

## 3. 歧义与风险

- 歧义点：如果某行首尾均为 0，是否应填 0？
  - 当前解释：规则仅当首尾同色且非零时触发。首尾均为 0 时保持原样（整行 0）。
  - 风险等级：low
- 未发现主要歧义。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_1x1_conv
- locality: 0
- single_linear_conv_possible: yes
- recommended_kernel: 1x1
- nonlinearity_needed: no (if using conditional logic via mask), or yes (if using ReLU trick)
- 原因：每行输出仅取决于该行的首尾两个像素值。可以用条件 mask（首==尾且非零）来切换"全行填色"或"保持原样"。1x1 Conv 可逐像素实现复制首/尾列值。

## 5. 最终摘要

```yaml
task_id: "045"
primitive_types: ["conditional_row_fill", "edge_comparison"]
input_shape_rule: "same as output, 10x10"
output_shape_rule: "same as input"
formal_rule_short: "if first_col == last_col != 0, fill entire row with that color"
locality: "1 (per row, depends only on row endpoints)"
single_linear_conv_possible: "probably"
recommended_architecture: "single_1x1_conv"
main_risk: "纯粹 1x1 Conv 无 mask 时可能需多层，但可通过广播首尾列实现"
confidence: "high"
```
