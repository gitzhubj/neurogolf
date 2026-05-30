# Task 071 规范

## 1. 核心规则

- 核心变换：大面积色块吸收相邻小面积色块的接触边界像素。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 如何判定哪个颜色被移除？当前解释：颜色中"包围"或"被附属"的一方被移除。风险: `low`。
- 边界像素的判断标准(4-邻域还是 8-邻域)？当前采用 4-邻域连通。风险: `low`。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 49 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Add+And+ArgMax+Cast+Equal+Greater+MatMul+Max+Mul+ReduceMax+ReduceSum+Reshape+Slice+Sub (49 nodes, 12 initializers)

## 5. 最终摘要

```yaml
task_id: 071
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 49 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Add+And+ArgMax+Cast+Equal+Greater+MatMul+Max+Mul+ReduceMax+ReduceSum+Reshape+Slice+Sub
actual_nodes: 49
```
