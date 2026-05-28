# Task 038 规范

## 1. 核心规则

- 输入尺寸：9x9。输出尺寸：1x5。
- 输入包含颜色 0（背景）、1（2x2 方块）、2（2x2 方块）以及其他散落颜色。
- 核心规则：将 9x9 网格视为 3x3 的超像素网格（每个超像素为 3x3 子区域）。每个子区域最多含一个 2x2 纯色块。输出 1x5 表示：子区域之间的特定邻接关系（如同色相邻的数量、或特定色对的相邻数）。
- 不确定具体计数的语义，但结构为：输出 1x5 的每个位置对应一种邻接模式（如：1-1 上下相邻、1-1 左右相邻、2-2 相邻、1-2 相邻等），值为 0 或 1 表示该模式是否存在。
- 形式化：
  ```text
  cells = divide 9x9 into 3x3 super-pixels
  for each adjacent pair of cells (i,j) and (i',j'):
      check colors contained
      set output[k] = 1 if specific adjaceny pattern k matches
  ```

## 2. 关键证据

- Train 0：输入含多个 1-块和 2-块，输出 [[1,1,0,0,0]]。
- Train 1：输入排列不同，输出 [[1,1,1,1,0]]。
- Train 2：输出 [[1,1,1,1,0]]。
- Test：输出 [[1,1,1,0,0]]。
- 所有 train 样例均为 9x9→1x5。arc-gen 样例均显示类似 5 位二进制输出。

## 3. 歧义与风险

- 歧义点：1x5 输出中每个位置的具体语义（统计哪种邻接关系）未完全确定。
- 当前采用的解释：5 个位置对应 5 种邻接模式的存在性（0/1）。
- 风险等级：`high`

## 4. NeuroGolf 架构提示

- `recommended_architecture`: `unknown`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_single_conv`
- `nonlinearity_needed`: `unknown`
- 原因：需要将 9x9 分区为 3x3 超像素，识别每个分区中的色块，然后统计邻接关系。涉及空间分区和逻辑计数。

## 5. 最终摘要

```yaml
task_id: "038"
primitive_types: [superpixel, adjacency_counting]
input_shape_rule: 9x9
output_shape_rule: 1x5
formal_rule_short: 统计 3x3 超像素分区中色块的邻接关系
locality: global
single_linear_conv_possible: no
recommended_architecture: unknown
main_risk: 1x5 输出每位语义不确定
confidence: low
```
