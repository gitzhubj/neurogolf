# Task 053 规范

## 1. 核心规则

- 输入/输出均为 3×3，固定尺寸。
- 输入颜色为 0、1、2，输出颜色同输入（保持原始颜色不变）。
- 核心变换：向下平移 1 格。所有非零图案整体向下移动一行。
- 移出底边界的行（row 2 → row 3，越界）被丢弃。
- 顶行（row 0）在输出中始终为 0（因为没有上一行可以移入）。

```text
for each cell (r, c):
    if r > 0:
        output[r][c] = input[r-1][c]
    else:
        output[r][c] = 0
```

## 2. 关键证据

- train 0：row0=[1,1,1] 下移到 row1 → 输出 row1=[1,1,1]。
- train 1：row1=[1,1,1] 下移到 row2 → 输出 row2=[1,1,1]。
- train 2：L 形图案 [0,1,0],[1,1,0] 下移到 [0,0,0],[0,1,0],[1,1,0]。
- train 3：颜色 2 的 L 形图案同样下移一行。
- 所有样本中图案在移动后保持列坐标不变。

## 3. 歧义与风险

- 歧义点：最底行图案下移是否应包裹回顶行。当前解释：直接丢弃（arc-gen 中无包裹回顶的证据）。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_kxk_conv（用 3×3 Conv 的 kernel offset 实现下移）
- locality: 1（仅依赖上一行）
- single_linear_conv_possible: yes（纯空间平移，3×3 Conv 可直接实现）
- recommended_kernel: 3x3
- nonlinearity_needed: no
- 实现方式：3×3 Conv，对每个通道 ch，设置 W[ch, ch, (1,0)] = 1.0（即 kernel 中向上偏移一行的位置），其余为 0。这样输入 (r-1,c) 的颜色映射到输出 (r,c)。

## 5. 最终摘要

```yaml
task_id: 053
primitive_types: [spatial_shift, translation]
input_shape_rule: fixed 3x3
output_shape_rule: fixed 3x3
formal_rule_short: shift all non-zero cells down by 1 row, discard bottom overflow
locality: 1
single_linear_conv_possible: yes
recommended_architecture: single_3x3_conv
main_risk: none
confidence: high
```
