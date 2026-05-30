# Task 093 规范

## 1. 核心规则

- 核心变换：灰色块沿短边扩张，有色像素使边界沿行/列外扩1格，同行/列多个有色像素扩张累加。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：扩展距离上限不明确。部分样例扩展 1 步，部分可扩展 2 步。当前解释：扩展至多 2 步（先填补中间格，再替换非-5 像素）。风险等级：medium。
- 歧义点：横向条和纵向条情况下扩展逻辑是否对称。当前解释：对称（均为向非-5 像素方向扩展）。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `yes`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 49 nodes: Clip+Concat+Conv+Greater+MaxPool+Mul+Pad+ReduceSum+Relu+Slic. Study baseline for optimal op sequence.

Baseline 实际架构: Clip+Concat+Conv+Greater+MaxPool+Mul+Pad+ReduceSum+Relu+Slice+Sub+Sum+Where (49 nodes, 15 initializers)

## 5. 最终摘要

```yaml
task_id: 093
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 49 nodes: Clip+Concat+Conv+Greater+MaxPool+Mul+Pad+ReduceSum+Relu+Slic. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Clip+Concat+Conv+Greater+MaxPool+Mul+Pad+ReduceSum+Relu+Slice+Sub+Sum+Where
actual_nodes: 49
```
