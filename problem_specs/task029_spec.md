# Task 029 规范

## 1. 核心规则

- 输入/输出尺寸相同（10x10）。
- 背景色为 0（黑色）。输入中仅有 2 个非零像素，颜色分别为 C1 和 C2（如 6=品红和 7=橙色，或 1=蓝和 4=黄）。
- 与 task027 相同的模式：两个彩色像素的行坐标 r1, r2（r1 < r2）将输出分为三个区域：
  - 区域 1 (rows 0..r1)：用 C1 绘制外框（首行满 C1，两侧竖线 C1）。
  - 区域 2 (rows r1+1..r2-1)：用 C2 绘制两侧竖条。
  - 区域 3 (rows r2..H-1)：用 C2 绘制间隔满行。
- 该任务与 task027 属于同一模板的不同实例（不同颜色组合）。
- arc-gen 样例支持该规则。

## 2. 关键证据

- train[0] 和 train[1] 均显示两像素输入 -> 三段式框架输出。
- 与 task027 的结构完全一致，仅颜色不同。
- 测试样例同样为两像素输入 -> 框架输出。

## 3. 歧义与风险

- 歧义点：与 task027 的区别是什么（可能仅颜色不同）。
- 当前采用的解释：与 task027 相同规则，仅颜色不同。
- 风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 88 nodes: Add+ArgMax+Cast+Conv+Equal+Gather+Greater+Less+Mul+ReduceMax. Study baseline for optimal op sequence.

Baseline 实际架构: Add+ArgMax+Cast+Conv+Equal+Gather+Greater+Less+Mul+ReduceMax+ReduceMin+ReduceSum+Squeeze+Sub+Unsqueeze+Where (88 nodes, 15 initializers)

## 5. 最终摘要

```yaml
task_id: 029
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 88 nodes: Add+ArgMax+Cast+Conv+Equal+Gather+Greater+Less+Mul+ReduceMax. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Add+ArgMax+Cast+Conv+Equal+Gather+Greater+Less+Mul+ReduceMax+ReduceMin+ReduceSum+Squeeze+Sub+Unsqueeze+Where
actual_nodes: 88
```
