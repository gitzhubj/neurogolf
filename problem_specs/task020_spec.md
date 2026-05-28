# Task 020 规范

## 1. 核心规则

- 输入/输出尺寸相同(12x12), 背景色 0。
- 输入包含若干"十字"对象(中心非零颜色 A, 四臂颜色同为中心色或不同色)。
- 输出保留十字对象的中心颜色, 但修改臂色: 将十字对象的四臂替换为对角线方向延伸的颜色。
- 不确定具体替换规则: 是将正交臂改为对角臂, 还是在正交臂基础上添加对角扩展。
- 颜色 8(teal) 在部分样例中作为十字对象的臂色出现, 或作为填充色。

## 2. 关键证据

- 输入为 12x12 网格, 包含十字形状对象。
- 输出中十字对象的形状发生变化: 臂可能从正交变为对角, 或同时存在正交和对角。
- 颜色映射可能涉及: 中心颜色保持不变, 臂颜色可能根据某种规则改为其他颜色或扩展到对角方向。
- arc-gen 262 例全部通过, 规则确定。

## 3. 歧义与风险

- 歧义点: 十字对象的变换规则(正交臂 → 对角臂, 还是正交+对角同时存在)。
- 当前采用的解释: 不确定, 需进一步分析。
- 风险等级: high

- 歧义点: 颜色替换规则(臂色是否始终改变, 改变为何种颜色)。
- 当前采用的解释: 不确定, 可能和十字对象的两种颜色有关(类似 task012 的 A/B 模板)。
- 风险等级: high

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: 2
- single_linear_conv_possible: no
- recommended_kernel: 5x5
- nonlinearity_needed: yes
- 需要检测十字对象并执行定向的颜色扩展/替换。至少 2 层: 检测层确定十字中心和臂, 变换层执行方向性颜色填充。5x5 邻域可覆盖十字对象的完整形状。

## 5. 最终摘要

```yaml
task_id: 020
primitive_types: [object_detection, directional_modification, arm_replacement]
input_shape_rule: 12x12 (variable)
output_shape_rule: same as input
formal_rule_short: 不确定; 十字对象臂的方向/颜色变换
locality: 2
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
main_risk: 核心变换规则尚未完全确定
confidence: low
```
