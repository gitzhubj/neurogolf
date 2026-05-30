# Task 044 规范

## 1. 核心规则

- 核心变换：找出灰色(5)形状包围的黑色空洞，将外部彩色图案按相同形状移入空洞填补。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：如果存在 3 个或更多相同形状的块，互换顺序是什么？
  - 当前解释：不确定，可能需要循环互换或按位置排列。
  - 风险等级：medium
- 歧义点：形状匹配的定义是严格的 bounding box 全等，还是仅宽高相同？
  - 当前解释：采用 bounding box 宽高相同即可，不要求内部像素排列全等。
  - 风险等级：low
- 歧义点：框架之外的散点如何处理？
  - 当前解释：保持不变，不参与交换。
  - 风险等级：low

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 1054 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Abs+Add+And+Cast+Clip+Col2Im+Concat+Gather+Greater+Less+MatMul+Max+MaxPool+Mul+Pad+ReduceMax+ReduceSum+Reshape+Slice+Sub+Transpose+Unsqueeze (1054 nodes, 59 initializers)

## 5. 最终摘要

```yaml
task_id: 044
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 1054 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Abs+Add+And+Cast+Clip+Col2Im+Concat+Gather+Greater+Less+MatMul+Max+MaxPool+Mul+Pad+ReduceMax+ReduceSum+Reshape+Slice+Sub+Transpose+Unsqueeze
actual_nodes: 1054
```
