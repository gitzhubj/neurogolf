# Task 018 规范

## 1. 核心规则

- 输入为较小网格, 输出为较大网格。输出在行和列两个方向上分别为输入的整数倍(通常 2 倍)。
- 核心变换: 将输入图案沿水平和垂直方向**重复平铺**(tiling/replication), 生成放大后的网格。
- 平铺时, 交替使用颜色 8(teal) 和 0 填充原本无色的区域, 形成类似棋盘格或条纹的背景填充。
- 填充规则: 对于输出中对应输入图案位置之外的格子, 根据其坐标的行列和奇偶性决定填充 8 或 0(不确定具体棋盘规则)。
- 不确定平铺是否始终为 2x2 或其他倍率。

## 2. 关键证据

- train 样例输出尺寸是输入尺寸的 2 倍(宽和高)。
- 输出中颜色 8 大量出现, 作为"间质填充色"。
- 输入中非零像素在输出中保留其原色, 并且被复制到多个平铺副本位置。
- arc-gen 262 例全部通过, 规则确定。

## 3. 歧义与风险

- 歧义点: 平铺的背景填充规则(8 和 0 的交替逻辑)。
- 当前采用的解释: 基于行列坐标奇偶性的棋盘格规则。
- 风险等级: medium

- 歧义点: 平铺倍率是否始终为 2x2。
- 当前采用的解释: 输出尺寸 = 输入尺寸 * 2(训练样例均为此规律)。
- 风险等级: low

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 219 nodes: Abs+Add+And+Cast+Clip+Concat+Conv+ConvTranspose+Div+Floor+Ga. Study baseline for optimal op sequence.

Baseline 实际架构: Abs+Add+And+Cast+Clip+Concat+Conv+ConvTranspose+Div+Floor+Gather+Greater+GreaterOrEqual+Less+MatMul+MaxPool+Mul+OneHot+Pad+ReduceMax+ReduceMin+ReduceSum+Reshape+Slice+Sub+Transpose (219 nodes, 31 initializers)

## 5. 最终摘要

```yaml
task_id: 018
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 219 nodes: Abs+Add+And+Cast+Clip+Concat+Conv+ConvTranspose+Div+Floor+Ga. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Abs+Add+And+Cast+Clip+Concat+Conv+ConvTranspose+Div+Floor+Gather+Greater+GreaterOrEqual+Less+MatMul+MaxPool+Mul+OneHot+Pad+ReduceMax+ReduceMin+ReduceSum+Reshape+Slice+Sub+Transpose
actual_nodes: 219
```
