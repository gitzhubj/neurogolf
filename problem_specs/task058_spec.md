# Task 058 规范

## 1. 核心规则

- 输入全零（任意尺寸 H×W），输出为 H×W 的迷宫/螺旋图案。
- 核心变换：从全零输入生成固定的螺旋形迷宫图案（颜色 3 和 0）。
- 图案是一个"螺旋迷宫"：外围一圈颜色 3，内部有一个从左上角开始的螺旋通道（0 和 3 交替形成螺旋路径通向中心）。
- 输出图案完全由网格尺寸 H×W 决定，与输入内容无关（输入恒为零）。
- 图案特征：N×N 的迷宫有 ceil(N/2)-1 层螺旋。

```text
output = generate_fixed_spiral_maze(H, W)
```

## 2. 关键证据

- train 0：6×6。外围 3，内部有一个简单的 U 形通道。
- train 1：8×8。外围 3，内部螺旋通道有 2 圈。
- train 2：15×15。外围 3，内部螺旋通道有 6 圈，呈标准螺旋形。
- train 3：13×13。类似螺旋结构。
- 所有样例输入全零，输出为固定螺旋迷宫，不同尺寸对应不同的螺旋圈数。

## 3. 歧义与风险

- 歧义点：迷宫生成的确切算法（是标准螺旋还是特定生成规则）。当前解释：从 (1,1) 开始的逆时针螺旋路径，宽度为 1 格。风险等级：low（arc-gen 覆盖多种尺寸）。
- 歧义点：偶数尺寸和非正方形的情况。当前解释：train 有非正方形样例（10×10 等），规则一致。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: constant_or_lookup_like_network（固定输出模板，与输入无关）
- locality: 0（逐像素独立，仅依赖坐标）
- single_linear_conv_possible: probably（固定坐标→颜色的映射可用 1×1 Conv 查表实现）
- recommended_kernel: 1x1
- nonlinearity_needed: no（纯查表）
- 实现策略：用静态常数/CoordConv 将 (r,c) 映射到 maze 模板。对于每个 H×W，预计算迷宫模板作为 Constant 节点。

## 5. 最终摘要

```yaml
task_id: 058
primitive_types: [maze_generation, fixed_pattern, spiral]
input_shape_rule: arbitrary (all-zero input)
output_shape_rule: same as input
formal_rule_short: generate a fixed spiral maze pattern (color 3 walls, 0 paths) based solely on grid dimensions
locality: 0
single_linear_conv_possible: probably
recommended_architecture: constant_or_lookup_like_network
main_risk: maze generation algorithm precise specification
confidence: high
```
