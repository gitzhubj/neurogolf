# Task 055 规范

## 1. 核心规则

- 输入输出尺寸相同。
- 输入由颜色 8 的十字网格线（水平和垂直方向）将画面分割为多个矩形区块。区块内填充 0。
- 核心变换：为每个被 8-网格线包围的矩形区块分配一个颜色，填充整个区块。
- 颜色分配规则：预定义的固定颜色序列，按区块位置分配。左侧/上方区块为颜色 2，下方为颜色 1，中间水平带为颜色 6 或 4 等。
- 8-网格线本身在输出中保持不变。
- 区块颜色与输入内容无关（输入区块全为 0），仅依赖区块的网格位置。

## 2. 关键证据

- train 0：18×19。两条水平 8-线（row 2 和 row 7）和两条垂直 8-线（col 4 和 col 11）分 6 个区块。输出颜色自上而下：2（顶部三区块）、4+6+3（中间带左中右）、1（底部区块）。
- train 1：12×14。水平 8-线在 row 4 和 row 7，垂直 8-线在 col 2 和 col 9。类似颜色分配模式。
- test 0：模式一致。
- arc-gen 262 例支持。

## 3. 歧义与风险

- 歧义点：颜色分配的具体规则（基于区块索引还是固定模板）。当前解释：基于网格拓扑位置的固定颜色查找表。风险等级：medium。
- 歧义点：不同样例间颜色具体值变化。当前解释：每种网格拓扑有自己的颜色映射，颜色值与输入无关。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_1x1_conv（固定颜色查找表，按区块位置分配）
- locality: 0
- single_linear_conv_possible: probably（若颜色分配仅依赖行列索引，1x1 Conv 可行）
- recommended_kernel: 1x1
- nonlinearity_needed: no

## 5. 最终摘要

```yaml
task_id: 055
primitive_types: [grid_fill, region_coloring, fixed_palette]
input_shape_rule: same as output
output_shape_rule: same as input
formal_rule_short: fill each rectangle region bounded by color-8 gridlines with a predefined color based on region position
locality: 0
single_linear_conv_possible: probably
recommended_architecture: single_1x1_conv
main_risk: color assignment rule not fully determined
confidence: medium
```
