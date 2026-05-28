# Task 040 规范

## 1. 核心规则

- 输入与输出尺寸相同，均为 10x10。
- 关键颜色：0（背景）、3（"待填充"标记色），以及边界颜色（分布在输入上下/左右边缘的非零、非 3 颜色）。
- 核心规则：每个值为 3 的像素，用离它最近的边界颜色替换。边界颜色位于网格的上下/左右边缘上（row=0、row=9、col=0、col=9 中包含的非零、非 3 色块）。
- 更精确的规则：网格被边界颜色沿垂直或水平方向"分区"。每个 3 的取值取决于它在哪个边界颜色的"影响范围"内——即距离哪个边界色块的行/列更近。
- 形式化：
  ```text
  for each cell (r,c) where input[r,c] == 3:
      find nearest boundary marker cell (rb, cb) with color B != 0, B != 3
      output[r,c] = B
  ```
- 其他单元格保持不变。

## 2. 关键证据

- Train 0：左列全为 1，右列全为 2。内部 3 按左右分半——靠近左侧的 3→1，靠近右侧的 3→2。
- Train 1：顶行全为 4，底行全为 7。内部 3 按上下分半——上半 3→4，下半 3→7。
- Train 2：顶行为 8，底行为 9。内部 3 按上下分半——上半→8，下半→9。
- Test：左列 5，右列 4，顶部有额外标记 3。内部 3 按左右分半填 5 或 4。
- arc-gen 样例均支持该填充规则。

## 3. 歧义与风险

- 歧义点：当水平和垂直边界同时存在时（如 test 中），如何确定分界线。
- 当前采用的解释：按照最近边界的原则——若水平和垂直边界距离相等，可能有特定的优先级规则。
- 风险等级：`medium`

## 4. NeuroGolf 架构提示

- `recommended_architecture`: `object_logic_required`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_single_conv`
- `nonlinearity_needed`: `yes`
- 原因：需要全局识别边界颜色位置，然后对每个 3 计算最近边界颜色进行替换。涉及距离计算和条件赋值。

## 5. 最终摘要

```yaml
task_id: "040"
primitive_types: [fill, nearest_neighbor, boundary_detection]
input_shape_rule: 10x10
output_shape_rule: 10x10
formal_rule_short: 每个 3 用最近边界颜色替换
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 多边界时的优先级规则
confidence: medium
```
