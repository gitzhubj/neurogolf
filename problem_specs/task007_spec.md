# Task 007 规范

## 1. 核心规则

- 核心变换：对角线序列平铺：提取反对角线上非零颜色序列，沿对角线方向循环填充整个输出。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：压实方向是向上还是向下堆积。当前解释：由上往下堆积，顶部对象保持或上移至 grid 顶部，后续对象紧接前一个对象底部。风险等级：low（train 0 中顶部对象下沉而非上移，暗示可能按某种对齐规则）。实际需要更多分析确定精确对齐规则。
- 歧义点：对象水平位置是否改变。当前解释：水平位置不变。但需要验证 train 0 中颜色 2 对象的水平位置变化是压实副作用还是独立规则。风险等级：medium。
- 歧义点：对象间距（压实后相邻对象之间留多少空白行）。当前解释：0 或 1 行空白，取决于具体对齐。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 13 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: ArgMax+Concat+OneHot+Pad+ReduceMax+Reshape+Slice+Tile+Unsqueeze (13 nodes, 13 initializers)

## 5. 最终摘要

```yaml
task_id: 007
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 13 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: ArgMax+Concat+OneHot+Pad+ReduceMax+Reshape+Slice+Tile+Unsqueeze
actual_nodes: 13
```
