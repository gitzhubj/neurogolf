# Task 087 规范

## 1. 核心规则

- 输入/输出均为 3×3，固定尺寸。
- 核心变换：像素重排列。保持所有 9 个格的颜色多集不变（即每种颜色的出现次数不变），但重新排列每个像素的位置。
- 排列规则：循环行移位——每行向上移动 1 行（row 0 ← row 1, row 1 ← row 2, row 2 ← row 0）。
- 即 `output[r][c] = input[(r+1) % 3][c]`。

## 2. 关键证据

- train 2 最清晰：[8,8,8; 5,5,8; 8,5,5] → [5,5,8; 8,5,5; 8,8,8]。row0 上移→row2, row1→row0, row2→row1。
- train 0：[2,2,1; 2,1,2; 2,8,1] → [2,1,2; 2,8,1; 2,2,1]，每行上移一位。
- train 1 和 train 3 同理验证。
- test 0：[6,4,4; 6,6,4; 4,6,7] → [6,6,4; 4,6,7; 6,4,4]，规则一致。

## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_3x3_conv（垂直平移可用 Conv kernel offset 实现）
- locality: 1（仅依赖上一行）
- single_linear_conv_possible: yes（3×3 Conv 的 (1,0) offset 实现向下看一行即向上移）
- recommended_kernel: 3x3
- nonlinearity_needed: no

## 5. 最终摘要

```yaml
task_id: 087
primitive_types: [row_permutation, cyclic_shift]
input_shape_rule: fixed 3x3
output_shape_rule: fixed 3x3
formal_rule_short: cyclic row shift upward by 1: output[r][c] = input[(r+1)%3][c]
locality: 1
single_linear_conv_possible: yes
recommended_architecture: single_3x3_conv
main_risk: none
confidence: high
```
