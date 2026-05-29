# Task 070 规范

## 1. 核心规则

- 输入/输出尺寸相同(17x17)。网格中有零散的颜色 1(蓝色)和颜色 8(浅蓝)像素,其余为 0。
- 核心规则:颜色 8 形成容器壁,颜色 1 形成纹理背景。8 所包围内部区域中的**部分 0 单元格变为 3**(绿色)。

```text
walls = color 8
interior = 4-directionally enclosed region bounded by walls and/or color 1 edges
for each 0-cell:
    if it is adjacent (4-dir) to a wall(8) AND inside the enclosed region:
        output = 3
    else:
        output = input
other cells (1, 8) unchanged
```

- 填充区域为 8 围成的内部空腔中紧邻 8 的 0 单元格。部分不紧邻墙壁的内部 0 可能不填充。
- 颜色 1 构成背景纹理,在 8 形成的容器外部保持不变。

## 2. 关键证据

- train[0]:8 在行 2-6,列 5-9 形成 C 形围栏,内部靠近 8 的 0→3;远离 8 的 0 保持 0;1 纹理和边界保持。
- train[1]:8 在行 7-9,列 0-9 附近形成包围,内部临近 8 的 0→3。
- train[2]:8 形成两个小包围区域,内部 0→3。
- test[0]:8 在行 11-14,列 6-13 附近形成包围,邻近 8 的 0→3。
- arc-gen 有 262 个样例,支持"8 围栏内的 0 填充 3"规则。

## 3. 歧义与风险

- 填充范围:只有紧邻 8 的 0→3,还是内部所有 0→3?样例显示靠近 8 的 0 填充,但内部远端的 0 可能保持。确切规则有待厘清。风险:medium。
- 8 的包围判定:并非所有 8 都形成封闭围栏;只有形成足够围堵的 8 形状才触发填充。风险:medium。
- 颜色 1 的作用:1 似乎是背景纹理填充,不作为墙壁。但 1 可能影响连通性判断。风险:low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global(需要连通性和包围检测)
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 需要 flood-fill 或膨胀操作来识别 8 周边的内部区域,属于对象级逻辑。
- memory_priority: 可使用迭代形态学膨胀从 8 向外扩展,标记可达的内部 0,限制迭代次数以避免填满整个容器。
- fusion_hint: 形态学膨胀可用 3×3 Conv(权重为 All-ones)+阈值化模拟,对 8 周围逐层扩张。

## 5. 最终摘要

```yaml
task_id: 070
primitive_types: [enclosure_fill, wall_adjacent, morphological_dilation, cavity_filling]
input_shape_rule: 17x17
output_shape_rule: 17x17
formal_rule_short: fill 0-cells adjacent to color-8 walls (inside enclosed region) with color 3
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: exact extent of fill (all interior 0 vs only wall-neighbor 0)
confidence: medium
```
