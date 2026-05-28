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

- recommended_architecture: unknown
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 涉及尺寸变化和重复平铺, 单一卷积核无法直接实现。需要在 ONNX 中使用 Resize/upsampling 或 tile/concat 操作。如果始终保持 2x 倍率放大, 可用转置卷积(stride=2)近似。

## 5. 最终摘要

```yaml
task_id: 018
primitive_types: [tiling, replication, checkerboard_fill]
input_shape_rule: variable (HxW)
output_shape_rule: 2H x 2W
formal_rule_short: tile input pattern in 2x2 grid, fill gaps with alternating 8/0 checkerboard
locality: global
single_linear_conv_possible: no
recommended_architecture: unknown
main_risk: 填充规则(8/0 交替)细节不确定
confidence: low
```
