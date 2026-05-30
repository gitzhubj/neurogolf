# Task 068 规范

## 1. 核心规则

- 核心变换：唯一出现的非零颜色像素用红色(2)框围成3x3方块标记。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 唯一颜色的定义:出现次数恰好为 1 的颜色。所有样例均满足此条件。风险:low。
- 边框颜色固定为 2(红色):所有样例都使用 2,但规则是否依赖 2 的存在?train 中 2 均存在。风险:low。
- 当唯一色像素位于网格边缘时,3×3 框部分超出边界:当前样例均在内部(距边界至少 1)。风险:low。
- 可能输入中有多个颜色出现 1 次:当前没有出现,但如有,需额外规则选择。风险:medium。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `yes`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 23 nodes: Concat+Conv+Mul+Pad+ReduceSum+Relu+Slice+Sub+Sum. Study baseline for optimal op sequence.

Baseline 实际架构: Concat+Conv+Mul+Pad+ReduceSum+Relu+Slice+Sub+Sum (23 nodes, 11 initializers)

## 5. 最终摘要

```yaml
task_id: 068
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 23 nodes: Concat+Conv+Mul+Pad+ReduceSum+Relu+Slice+Sub+Sum. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Concat+Conv+Mul+Pad+ReduceSum+Relu+Slice+Sub+Sum
actual_nodes: 23
```
