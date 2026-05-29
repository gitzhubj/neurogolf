# Task 028 规范

## 1. 核心规则

- 输入/输出尺寸相同（变化尺寸，例如 5x10、10x10）。
- 背景色为 0。输入包含多个不同颜色的连通块（颜色如 1=蓝、2=红、4=黄），各块形状固定（如 2x2 方块或 L 形）。
- 核心规则：将所有彩色块沿垂直方向对齐到同一行（对齐到所有块中最小行坐标），保持各块的内部形状和左右顺序不变。
- 形式化表达：
  ```text
  找到所有非零像素组成的连通块 B₁, B₂, ..., Bₙ。
  设 min_row = min(top_row(Bᵢ) for all i)。
  对每个块 Bᵢ: 将其垂直平移到 min_row（即向上平移 top_row(Bᵢ) - min_row）。
  输出为平移后的结果。未覆盖位置填 0。
  ```
- 块的水平相对位置保持不变。
- arc-gen 样例全部支持该规则。

## 2. 关键证据

- train[0]（5x10）：三个块分别在 rows 0-1（红 2）、rows 1-2（蓝 1）、rows 2-3（黄 4）。输出将所有块对齐到 rows 1-2。
- train[1]（10x10）：多个块分散在不同行，输出全部对齐到同一行区间。
- train[2]（5x10）：散落像素同样被上提到对齐行。
- 测试样例：同样模式，块对齐。

## 3. 歧义与风险

- 歧义点：对齐行的选择方式（最小行 vs 最大行 vs 中位行）。当前样例中所有块被提到同一区间。
- 当前采用的解释：所有块上移到最小 top_row 的位置。
- 风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：需要先识别各连通块，计算每个块的 top_row，然后对每个块做垂直平移。这需要连通组件分析和对象级操作。

## 5. 最终摘要

```yaml
task_id: 028
primitive_types: [object_detection, vertical_translation, block_alignment]
input_shape_rule: variable, same as output
output_shape_rule: same as input
formal_rule_short: 所有彩色块垂直对齐到最小 top_row，保持形状和左右顺序
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 对齐方向可能有变体
confidence: medium
```
