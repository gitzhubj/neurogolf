# Task 012 规范

## 1. 核心规则

- 输入/输出均为 12x12, 背景色 0。
- 检测所有"十字"对象: 中心非零颜色 A, 四个正交方向邻居颜色 B(A 和 B 不同, 非零)。
- 对每个十字对象, 以其中心为中心放置 5x5 固定模板, 模板仅使用 A 和 B 两种颜色。
- 5x5 模板结构:

```text
[A, 0, B, 0, A]
[0, A, B, A, 0]
[B, B, A, B, B]
[0, A, B, A, 0]
[A, 0, B, 0, A]
```

- 多个十字对象的模板可能重叠; 当重叠时, 后放置模板的非零位置覆盖先前的零, 但不覆盖先前已放置的非零格(不确定具体冲突解决, 目前假设 non-zero 保护 / OR 语义)。

## 2. 关键证据

- train 样例各有 2 个十字对象, 模板 5x5 不重叠。
- test 样例十字对象分布在网格两侧(如 (2,8) 和 (7,2)), 颜色相同(A=4,B=3), 模板 5x5 不重叠。
- 模板中 A 出现在中心 + 4 角 + 4 对角邻位(共 9 个); B 出现在 4 条正交臂(连续 2 格, 共 8 个); 仅 4 个空位(棋盘 pattern 的空白)保持为 0。
- arc-gen 262 例全部通过, 规则确定。

## 3. 歧义与风险

- 歧义点: 多个十字模板重叠时的冲突解决策略。
- 当前采用的解释: 非零优先, 后写不覆盖先写的非零格 (OR 语义)。
- 风险等级: low(重叠情况在 train/test 中未出现)。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: 2
- single_linear_conv_possible: no
- recommended_kernel: 5x5
- nonlinearity_needed: yes
- 需要先检测十字对象(AND 逻辑: 中心非零 AND 四臂非零), 再放置 5x5 模板。单一 5x5 卷积可覆盖模板放置, 但对象检测可能需要额外的中间激活。整体至少需要 2 层: 检测层 + 模板放置层。

## 5. 最终摘要

```yaml
task_id: 012
primitive_types: [object_detection, template_placement]
input_shape_rule: 12x12
output_shape_rule: 12x12
formal_rule_short: for each cross (center A, arms B), place 5x5 fixed template with colors A,B
locality: 2
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
main_risk: 模板重叠冲突解决策略
confidence: high
```
