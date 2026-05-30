# Task 078 规范

## 1. 核心规则

- 核心变换：蓝色(1)形状内部孔洞用红色(2)填充，同时移除原始红色竖线源。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- "内部"的判断标准？当前看是蓝色(1)形状的 4-邻域凹槽。风险: `medium`。
- 蓝色形状边界是否参与判断？蓝色(1)本身不变，只影响 0→2 的位置选择。风险: `low`。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 22 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Concat+Mul+Pad+ReduceSum+Relu+Slice+Sub+Sum (22 nodes, 11 initializers)

## 5. 最终摘要

```yaml
task_id: 078
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 22 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Concat+Mul+Pad+ReduceSum+Relu+Slice+Sub+Sum
actual_nodes: 22
```
