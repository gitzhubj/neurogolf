# Task 072 规范

## 1. 核心规则

- 输入尺寸 13x5(13 行, 5 列)，输出尺寸 6x5。
- 输入第 7 行(索引 6)为全黄(4)分隔行。
- 上下两部分各 6 行(上: 0-5, 下: 7-12)。输入仅使用颜色 2(红)和 0(背景)。
- 输出仅使用颜色 3(绿)和 0(背景)，尺寸与上下部分相同(6x5)。
- 变换规则为"上下异或(XOR)"：输出在(r,c)处为绿色(3)当且仅当上半部分和下半部分的(r,c)处恰好一个有红色(2)。

```text
for each cell (r,c) in 0..5 x 0..4:
    a = (input[r][c] == 2)
    b = (input[r+7][c] == 2)
    output[r][c] = 3 if (a XOR b) else 0
```

## 2. 关键证据

- 所有 train/test 均为 13x5 输入 → 6x5 输出，中间一行固定为黄(4)。
- train[0] 的 XOR 预测与输出完全匹配(30/30 像素正确)。
- 其他 train 样例 XOR 匹配率均为 30/30。上下部分各自单独匹配率仅为 10-20/30。
- arc-gen 含 262 个额外样例全部支持 XOR 规则。
- 黄色(4)行仅作分隔，不参与计算，输出中完全消失。

## 3. 歧义与风险

> 未发现主要歧义。规则明确，所有样例严格一致。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_kxk_conv
- locality: 0 (逐像素独立操作)
- single_linear_conv_possible: no
- recommended_kernel: 1x1
- nonlinearity_needed: no
- 关键难点：需要读取输入中相距 7 行的两个像素。不能直接用 1x1 Conv。可考虑：
  - 用两个独立切片(Slice)分别提取上下部分，然后在 channel 维度拼接，再用 1x1 Conv  做异或映射。
  - 或者用 stride=7 的 1x7 Conv 同时采样上下两行。
  - 异或逻辑：红色(2)出现为 1，通过 2 个 channel 相加后 mod 2 实现 XOR。等价于 `out = |top_red - bottom_red|`。

## 5. 最终摘要

```yaml
task_id: 072
primitive_types: [xor_operation, split_and_compare, row_separator]
input_shape_rule: 13x5
output_shape_rule: 6x5
formal_rule_short: XOR of top half and bottom half of grid, separated by yellow row; red(2) -> green(3) in output
locality: 0
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
memory_priority: Slice top/bottom halves separately; avoid large intermediate tensors
fusion_hint: Use Conv with stride to sample both halves; or use gather + elementwise ops
main_risk: none
confidence: high
```
