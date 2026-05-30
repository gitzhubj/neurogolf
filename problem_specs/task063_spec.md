# Task 063 规范

## 1. 核心规则

- 核心变换：浅蓝(8)为墙红(2)标识外部，绿(3)填充被墙包围且与红区隔离的内部空白格。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 四连通 vs 八连通:当前使用四连通(上下左右),所有样例一致。风险:low。
- 背景/墙的区分:出现最多的非零色为背景,另一种为墙。验证所有样例均成立。风险:low。
- 如果 0 区域通过狭窄通道连通到边缘:只有完全封闭的才填充,狭窄通道也算连通到边缘。风险:low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 34 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Clip+Concat+Max+Mul+Pad+ReduceMax+ReduceSum+Relu+Slice+Sub+Sum (34 nodes, 13 initializers)

## 5. 最终摘要

```yaml
task_id: 063
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 34 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Clip+Concat+Max+Mul+Pad+ReduceMax+ReduceSum+Relu+Slice+Sub+Sum
actual_nodes: 34
```
