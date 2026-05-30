# Task 067 规范

## 1. 核心规则

- 核心变换：周期提取：输入水平重复模式周期等于行数H，输出前H列最小周期正方形。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 周期 N 必须是 W 的约数,且最小。所有样例中 N 均整除宽度。风险:low。
- 仅水平方向重复?所有样例水平重复,未涉及垂直方向周期。风险:low。
- 如果输入中某列被 0 部分填充但整体仍保持周期模式,不影响规则(周期由非零模式决定)。风险:low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 7 nodes: Conv+Div+Greater+ReduceMax+ReduceSum+Sum+Where. Study baseline for optimal op sequence.

Baseline 实际架构: Conv+Div+Greater+ReduceMax+ReduceSum+Sum+Where (7 nodes, 4 initializers)

## 5. 最终摘要

```yaml
task_id: 067
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 7 nodes: Conv+Div+Greater+ReduceMax+ReduceSum+Sum+Where. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Conv+Div+Greater+ReduceMax+ReduceSum+Sum+Where
actual_nodes: 7
```
