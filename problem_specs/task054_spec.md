# Task 054 规范

## 1. 核心规则

- 输入输出尺寸相同（H×W → H×W）。
- 背景色/边界色（通常为 8、1 或 4）将网格划分为若干矩形区域，区域内填充单一主色。
- 核心变换：区域内的"特殊格"（颜色与区域主色不同）沿水平和垂直方向投影，画出十字线。
- 投影线从特殊格出发，沿 4 个方向延伸直到碰到边界色或网格边缘，线的颜色为特殊格颜色。
- 区域主色格在不被投影线覆盖时保持不变；被覆盖时替换为投影线颜色。
- 多条投影线相交时，存在颜色优先级规则（深浅/数值大小可能决定优先级）。

## 2. 关键证据

- train 0：30×30。边界 8，左侧区域主色 1，特殊格颜色 2/3/4 分布其中。输出在特殊格的行和列上画出颜色 2 的投影线，局部交点为 3。
- train 1：30×30。边界 1，两个区域主色 2，特殊格颜色 3/4。输出画十字线。
- train 2：30×30。边界 8，多个区域，特殊格颜色 4/5/6。
- 所有样例中投影线严格遵守边界色停止规则。
- arc-gen 262 例覆盖多种区域形状。

## 3. 歧义与风险

- 歧义点：多线相交时的颜色优先级。当前解释：颜色值较大的优先。风险等级：medium。
- 歧义点：区域自动检测算法（如何区分边界色、主色、特殊格）。当前解释：边界色为全网格中出现频率最高且形成连续边界的颜色。风险等级：medium。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required（需要区域检测 + 射线投影）
- locality: global（投影线可横跨整个区域）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes

## 5. 最终摘要

```yaml
task_id: 054
primitive_types: [region_detection, ray_casting, crosshair_drawing]
input_shape_rule: same as output
output_shape_rule: same as input
formal_rule_short: for each special-colored cell, draw crosshair lines in all 4 directions until hitting boundary color
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: color priority at line intersections uncertain
confidence: medium
```
