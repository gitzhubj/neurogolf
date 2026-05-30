# Task 001 规范

## 1. 核心规则

- 核心变换：模式平铺：3x3输入平铺为9x9输出，每个3x3子块在输入对应位置非零时复制输入图案，否则全零。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：若同一输入包含多种前景色，输出颜色如何确定（按 block selector、按 tile cell、或需相等门控）。当前解释：按 tile cell 颜色输出。风险等级：medium（所有可见样例只有一种前景色，无法区分）。
- 歧义点：NeuroGolf 30x30 canvas 中 9x9 外区域是否需显式置零。当前解释：裁剪忽略。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 12 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Cast+Concat+Gather+Or+Pad+ReduceMax+Slice+Tile+Where (12 nodes, 4 initializers)

## 5. 最终摘要

```yaml
task_id: 001
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 12 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Cast+Concat+Gather+Or+Pad+ReduceMax+Slice+Tile+Where
actual_nodes: 12
```
