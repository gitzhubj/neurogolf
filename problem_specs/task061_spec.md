# Task 061 规范

## 1. 核心规则

- 核心变换：周期补全：识别输入中周期性重复图案，用对应周期值填充零区域。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- M 的确定方式:取最大颜色值还是最大颜色值+1?当前解释取最大颜色值(非零),对 test M=9 成立。风险:low。
- 公式 `(r*c+1) mod M` 中 0 映射为 M:验证所有样例均一致。风险:low。
- 输入中可能有多种非零颜色,公式只依赖于 M(最大颜色),与具体分布无关。风险:low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 9 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Cast+Gather+Greater+OneHot+Pad+ReduceSum+Slice+Sub (9 nodes, 12 initializers)

## 5. 最终摘要

```yaml
task_id: 061
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 9 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Cast+Gather+Greater+OneHot+Pad+ReduceSum+Slice+Sub
actual_nodes: 9
```
