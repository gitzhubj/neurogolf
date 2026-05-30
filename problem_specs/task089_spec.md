# Task 089 规范

## 1. 核心规则

- 输入/输出均为 13×13（固定尺寸）。
- 输入中包含一个"源图案"（2×2 或 3×3 的小型形状，由 2-3 种颜色组成）和若干"目标标记格"（分布在网格各处的孤立非零颜色格）。
- 核心变换：将源图案复制到每个目标标记格的位置。目标标记格的颜色用于确定图案的锚点（即图案中哪种颜色应对齐到标记位置）。
- 复制时，图案以标记格为锚点覆盖周围区域（锚点颜色在图案中的相对位置决定了图案的粘贴偏移）。
- 原始图案和原始输入中不被覆盖的格子保持不变。

## 2. 关键证据

- train 0：源图案 2×2（颜色 1,2），标记 2（仅一个标记格）。输出复制图案到标记位置，锚点 2 对齐。
- train 1：源图案 3×3（颜色 4,3），标记 3（多个）。输出在标记位置各粘贴一份图案。
- train 2：源图案 3×2（颜色 8,3），标记 2 和 4。输出在相应位置粘贴。
- train 3：多个不同颜色的源图案和标记，每个标记选择锚点颜色匹配的源图案复制。
- 各 train 样例中，图案复制保留全部颜色和形状。

## 3. 歧义与风险

- 歧义点：若有多个源图案或多个标记时，如何匹配标记和图案。当前解释：标记颜色匹配源图案中的某颜色作为锚点。风险等级：medium。
- 歧义点：复制时超出网格边界。当前解释：截断。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 181 nodes: Cast+Concat+Conv+Gather+Greater+MaxPool+Mul+Pad+ReduceSum+Sl. Study baseline for optimal op sequence.

Baseline 实际架构: Cast+Concat+Conv+Gather+Greater+MaxPool+Mul+Pad+ReduceSum+Slice+Sub+Sum (181 nodes, 25 initializers)

## 5. 最终摘要

```yaml
task_id: 089
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 181 nodes: Cast+Concat+Conv+Gather+Greater+MaxPool+Mul+Pad+ReduceSum+Sl. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Cast+Concat+Conv+Gather+Greater+MaxPool+Mul+Pad+ReduceSum+Slice+Sub+Sum
actual_nodes: 181
```
