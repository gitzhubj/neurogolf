# Task 006 规范

## 1. 核心规则

- 输入固定 7x7，输出固定 7x7（同尺寸）。
- 背景色为 0。输入中非零值沿某条反对角线（anti-diagonal，即 r+c 为常数的线）及其邻近位置出现，形成一段颜色序列。
- 核心变换：从输入反对角线提取非零颜色序列 S（长度为 L，L=3 或 4），然后将该序列沿反对角线方向平铺填充整个 7x7 输出。
- 输出[r,c] = S[(r + c) mod L]。颜色序列在输出中保持输入原色，不重染色。

```text
# 从输入沿反对角线提取颜色序列 S
S = [values at positions where r+c increases and value != 0]
# 或等效地：S 是沿主反对角线遇到的非零颜色的循环序列
L = length of S

for r in 0..6, c in 0..6:
    output[r][c] = S[(r + c) % L]
```

## 2. 关键证据

- train 0：输入反对角线 (0,0)=2、(0,1)=8、(0,2)=3 构成序列 [2,8,3]。输出按 anti-diagonal 方向重复平铺：行 0 为 [2,8,3,2,8,3,2]（r+c=0..6 依次对应 S[0..6 mod 3]），行 1 为 [8,3,2,8,3,2,8]（r+c=1..7 对应 S[1..7 mod 3]），全图一致。
- train 1：输入序列从右下向左上读取为 [1,2,4]。输出平铺序列 [2,4,1]（序列起点取输出[0,0]对应的值）。全图按 (r+c) mod 3 的节奏铺满。
- train 2：输入含 4 色序列 [4,8,3,x]，输出按 (r+c) mod L 平铺，L=3 或 4 取决于序列长度。
- test：输入反对角线含 [1,4,2] 三种色，输出平铺验证序列 tiling 规则。
- arc-gen 涵盖多组颜色组合和不同序列长度，均支持反对角线序列提取 + 全图平铺。

## 3. 歧义与风险

- 歧义点：序列的读取方向和起始位置。当前解释：从最小 r+c 值（左上角附近）开始沿反对角线（r+c 递增）读取非零值，用该序列按 (r+c) mod L 平铺。但不同样例中序列起始点在输出中的对齐方式可能不同（如 train 1 输出[0,0] = 序列[1] 而非序列[0]）。风险等级：medium。
- 歧义点：序列长度 L 的确定（何时截断）。当前解释：提取所有反对角线上连续出现的非零值直到遇到全零反对角线。风险等级：low。
- 歧义点：若输入有两个不同反对角线上都有非零值且颜色序列不同。当前解释：取最先遇到（最小 r+c）的序列，但可见数据无此歧义。风险等级：medium。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu（需序列检测和复制定位，单层 Conv 不足以覆盖序列方向的全局平铺）
- locality: global（每输出格依赖序列长度和起始偏置，后者需全局序列提取）
- single_linear_conv_possible: no（序列起始检测和 (r+c) mod L 的坐标路由非单层线性可表达）
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes（序列检测的 argmin/argmax 逻辑需要非线性）

## 5. 最终摘要

```yaml
task_id: 006
primitive_types: [pattern_completion, tiling, sequence_extraction]
input_shape_rule: fixed 7x7
output_shape_rule: fixed 7x7
formal_rule_short: extract color sequence from anti-diagonal, tile it across the full grid using (r+c) mod L indexing
locality: global
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
main_risk: sequence start position alignment varies between examples; precise extraction rule for multi-sequence inputs undefined
confidence: medium
```
