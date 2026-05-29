# Task 013 规范

## 1. 核心规则

- 输入和输出尺寸相同, 背景色为 0。
- 输入包含若干"种子"像素(非零颜色), 分布在网格中, 具有长轴方向和一定的间距。
- 输出沿长轴方向延伸出周期性的交替颜色条纹。
- 条纹规则: 从种子沿长轴的垂直方向向外, 以固定间距交替放置两种颜色(种子颜色和另一交替颜色)。
- 不确定具体的长轴判定方法和交替颜色配对规则, 但从 through 率来看(4/4 train, 1/1 test, 262/262 arc-gen), 规则是确定的, 可被卷积网络学习。

## 2. 关键证据

- 输入为稀疏点阵, 输出为周期条纹图案。
- 条纹方向由种子所在区域的"长轴"(主方向)决定。
- 条纹在输出中以种子间距为周期, 交替使用两种颜色。
- arc-gen 262 例全部通过 with-spec 基线, 规则可学习实现。

## 3. 歧义与风险

- 歧义点: 长轴判定标准(如何从多个种子中选择主方向)。
- 当前采用的解释: 基于种子分布的 PCA 或几何主方向分析, 计算其最大扩展方向。
- 风险等级: medium(具体算法细节尚待验证, 但基于卷积的方案可规避精确几何推理)。

- 歧义点: 交替颜色的配对规则。
- 当前采用的解释: 颜色来自输入中种子的颜色及其配对色, 配对可能基于固定颜色表。
- 风险等级: medium

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: k
- single_linear_conv_possible: no
- recommended_kernel: 5x5 or larger
- nonlinearity_needed: yes
- 条纹生成需要方向性卷积和周期性激活。不能简化为单一 1x1 或 kxk 卷积。需要多层: 检测层确定方向/间距, 生成层沿方向绘制交替条纹。

## 5. 最终摘要

```yaml
task_id: 013
primitive_types: [direction_detection, stripe_generation, periodicity]
input_shape_rule: same as output (variable)
output_shape_rule: same as input
formal_rule_short: extend periodic alternating-color stripes along dominant axis from seed pixels
locality: k
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
main_risk: 长轴判定和颜色配对规则细节不确定
confidence: low
```
