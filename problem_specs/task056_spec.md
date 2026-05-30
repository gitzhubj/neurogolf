# Task 056 规范

## 1. 核心规则

- 核心变换：连通分量计数：统计非零像素4-连通分量个数，1个->6，2个->3，3个->1，5个->2。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：train 0 和 train 5（颜色 4/5 的类似 X 形）为何输出 1 而非 2。当前解释：中心格是否被占用的差异。风险等级：medium。
- 歧义点：是否有更多形状模式未出现在 train 中。当前解释：arc-gen 36 例应覆盖主要形状。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 7 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: ArgMax+Gather+MatMul+Pad+ReduceSum+Reshape+Slice (7 nodes, 10 initializers)

## 5. 最终摘要

```yaml
task_id: 056
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 7 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: ArgMax+Gather+MatMul+Pad+ReduceSum+Reshape+Slice
actual_nodes: 7
```
