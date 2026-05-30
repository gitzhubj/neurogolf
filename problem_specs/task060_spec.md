# Task 060 规范

## 1. 核心规则

- 输入/输出均为 5×11。
- 输入中在某一行（如 row 1 或 row 3）的最左列和最右列各有一个非零颜色（形成一对颜色端点）。
- 核心变换：对每一对有颜色端点的行，从左端点的颜色开始，填充该行左半部分（col 0 到 col 4）；在正中间列（col 5）填充颜色 5（灰色分隔符）；从 col 6 到 col 10 填充右端点的颜色。
- 如果某行的端点是不同颜色对（如 train[0] row1 有 1 和 2，test[0] 还有多行），每行独立处理。
- 没有颜色端点的行保持全零。
- 多对颜色可以出现在不同行中（如 test 有两行有颜色对）。

```text
for each row r:
    left_color = leftmost non-zero cell in row r
    right_color = rightmost non-zero cell in row r
    if left_color and right_color exist:
        for each col c:
            if c < mid: output[r][c] = left_color
            elif c == mid: output[r][c] = 5
            else: output[r][c] = right_color
```

## 2. 关键证据

- train 0：row 1 有左端点颜色 1（col 0）和右端点颜色 2（col 10）。输出 row 1：col 0-4 为 1，col 5 为 5，col 6-10 为 2。
- train 1：row 3 有左端点颜色 3 和右端点颜色 7。输出 row 3 同理填充。
- test 0：有两对端点（row 1 有 4 和 8，row 3/4 有 6 和 9），每行独立填充，中线 col 5 为灰色 5。

## 3. 歧义与风险

- 歧义点：若同一行有多个非零颜色（非仅左右端点）。当前解释：取最左和最右的非零格颜色作为端点。风险等级：low。
- 歧义点：中线颜色始终为 5。当前解释：5 是固定的分隔符，不依赖端点颜色。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Multi-op custom architecture (16 nodes). Study baseline directly.
- `fusion_hint`: Ops used: Mul+Pad+Slice+Sub+Sum...

Baseline 实际架构: Mul+Pad+Slice+Sub+Sum (16 nodes, 18 initializers)

## 5. 最终摘要

```yaml
task_id: 060
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
memory_priority: Multi-op custom architecture (16 nodes). Study baseline directly.
fusion_hint: Ops used: Mul+Pad+Slice+Sub+Sum...
main_risk: high — complex architecture, refer to baseline
confidence: medium
actual_ops: Mul+Pad+Slice+Sub+Sum
actual_nodes: 16
```
