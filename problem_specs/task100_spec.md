# Task 100 规范

## 1. 核心规则

- 核心变换：两个空心矩形框选面积较大框架的颜色，输出该色2x2实心方块，面积相同选更宽的。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：当两个框架面积相等时的选择规则。当前解释：未覆盖，可能按颜色值大小或位置。风险等级：medium。
- 歧义点：框架定义——边框厚度是否为 1 像素？当前解释：是，框架为单像素厚度的空心矩形。风险等级：low。
- 歧义点：输出为何是 2x2 而非其他尺寸。当前解释：固定输出格式，所有样例一致。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 28 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Add+ArgMax+Cast+Expand+Greater+Mul+OneHot+Pad+ReduceSum+Slice+Sub+Unsqueeze+Where (28 nodes, 14 initializers)

## 5. 最终摘要

```yaml
task_id: 100
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 28 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Add+ArgMax+Cast+Expand+Greater+Mul+OneHot+Pad+ReduceSum+Slice+Sub+Unsqueeze+Where
actual_nodes: 28
```
