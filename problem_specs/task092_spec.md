# Task 092 规范

## 1. 核心规则

- 核心变换：同色像素对用水平/垂直线连接，灰色(5)大块朝有色像素方向外扩1格，交叉点垂直线优先。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：若某颜色在多个行或列各有配对。当前解释：所有行和所有列独立处理。风险等级：low。
- 歧义点：纵向/横向优先级在不同颜色间是否固定为纵向获胜。当前解释：是，纵向填充在横向之后执行（或其他等价机制）。风险等级：medium。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 42 nodes: And+Cast+Conv+Equal+Greater+MaxPool+Mul+ReduceMax+ReduceSum+. Study baseline for optimal op sequence.

Baseline 实际架构: And+Cast+Conv+Equal+Greater+MaxPool+Mul+ReduceMax+ReduceSum+Slice+Where (42 nodes, 9 initializers)

## 5. 最终摘要

```yaml
task_id: 092
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 42 nodes: And+Cast+Conv+Equal+Greater+MaxPool+Mul+ReduceMax+ReduceSum+. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: And+Cast+Conv+Equal+Greater+MaxPool+Mul+ReduceMax+ReduceSum+Slice+Where
actual_nodes: 42
```
