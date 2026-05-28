# Task 047 规范

## 1. 核心规则

- 输入输出尺寸相同（均为 9x9）。
- 背景色为 0。输入中仅有 2 个非零像素：一个 8 (cyan) 和一个 7 (orange)。
- 核心规则：从 8 像素出发，先垂直向上画线（颜色 8）至 grid 顶部边界，再从该点水平向右画线（颜色 8）至 7 像素的列位置。从 7 像素出发，先水平向左画线（颜色 7）至 8 像素的列位置，再垂直向下画线（颜色 7）至 grid 底部边界。两线交点处颜色为 2 (red)。
- 形式化：设 8 位于 (r8, c8)，7 位于 (r7, c7)。

```text
拐点 = (r8, c7)   # 8 的垂直路径与 7 的水平路径交汇处
# 8 的路径
for row from 0 to r8:      output[row][c8] = 8
for col from c8 to c7:     output[r8][col] = 8
# 7 的路径
for col from c8 to c7:     output[r7][col] = 7
for row from r7 to H-1:    output[row][c7] = 7
# 交点
output[r8][c7] = 2
# 7 先行（左）后下：交点以前路径的输出覆盖规则见下
```

- 路径交点 (r8, c7) 使用颜色 2。在拐点处，8 的水平线和 7 的水平线在 row r7 和 row r8 可能重叠或相交。

## 2. 关键证据

- train 1：8 在 (2,2)，7 在 (6,6)。输出：8 的垂直线 col 2 row 0–2，8 的水平线 row 2 col 2–6；7 的水平线 row 6 col 2–6，7 的垂直线 col 6 row 6–8；交点 (2,6) 为 2。
- train 2：8 在 (1,3)，7 在 (7,6)。同样的 L 形连接，拐点颜色 2。
- arc-gen 全部支持此规则：两色分别走 L 形路径交汇，交点色 2。

## 3. 歧义与风险

- 歧义点：8 的垂直线是先向上到 row 0 还是先向上到 min(r8, 0)？
  - 当前解释：从 8 所在行向上直画到 row 0（顶部边界）。
  - 风险等级：low
- 歧义点：拐点处 8/7/2 的覆盖优先级如何？如果 r8 == r7 或 c8 == c7 怎么办？
  - 当前解释：拐点固定为 2。若 r8==r7 则水平线重合（无垂直段）。观测中未见这种情况，按常规处理。
  - 风险等级：low

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global（需要知道两个点的全局坐标来画线）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：需要定位两个特定颜色的像素的全局坐标，然后沿轴绘制线段，属于"画线"任务，Conv 无法直接实现。

## 5. 最终摘要

```yaml
task_id: "047"
primitive_types: ["line_drawing", "L_shape_routing"]
input_shape_rule: "same as output, 9x9"
output_shape_rule: "same as input"
formal_rule_short: "draw L-lines from 8 (up then right) and 7 (left then down), intersection=2"
locality: "global"
single_linear_conv_possible: "no"
recommended_architecture: "object_logic_required"
main_risk: "两点重合或共线时行为已推定为合理"
confidence: "high"
```
