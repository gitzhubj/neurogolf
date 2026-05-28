# Task 001 规范

## 1. 核心规则

- 输入固定 3x3，输出固定 9x9（高宽各乘以输入尺寸，即 `H_out = H_in * H_in = 9`，`W_out = W_in * W_in = 9`）。
- 背景色为 0。每个样例只有一种前景色 k（1..9），输出也只用 0 和同一个 k。
- 核心变换：条件 Kronecker 积式平铺。把 9x9 输出视为 3x3 个 3x3 block，每个 block 的位置 (R,C) 对应输入格 I[R,C]。
- 若输入格 I[R,C] 非零（前景色 k），则该 block 填入整个 3x3 输入图案；若 I[R,C] == 0，则该 block 全为 0。

```text
for each output cell at (r_out, c_out):
    R = r_out // 3
    C = c_out // 3
    r = r_out % 3
    c = c_out % 3
    output[r_out, c_out] = input[r, c]   if input[R, C] != 0 and input[r, c] != 0
    output[r_out, c_out] = 0             otherwise
```

- 若输入同一格出现多种非零色，当前解释为：按 tile cell 颜色输出（所有可见样例每例仅一种前景色，多色情况未覆盖）。

## 2. 关键证据

- train 0：前景色 7，I[0,0]=0 导致输出左上 3x3 block 全零，而 I[0,1]=7 和 I[0,2]=7 使右上两个 block 复制完整 7-图案，符合条件平铺。
- train 1：前景色 4，I[1,0]=I[1,1]=I[1,2]=0 使输出中间三行全零，左上 block 因 I[0,0]=4 填入完整图案，排除了普通 3 倍 nearest-neighbor 放大。
- train 2：前景色 2，仅 3 个前景格激活对应 block，其余 block 全零，排除全图固定模板解释。
- 所有 5 个 train 样例覆盖颜色 2,4,6,7，输出颜色集合与输入一致为 {0, k}。
- arc-gen 覆盖全部前景色 1..9 和 2 到 8 个前景格，均支持该规则。

## 3. 歧义与风险

- 歧义点：若同一输入包含多种前景色，输出颜色如何确定（按 block selector、按 tile cell、或需相等门控）。当前解释：按 tile cell 颜色输出。风险等级：medium（所有可见样例只有一种前景色，无法区分）。
- 歧义点：NeuroGolf 30x30 canvas 中 9x9 外区域是否需显式置零。当前解释：裁剪忽略。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: constant_or_lookup_like_network（固定坐标路由 + AND 门控，非单层 Conv 可表达）
- locality: global（每个输出格依赖两个不同输入坐标，非平移等变 offset）
- single_linear_conv_possible: no（需要 floor/mod 坐标映射和 AND 门控）
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes（AND 门控需要非线性或 argmax 打分技巧）

## 5. 最终摘要

```yaml
task_id: 001
primitive_types: [tiling, scaling, conditional_gate]
input_shape_rule: fixed 3x3
output_shape_rule: fixed 9x9 = 3x3 blocks of 3x3 tiles
formal_rule_short: each nonzero input cell replaced by full 3x3 input pattern; zero cells replaced by 3x3 zero block
locality: global
single_linear_conv_possible: no
recommended_architecture: constant_or_lookup_like_network
main_risk: multi-color input handling undefined
confidence: high
```
