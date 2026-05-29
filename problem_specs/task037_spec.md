# Task 037 规范

## 1. 核心规则

- 输入与输出尺寸相同，均为 10x10。
- 背景色为 0。输入中有若干散落的非零颜色像素（颜色 1–9 中多种）。
- 核心规则：每个非零像素沿 45 度对角线方向"滑落"——具体而言，每个非零像素沿"左下"方向（r+1, c-1）连续移动，直到到达网格边界或被另一个非零像素挡住。
- 不同颜色的像素独立滑落，互不干扰（不同颜色不会相互阻挡，但同色像素如果堆在一起会有相互作用）。
- 形式化描述：对每个非零像素，沿 (dr=+1, dc=-1) 方向移动，直到 r=H-1 或 c=0 或遇到障碍。

## 2. 关键证据

- Train 0：输入中 2 在 (0,2)，滑落到 (2,0)（对角线）；6 在 (0,5)→(1,4)→(2,3)→(3,2)→(4,1)→(5,0)（共滑落 5 步）。
- Train 1：多颜色（9,3,8,7 等）均沿左下对角线滑落。
- Train 2：包含 6,8,4,9 等颜色，滑落模式一致。
- Test：多颜色交叉，输出中所有非零像素均沿左下对角线排列。
- arc-gen 样例支持滑落规则。

## 3. 歧义与风险

- 歧义点：不同颜色的像素是否在滑落过程中相互阻挡。
- 当前采用的解释：所有颜色像素可以"穿过"不同颜色的像素，但同色像素会堆叠。
- 风险等级：`medium`

## 4. NeuroGolf 架构提示

- `recommended_architecture`: `object_logic_required`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_single_conv`
- `nonlinearity_needed`: `yes`
- 原因：每个像素需要沿对角线滑动直到碰壁或被阻挡，涉及条件判断和路径追踪，无法用静态卷积核实现。需要迭代或递归逻辑。

## 5. 最终摘要

```yaml
task_id: "037"
primitive_types: [diagonal_gravity, sliding]
input_shape_rule: 10x10
output_shape_rule: 10x10
formal_rule_short: 非零像素沿左下对角线滑落到底部/左侧边界
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 不同颜色像素的阻挡规则
confidence: medium
```
