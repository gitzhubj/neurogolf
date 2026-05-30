# Task 084 规范

## 1. 核心规则

- 输入/输出尺寸相同（H×W，3×3 到 15×15）。
- 输入仅最左列（col 0）全为同一非零颜色（如 6, 5, 8, 3），其余全部为 0。
- 核心变换：在输入基础上绘制固定的几何图案：
  - 保持左列颜色不变。
  - 从 (0, W-1) 到 (H-2, 1) 画一条颜色 2 的反对角线（每行右移一格）。
  - 底部行（row H-1）从 col 1 到 col W-1 填充颜色 4。
- 图案完全由网格尺寸决定，与输入颜色值无关（仅左列颜色被保留）。

## 2. 关键证据

- train 0：15×15，左列颜色 6。反对角线 2 从 (0,14) 到 (13,1)，底部行填 4。
- train 1：3×3，左列颜色 5。反对角线 2: (0,2)→2, (1,1)→2。底部行 (2,1)-(2,2) 填 4。
- train 2：7×7，同理缩放。
- test 0：10×10，左列颜色 3。反对角线 (0,9)→2 递减到 (8,1)→2，底部行 (9,1-9) 填 4。

## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 257 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Abs+Add+Cast+Less+Mul+ReduceSum+Sub+Sum (257 nodes, 142 initializers)

## 5. 最终摘要

```yaml
task_id: 084
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 257 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Abs+Add+Cast+Less+Mul+ReduceSum+Sub+Sum
actual_nodes: 257
```
