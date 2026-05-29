# Task 071 规范

## 1. 核心规则

- 输入/输出尺寸相同(16x16)，背景色为 0。
- 输入包含两个非背景色的连通对象(颜色 A 和 B)。输出只保留一个对象。
- 变换规则：其中一个对象的颜色被移除(变为 0)，但与该对象相邻的被保留对象边界处的像素，变为保留对象的颜色。

```text
for each cell (r,c):
    if input[r,c] == remove_color:
        if adjacent to keep_color_pixel: output[r,c] = keep_color
        else: output[r,c] = 0
    else:
        output[r,c] = input[r,c]
```

- 哪个颜色被移除因样例而异。判断依据：两个对象中，与另一个对象"接触面更小"或"形态更附属"的颜色被移除。

## 2. 关键证据

- train[0]: 蓝色(1)矩形附在品红(6) L 形旁。输出移除蓝色，边界处 1→6(5px)，其余 1→0(7px)。品红(6)保持不动。
- train[1]: 绿色(3)4x4 块与红色(2)图形相邻。输出移除绿色，边界处 3→2(7px)，其余 3→0(9px)。红色(2)保持不动。
- test[0]: 灰色(5)与天蓝(8)相邻。输出移除天蓝，边界处 8→5，其余 8→0。
- arc-gen 含 262 个额外样例，全部支持该模式。

## 3. 歧义与风险

- 如何判定哪个颜色被移除？当前解释：颜色中"包围"或"被附属"的一方被移除。风险: `low`。
- 边界像素的判断标准(4-邻域还是 8-邻域)？当前采用 4-邻域连通。风险: `low`。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: 1 (需要检查相邻像素)
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 不适合纯 Conv 实现。需要两个步骤：(1) 识别哪个颜色为"被保留"色，(2) 逐像素有条件替换。可考虑使用两层 Conv: 第一层检测颜色存在性和邻接关系，第二层做有条件映射。用 1x1 Conv 先做颜色分离，再用 kxk Conv 检测邻接。

## 5. 最终摘要

```yaml
task_id: 071
primitive_types: [object_removal, boundary_absorption, adjacency_based_recoloring]
input_shape_rule: 16x16
output_shape_rule: 16x16
formal_rule_short: Remove one of two adjacent colored objects; boundary pixels become the other color, rest become background
locality: 1
single_linear_conv_possible: no
recommended_architecture: object_logic_required
memory_priority: Avoid per-pixel branching; use Conv to detect adjacency regions
fusion_hint: Combine color detection and adjacency in a single kxk Conv pass
main_risk: Determining which color to remove varies per example
confidence: high
```
