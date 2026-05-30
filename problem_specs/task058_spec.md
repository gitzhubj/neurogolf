# Task 058 规范

## 1. 核心规则

- 核心变换：递归方形螺旋：全零输入生成绿色(3)方形递归螺旋边框图案。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：迷宫生成的确切算法（是标准螺旋还是特定生成规则）。当前解释：从 (1,1) 开始的逆时针螺旋路径，宽度为 1 格。风险等级：low（arc-gen 覆盖多种尺寸）。
- 歧义点：偶数尺寸和非正方形的情况。当前解释：train 有非正方形样例（10×10 等），规则一致。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 15 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: And+Cast+Concat+Gather+Greater+Not+Pad+ReduceMax+ReduceSum+Reshape+Slice+Sub (15 nodes, 11 initializers)

## 5. 最终摘要

```yaml
task_id: 058
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 15 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: And+Cast+Concat+Gather+Greater+Not+Pad+ReduceMax+ReduceSum+Reshape+Slice+Sub
actual_nodes: 15
```
