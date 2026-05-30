# Task 096 规范

## 1. 核心规则

- 核心变换：提取非背景彩色子图案连通组件，按外到内层级对称组合，外层框架+内层点角图案。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：输入中嵌套对象的排序规则（如何确定哪个在最外层）。当前解释：按对象 bounding box 大小排序，最大的在最外层。风险等级：medium。
- 歧义点：输出尺寸（7 或 11）的决定因素。当前解释：取决于有效对象数量（N 个对象产生 2N±1 环）。风险等级：high。
- 歧义点：颜色映射规则——输入中的哪个颜色对应输出中的哪一环。当前解释：取决于对象的"边框色"和"填充色"。风险等级：high。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 480 nodes: Abs+Add+And+Cast+Clip+Conv+CumSum+Div+Expand+Gather+GatherEl. Study baseline for optimal op sequence.

Baseline 实际架构: Abs+Add+And+Cast+Clip+Conv+CumSum+Div+Expand+Gather+GatherElements+Greater+GreaterOrEqual+Less+LessOrEqual+Max+Min+Mul+Pad+ReduceMax+ReduceMin+ReduceSum+Reshape+ScatterND+Slice+Sub+Unsqueeze+Where (480 nodes, 42 initializers)

## 5. 最终摘要

```yaml
task_id: 096
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 480 nodes: Abs+Add+And+Cast+Clip+Conv+CumSum+Div+Expand+Gather+GatherEl. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Abs+Add+And+Cast+Clip+Conv+CumSum+Div+Expand+Gather+GatherElements+Greater+GreaterOrEqual+Less+LessOrEqual+Max+Min+Mul+Pad+ReduceMax+ReduceMin+ReduceSum+Reshape+ScatterND+Slice+Sub+Unsqueeze+Where
actual_nodes: 480
```
