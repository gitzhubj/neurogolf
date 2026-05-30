# Task 048 规范

## 1. 核心规则

- 核心变换：若所有红(2)的2x2方块可通过浅蓝(8)的4邻域路径连通，输出8否则输出0。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：平局（count_8 == count_2）时输出什么？
  - 当前解释：输出 [[0]]。部分 arc-gen 样例支持此解释。
  - 风险等级：low
- 歧义点：是否可能不是简单的计数，而是比 bounding box 面积或其他空间属性？
  - 当前解释：计数规则已通过 train 1-2 和多个 arc-gen 验证，置信度高。但极少数 corner case 可能有不同行为。
  - 风险等级：low

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 49 nodes: ArgMax+Cast+Conv+Gather+Greater+Mul+OneHot+Pad+ReduceSum+Res. Study baseline for optimal op sequence.

Baseline 实际架构: ArgMax+Cast+Conv+Gather+Greater+Mul+OneHot+Pad+ReduceSum+Reshape+Slice+Sum+Where (49 nodes, 15 initializers)

## 5. 最终摘要

```yaml
task_id: 048
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 49 nodes: ArgMax+Cast+Conv+Gather+Greater+Mul+OneHot+Pad+ReduceSum+Res. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: ArgMax+Cast+Conv+Gather+Greater+Mul+OneHot+Pad+ReduceSum+Reshape+Slice+Sum+Where
actual_nodes: 49
```
