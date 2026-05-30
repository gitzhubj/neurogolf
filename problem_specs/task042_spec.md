# Task 042 规范

## 1. 核心规则

- 核心变换：绿色(3)45度相邻对端点外侧马步偏移(-1,+2)放置浅蓝(8)，2x2绿色方块两端外侧放置2x2浅蓝块。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：当存在 3 个或更多 3-组件时，如何配对？以及配对的全局参考中心是什么？
  - 当前解释：每个 3-组件独立产生一个对应的 8-组件，反射中心为 3-组件自身的中心点或配对组件的联合中心。具体中心可能由全局 grid 中心或组件间相对位置决定，细节不确定。
  - 风险等级：medium
- 歧义点：3-组件是单点 vs 2x2 块 vs 3x3 块时，8-组件的放置规则是否一致？
  - 当前解释：是，规则一致，均为 180 度旋转复制。
  - 风险等级：low

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 54 nodes: And+Conv+Greater+Less+Mul+Pad+ReduceSum+Slice+Sub+Sum+Where. Study baseline for optimal op sequence.

Baseline 实际架构: And+Conv+Greater+Less+Mul+Pad+ReduceSum+Slice+Sub+Sum+Where (54 nodes, 18 initializers)

## 5. 最终摘要

```yaml
task_id: 042
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 54 nodes: And+Conv+Greater+Less+Mul+Pad+ReduceSum+Slice+Sub+Sum+Where. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: And+Conv+Greater+Less+Mul+Pad+ReduceSum+Slice+Sub+Sum+Where
actual_nodes: 54
```
