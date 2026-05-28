# Task 025 规范

## 1. 核心规则

- 输入 5x7，输出 5x3。
- 背景色为 0。关键颜色：9（栗色）、1（蓝色）、8（青色）。
- 输入第 4 列（0-indexed 即 col=3）整列为 1（蓝色），作为垂直分隔线，将输入分为左半（cols 0-2）和右半（cols 4-6），各为 5x3。
- 对每个位置 (r, c) for c in 0..2：如果输入左半 `input[r][c] == 9` 且右半 `input[r][c+4] == 9`，则输出 `output[r][c] = 8`；否则 `output[r][c] = 0`。
- 形式化表达：
  ```text
  for r in 0..4, for c in 0..2:
      output[r][c] = 8 if input[r][c] == 9 and input[r][c+4] == 9 else 0
  ```
- 本质是按位 AND 操作：两个 5x3 区域逐像素比较，两者均为 9 时输出 8。

## 2. 关键证据

- train[0]（5x7 -> 5x3）：左半第一行 `[0,9,9]`，右半 `[9,9,9]`，输出第一行 `[0,0,0]`——左[0]=0 不等 9，不符合 AND 条件产生 0。其他位置验证 AND 逻辑一致。
- train[1]：左半 `[0,0,0], [0,0,0], [0,0,0], [0,9,9], [0,0,0]`，右半 `[9,0,0], [9,9,9], [9,9,9], [0,0,0], [9,9,9]`。输出 `[0,8,8], [0,0,0], [0,0,0], [0,0,0], [0,0,0]`——仅位置 (0,1) 和 (0,2) 的 AND 为真。
- train[2-4]：同样模式，AND 逻辑一致。
- 测试样例：同样结构，左/右半比较。

## 3. 歧义与风险

- 歧义点：AND 操作是否只对颜色 9 敏感，还是说 0 vs 非 0 即可。从训练样例看，只有 9 和 0 参与，规则简化为 9 AND 9 = 8。
- 当前采用的解释：仅当左右对应位置都为 9 时输出 8。
- 风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_1x1_conv
- locality: 0
- single_linear_conv_possible: yes
- recommended_kernel: 1x1
- nonlinearity_needed: no
- 原因：本质是按位 AND。可将 input 左右半分别 shift/stack，通过 1x1 Conv 的 weight 和 bias 实现。逻辑：检测 input[:,c]==9 AND input[:,c+4]==9。两个 one-hot 通道相乘即可。

颜色映射表：
```text
(9_left, 9_right) -> 8 (output)
otherwise -> 0
```
简洁 weight_fn: `output[8] = input[9_left] * input[9_right]`，其中 9_left 为 col 0-2 的通道，9_right 为 col 4-6 的通道。

## 5. 最终摘要

```yaml
task_id: 025
primitive_types: [pixelwise_AND, channel_comparison]
input_shape_rule: 5x7
output_shape_rule: 5x3
formal_rule_short: output[c]=8 if left[c]==9 and right[c]==9 else 0
locality: 0
single_linear_conv_possible: yes
recommended_architecture: single_1x1_conv
main_risk: 测试中可能出现其他颜色代替 9
confidence: high
```
