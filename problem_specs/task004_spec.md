# Task 004 规范

## 1. 核心规则

- 输入输出同尺寸。输入尺寸可变（观测 8..16 行，8..16 列）。
- 背景色为 0。每种非零颜色在输出中保持原色，无重染色。
- 核心变换：对每个同色 8-连通非零对象执行"右剪切"。对象最低行保持原位不动；其余行的所有像素向右平移 1 格，若平移后超出该对象 bounding box 的最右列则被夹回右边界。
- 每个颜色独立分割对象，互不干扰；多个对象的移动并行进行。

```text
for each same-color 8-connected object C:
    bottom = max row in C
    right = max col in C
    for each pixel (r,c) in C:
        if r == bottom:  target = (r, c)
        else:            target = (r, min(c+1, right))
        output[target] = color_of(C)
```

## 2. 关键证据

- train 0（8x9）：单一颜色 8 对角臂对象。顶行 [0,8,8,8,8,8,0,0,0] 变为 [0,0,8,8,8,8,8,0,0]（全体右移 1）。第 4 行右端列 8 的 8 被夹住不越界。底行（行 5）[0,0,0,0,8,8,8,8,8] 完全保持。
- train 1（8x9）：颜色 8 对象 + 颜色 7 和 6 等多对象场景，每对象按各自 bbox 独立执行右剪切，非按全图统一边界。
- train 2（10x10）：多色多对象，底行均保持、非底行右移并受各自右边界约束。
- arc-gen 涵盖多种形状（diagonal arms、L-shapes、compact blocks）和全部颜色 1..9，均支持独立右剪切规则。

## 3. 歧义与风险

- 歧义点：连通性判断用 4-邻接还是 8-邻接。当前解释：8-邻接（含对角线），因对角相邻段若按 4-邻接拆分会得出错误底行和最右列。风险等级：low（train 0 中斜向 8 构成的连续臂是关键证据）。
- 歧义点：两个对象右剪切后目标坐标冲突如何裁决。当前解释：可见样例无冲突。风险等级：medium。
- 歧义点：若对象最低行有多行（如对象底部不平），哪些行保持。当前解释：仅 max_row 行保持，其余均右移。因可见对象底行均为单一连续行，无法验证多底行情况。风险等级：medium。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required（需 8-连通分量分割、对象级 bbox 计算、条件坐标映射）
- locality: global（像素目标坐标依赖所属对象的全局 bottom 和 right）
- single_linear_conv_possible: no（需连通组件推理和对象级条件路由）
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes

## 5. 最终摘要

```yaml
task_id: 004
primitive_types: [object_movement, connected_component_reasoning, conditional_gate]
input_shape_rule: variable rectangular (8..16 x 8..16)
output_shape_rule: same as input
formal_rule_short: each same-color 8-connected object gets right-shear: bottom row fixed, other rows shift right by 1, capped at object's rightmost column
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: multi-object collision resolution undefined; multi-bottom-row objects untested
confidence: high
```
