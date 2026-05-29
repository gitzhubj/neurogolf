# Task 067 规范

## 1. 核心规则

- 输入网格由水平方向重复的块(period)拼成,输出为**第一个完整周期块**(最左侧的 N 列,其中 N 为水平周期长度)。
- 核心规则:找到最小的正整数 N 使得对所有 i,W-N-1 列满足`input[:, i] == input[:, i+N]`,输出`input[:, 0:N]`。

```text
find minimal N in [1, W//2] such that for all i in [0, W-N-1]: input[:, i] == input[:, i+N]
output = input[:, 0:N]
```

- 输出行数与输入相同,列数 = N。

## 2. 关键证据

- train[0]:3×9 输入,周期 N=3(每 3 列重复),输出 3×3(前 3 列)。
- train[1]:4×12 输入,周期 N=4,输出 4×4。
- train[2]:2×6 输入,周期 N=2,输出 2×2。
- test[0]:5×15 输入,周期 N=5,输出 5×5。
- arc-gen 有 262 个样例,全部支持周期性检测规则。

## 3. 歧义与风险

- 周期 N 必须是 W 的约数,且最小。所有样例中 N 均整除宽度。风险:low。
- 仅水平方向重复?所有样例水平重复,未涉及垂直方向周期。风险:low。
- 如果输入中某列被 0 部分填充但整体仍保持周期模式,不影响规则(周期由非零模式决定)。风险:low。

## 4. NeuroGolf 架构提示

- recommended_architecture: constant_or_lookup_like_network
- locality: global(需比较全列)
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: no
- 周期检测需要全局比较列之间的异同,不能由 Conv 完成。但输出只是简单的裁剪(取前 N 列),裁剪本身是索引操作。
- memory_priority: 裁剪操作只产生一个输出张量(尺寸小于等于输入),内存友好。周期检测可用 Reduce 操作实现(逐列比较)。
- fusion_hint: 周期检测和裁剪可分离:检测逻辑用少量 Reduce 和 ArgMin,裁剪用 Slice。

## 5. 最终摘要

```yaml
task_id: 067
primitive_types: [period_detection, tiling, cropping, column_comparison]
input_shape_rule: R x W (W multiple of period)
output_shape_rule: R x N (N = horizontal period)
formal_rule_short: output = first period of input's horizontal tiling, N = min period such that col[i] == col[i+N]
locality: global
single_linear_conv_possible: no
recommended_architecture: constant_or_lookup_like_network
main_risk: none
confidence: high
```
