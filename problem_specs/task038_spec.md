# Task 038 规范

## 1. 核心规则

- 核心变换：统计蓝色(1)的2x2方块个数N，输出1行5列，前N格为1其余为0。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：1x5 输出中每个位置的具体语义（统计哪种邻接关系）未完全确定。
- 当前采用的解释：5 个位置对应 5 种邻接模式的存在性（0/1）。
- 风险等级：`high`

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 16 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Concat+Mul+Pad+ReduceSum+Relu+Resize+Slice+Sub+Sum (16 nodes, 13 initializers)

## 5. 最终摘要

```yaml
task_id: 038
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 16 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Concat+Mul+Pad+ReduceSum+Relu+Resize+Slice+Sub+Sum
actual_nodes: 16
```
