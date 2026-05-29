# Task 017 规范

## 1. 核心规则

- 输入/输出尺寸相同(通常为 10x10), 背景色 0。
- 输入包含若干非零颜色组成的图案(菱形/交叉排列), 位于网格上半部或局部区域。
- 输出将输入图案以垂直中线为对称轴进行镜像复制: 将图案中每个非零像素的颜色和位置, 沿水平方向对称复制到空白区域。
- 图案的对称复制保持"图案内交替颜色"的关系不变: 如果图案内颜色 A 和 B 交替出现, 复制后仍保持 A/B 交替。
- 复制后的输出中, 原始图案仍保留在原位置。

## 2. 关键证据

- train 1 输入: 菱形图案(颜色 3,8,2)在网格左侧, 输出将图案对称复制到右侧。
- train 2 输入: 菱形图案(颜色 2,3,4)在网格上半部, 输出在下方补充对称图案。
- test 输入: 图案(颜色 1,4,2)在网格左侧/上方, 输出需对称填充。
- 填充位置为原图案关于某对称轴(垂直或水平)的镜像位置, 颜色保持不变。
- arc-gen 262 例全部通过, 规则确定。

## 3. 歧义与风险

- 歧义点: 对称轴的具体位置(是网格的正中线还是图案自身的对称轴)。
- 当前采用的解释: 网格的几何中线, 或图案的"自然对称轴"(即图案到镜像的距离等于镜像到边界的距离)。
- 风险等级: medium

- 歧义点: 多个不相连的图案如何处理。
- 当前采用的解释: 每个独立图案分别做镜像, 互不影响。
- 风险等级: low

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 对称复制需要识别图案的边界/轴心, 然后翻转并复制。这涉及非局部的坐标变换, 单一 kxk 卷积无法实现全局翻转。需要在 ONNX 中实现坐标翻转 + gather/scatter 或使用转置卷积。

## 5. 最终摘要

```yaml
task_id: 017
primitive_types: [symmetry, mirror_copy, pattern_completion]
input_shape_rule: same as output (variable)
output_shape_rule: same as input
formal_rule_short: mirror-copy pattern across symmetry axis to fill empty region
locality: global
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
main_risk: 对称轴位置的确定
confidence: medium
```
