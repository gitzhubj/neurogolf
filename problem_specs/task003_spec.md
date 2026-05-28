# Task 003 规范

## 1. 核心规则

- 输入输出同尺寸。输入尺寸可变（观测 8..16 行，8..16 列）。
- 背景色为 0。每种非零颜色 k（1..9）在输出中保持原色不变，无重染色。
- 核心变换：将每个同色 8-连通非零对象执行"右剪切"——对象最底行保持原位，其余行向右平移 1 格，移动后若超出对象自身右边界则被夹回右边界。
- 连通性按 8-邻接（含对角线）判断；每个颜色独立分割对象。

```text
for each same-color 8-connected object C with color k:
    bottom = max row in C
    right = max col in C
    for each pixel (r,c) in C:
        if r == bottom:
            target = (r, c)      # 底行保持不动
        else:
            target = (r, min(c+1, right))  # 右移 1，但不超出对象右界
        output[target] = k
```

## 2. 关键证据

- train 0（14x9）：颜色 6 对象 bbox 行 1..5、列 1..6。顶行列 1..3 变为 2..4；第 4 行列 3 变为列 4，但列 6 已在右边界保持不动；最底行（行 5）完全保持不变。颜色 2 对象同理独立移动。
- train 1（8x9）：颜色 8 对角臂对象底行为行 5，非底行右移但行 4 的右端列 8 被夹住不越界。
- train 2（11x10）：多对象场景，每对象按自身 bbox 独立右剪切，非按全图统一右边界。
- arc-gen 涵盖多种对象形状和颜色，均支持同色 8-连通独立右剪切规则。

## 3. 歧义与风险

- 歧义点：连通性使用 4-邻接还是 8-邻接。当前解释：8-邻接（含对角线），因斜向相邻段在 4-邻接下会被拆成两个对象，导致错误结果。风险等级：low。
- 歧义点：两个对象右剪切后若目标坐标冲突，如何裁决。当前解释：可见样例无冲突，覆盖规则未定义。风险等级：medium。
- 歧义点：底行保持是指整行像素还是仅水平底边。当前解释：整行（因可见对象底行均为水平连续段，二者等价）。风险等级：medium。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required（需同色 8-连通分量分割、对象级 bbox、条件坐标映射）
- locality: global（每个像素是否移动取决于所属对象的全局 bottom(C) 和 right(C)）
- single_linear_conv_possible: no（需连通组件和对象级条件路由）
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes（对象分割和条件 gate 均需非线性）

## 5. 最终摘要

```yaml
task_id: 003
primitive_types: [object_movement, connected_component_reasoning, conditional_gate]
input_shape_rule: variable rectangular (8..16 x 8..16)
output_shape_rule: same as input
formal_rule_short: for each same-color 8-connected object, keep bottom row, shift other rows right by 1 capped at object rightmost column
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: collision resolution between objects undefined; connectivity type (4 vs 8) decisive for diagonal shapes
confidence: high
```
