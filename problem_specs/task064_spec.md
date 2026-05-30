# Task 064 规范

## 1. 核心规则

- 核心变换：孤立像素沿直线连接最近的彩色矩形块，用像素自身颜色绘制连接线。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 矩形块的识别:块是连续的矩形区域,颜色唯一。所有样例中块形状规则(矩形),边界明确。风险:low。
- 当种子同时在块的行和列范围内时:应画 L 形折线(水平+垂直)。train[2]种子(6,10)只同行,无此类情况。风险:medium(test 可能遇到)。
- 背景色固定为当前样例中出现最多的颜色,块颜色和种子颜色都是唯一的。风险:low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 48 nodes: And+Cast+Conv+Equal+Gather+Greater+Less+MaxPool+Mul+Pad+Redu. Study baseline for optimal op sequence.

Baseline 实际架构: And+Cast+Conv+Equal+Gather+Greater+Less+MaxPool+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum+Where (48 nodes, 12 initializers)

## 5. 最终摘要

```yaml
task_id: 064
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 48 nodes: And+Cast+Conv+Equal+Gather+Greater+Less+MaxPool+Mul+Pad+Redu. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: And+Cast+Conv+Equal+Gather+Greater+Less+MaxPool+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum+Where
actual_nodes: 48
```
