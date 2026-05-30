# Task 004 规范

## 1. 核心规则

- 核心变换：颜色区域右移：每个颜色区域像素右移1格，最底行和最右列边界保持不变。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：连通性判断用 4-邻接还是 8-邻接。当前解释：8-邻接（含对角线），因对角相邻段若按 4-邻接拆分会得出错误底行和最右列。风险等级：low（train 0 中斜向 8 构成的连续臂是关键证据）。
- 歧义点：两个对象右剪切后目标坐标冲突如何裁决。当前解释：可见样例无冲突。风险等级：medium。
- 歧义点：若对象最低行有多行（如对象底部不平），哪些行保持。当前解释：仅 max_row 行保持，其余均右移。因可见对象底行均为单一连续行，无法验证多底行情况。风险等级：medium。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `yes`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 4 nodes: Cast+Conv+Relu. Study baseline for optimal op sequence.

Baseline 实际架构: Cast+Conv+Relu (4 nodes, 4 initializers)

## 5. 最终摘要

```yaml
task_id: 004
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 4 nodes: Cast+Conv+Relu. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Cast+Conv+Relu
actual_nodes: 4
```
