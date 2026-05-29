# Task 026 规范

## 1. 核心规则

- 输入/输出尺寸相同（变化尺寸，例如 10x10）。
- 背景色为 0（黑色）。输入包含一个由 1（蓝色）像素构成的连通形状。输出保留所有蓝色像素，并在特定位置添加 2（红色）像素。
- 核心规则：对于每个值为 0 的单元格，检查其 8 邻域（包括对角线）中蓝色(1)邻居的数量。若蓝色邻居数 >= 3，则将该单元格在输出中填为 2（红色）。
- 形式化表达：
  ```text
  for each cell (r,c) where input[r][c] == 0:
      count = number of blue neighbors in 8-neighborhood
      if count >= threshold: output[r][c] = 2
      else: output[r][c] = 0
  for each cell (r,c) where input[r][c] == 1:
      output[r][c] = 1
  ```
- 阈值可能为 2 或 3，需要通过更多样例验证。当前采用阈值 3（基于 train[0] 检查）。
- arc-gen 样例支持该规则，填充位置均为蓝色形状的凹陷/内角处。

## 2. 关键证据

- train[0]（10x10）：蓝色形状左侧有一个明显凹陷，输出中凹陷内被 2 填充。填充位置的 8 邻域内至少 3 个方向有蓝色邻居。
- train[1-2]：同样模式，2 始终出现在蓝色形状的角落/凹陷处，而非外围扩张。
- 所有 3 个训练样例中，2 从不与蓝色直接正交相邻多于一格，倾向于填充"内角"。
- 测试样例：蓝色形状有类似凹陷，填充模式一致。

## 3. 歧义与风险

- 歧义点：精确的邻居计数阈值（2、3 或其他）未完全确定。
- 当前采用的解释：8 邻域内蓝色邻居数 >= 3 时填 2。
- 风险等级：medium（阈值可能随输入变化）。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_kxk_conv
- locality: 1
- single_linear_conv_possible: probably
- recommended_kernel: 3x3
- nonlinearity_needed: yes (ReLU for thresholding)
- 原因：本质是 3x3 邻域内的邻居计数。可用 3x3 Conv（通道 1=blue 的 one-hot）后接 ReLU 阈值检测实现。weight_fn：3x3 全 1 卷积核（作用于 blue 通道），bias = -threshold + 1，ReLU 后取 sign。

## 5. 最终摘要

```yaml
task_id: 026
primitive_types: [neighbor_count, morphological_fill, concavity_detection]
input_shape_rule: variable, same as output
output_shape_rule: same as input
formal_rule_short: 对每个 0 格，若 8 邻域蓝邻居 >= 3 则输出 2，否则保持原 1/0
locality: 1
single_linear_conv_possible: probably
recommended_architecture: single_kxk_conv
main_risk: 阈值不确定（2 还是 3）
confidence: medium
```
