# Task 066 规范

## 1. 核心规则

- 输入/输出尺寸相同(各样例 20x20,10x10,15x15,13x13)。
- 网格中有三种颜色:障碍物(颜色 8)、源标记(颜色 3)、目标标记(颜色 2),其余为 0(空地)。
- 核心规则:在源标记与目标标记之间画一条**颜色 3 的最短 Manhattan 路径**,路径绕开障碍物(8)。

```text
sources = all cells where input == 3
targets = all cells where input == 2
find shortest 4-directional path from any source to any target, avoiding obstacle cells (8)
for all cells on path: set output to 3
all other cells = input unchanged
```

- 路径优先利用已有 3 作为起点,终点为紧邻目标(2)的空地。
- 障碍物(8)保持不动,路径不能经过 8。

## 2. 关键证据

- train[0]:20x20,源 3 在左下(14,3)(15,3),目标 2 在右上(2,17)(3,17),路径先垂直向上再水平向右,绕开散布的 8。
- train[1]:10x10,源 3 在(1,1)(2,1),目标 2 在(6,5)(7,5),路径先向下再向右,绕过 8。
- train[2]:15x15,源 3 在(5,1)(5,2),目标 2 在(9,1)(9,2),路径先水平向右绕过正下方的 8 再垂直向下。
- test[0]:13x13,源 3 在(7,3)(7,4),目标 2 在(1,6)(1,7),路径先水平向右再垂直向上。
- arc-gen 有 262 个样例,支持最短路径解释。

## 3. 歧义与风险

- 当存在多条等长最短路径时:未指定选择规则。风险:medium(不同路径选择可能导致输出不同)。
- 路径终点:路径末端是紧邻 2 的 0 单元格,而不是覆盖 2 本身。风险:low。
- 目标(2)可能在路径完成后仍然保留 2,不会变为 3。风险:low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 需要路径搜索(BFS/Dijkstra),这是典型的对象级逻辑,完全超出卷积能力。
- memory_priority: BFS 需要 frontier 队列和 visited 标记。建议在 ONNX 外部实现或用固定次数的迭代形态学扩张模拟(扩张次数等于最大路径长度≈30)。
- fusion_hint: 如用迭代扩张模拟,可将每次扩张融合为一个 Conv(3x3 邻域)+Add+Clip 操作,保持单一张量。

## 5. 最终摘要

```yaml
task_id: 066
primitive_types: [path_finding, shortest_path, obstacle_avoidance, BFS]
input_shape_rule: varies (10-20)x(10-20)
output_shape_rule: same as input
formal_rule_short: draw shortest Manhattan path (color 3) from source(3) cells to target(2) cells, avoiding obstacles(8)
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: tie-breaking when multiple shortest paths exist
confidence: medium
```
