# Task 041 规范

## 1. 核心规则

- 输入输出尺寸相同（10x10 或类似）。
- 背景色为 0 (black)，非零色构成离散的颜色组（每组的颜色相同且唯一）。
- 核心规则：对每一行，对每一种在该行出现的颜色，将该行中该颜色的最左和最右出现位置之间的所有单元格填充为该颜色。
- 形式化：

```text
for each row r:
    for each color c in unique colors in input[r]:
        left = min(col where input[r][col] == c)
        right = max(col where input[r][col] == c)
        if left < right:
            output[r][left ... right] = c
        else:
            output[r][left] = c
    cells without assignment remain as input
```

- 每个颜色组独立处理，颜色之间互不干扰。

## 2. 关键证据

- train 1：绿色(3)在 row 1 的 col 1 和 col 8，输出 row 1 的 col 1–8 全部为 3。row 4 的 col 4 和 col 5 相邻，无需填充。
- train 2：存在 3 种颜色 (1, 4, 及 row 0 和 row 6–9 中的 4)，每种颜色的最左/最右填充分别独立生效。
- train 3：颜色 6 和 8 同时存在于同一行但互不干扰，每色仅在其自身区间内填充。
- arc-gen 全部支持行内最左最右填充规则，不同颜色、不同物体形状均遵循此规则。

## 3. 歧义与风险

- 歧义点：如果某行中某颜色仅出现一次（left==right），是否应保持原样？
  - 当前解释：是，保持原样，不需要填充。
  - 风险等级：low
- 未发现主要歧义。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Multi-op custom architecture (18 nodes). Study baseline directly.
- `fusion_hint`: Ops used: And+Cast+Concat+CumSum+Not+Or+Pad+Slice+Split...

Baseline 实际架构: And+Cast+Concat+CumSum+Not+Or+Pad+Slice+Split (18 nodes, 6 initializers)

## 5. 最终摘要

```yaml
task_id: 041
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
memory_priority: Multi-op custom architecture (18 nodes). Study baseline directly.
fusion_hint: Ops used: And+Cast+Concat+CumSum+Not+Or+Pad+Slice+Split...
main_risk: high — complex architecture, refer to baseline
confidence: medium
actual_ops: And+Cast+Concat+CumSum+Not+Or+Pad+Slice+Split
actual_nodes: 18
```
