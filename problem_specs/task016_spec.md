# Task 016 规范

## 1. 核心规则

- 输入/输出尺寸相同(3x3), 所有行完全相同(每列有唯一值)。
- 核心规则为固定颜色映射(逐像素):

```text
for each cell (r,c):
    output[r,c] = color_map[input[r,c]]
```

- 颜色映射表通过配对交换实现:

| 输入 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 9 |
|------|---|---|---|---|---|---|---|---|
| 输出 | 5 | 6 | 4 | 3 | 1 | 2 | 9 | 8 |

- 颜色 0 保持 0, 颜色 7 保持 7(未在样例中出现)。

## 2. 关键证据

- 所有 train/test 样例均为 3x3 输入 → 3x3 输出, 逐列相同。
- train 1: [3,1,2] → [4,5,6] (3↔4, 1↔5, 2↔6)
- train 2: [2,3,8] → [6,4,9] (2↔6, 3↔4, 8↔9)
- train 3: [5,8,6] → [1,9,2] (5↔1, 8↔9, 6↔2)
- 映射表完全一致, 4 组 pair-swap: (1,5), (2,6), (3,4), (8,9)。
- arc-gen 含有大量额外验证样例(300+), 全部支持该映射。

## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_1x1_conv
- locality: 0
- single_linear_conv_possible: yes
- recommended_kernel: 1x1
- nonlinearity_needed: no
- 最简单的颜色映射任务。1x1 Conv(in=10, out=10) 权重矩阵 W[out_c, in_c, 1, 1] 即可实现: 对每个 in_c, 设置 W[map[in_c], in_c, 0, 0] = 1.0, bias=0。如 W[5,1] = 1, W[6,2] = 1, W[4,3] = 1, W[3,4] = 1, W[1,5] = 1, W[2,6] = 1, W[9,8] = 1, W[8,9] = 1, W[0,0]=1, W[7,7]=1。

## 5. 最终摘要

```yaml
task_id: 016
primitive_types: [color_permutation, elementwise_mapping]
input_shape_rule: 3x3
output_shape_rule: 3x3
formal_rule_short: output[r,c] = color_map[input[r,c]] with fixed pairwise swaps
locality: 0
single_linear_conv_possible: yes
recommended_architecture: single_1x1_conv
main_risk: none
confidence: high
```
