# Task 064 规范

## 1. 核心规则

- 输入/输出尺寸相同(各样例尺寸不同:9x12,10x12,12x14,19x21)。
- 输入有三种颜色:背景色(占绝大多数)、一个矩形块(颜色 A)、若干孤立"种子"像素(颜色 B)。
- 核心规则:对于每个种子像素,如果其所在行或列与矩形块的范围**相交**,则在块与该种子之间画一条水平或垂直的直线(颜色为 B),连接块的边缘到种子位置。

```text
for each seed pixel at (r,c) with color B:
    if r_min_block <= r <= r_max_block:
        draw horizontal line of color B from block_right_edge+1 to c at row r
    if c_min_block <= c <= c_max_block:
        draw vertical line of color B from block_bottom_edge+1 to r at column c
```

- 种子与块在同一行时画水平线,同一列时画垂直线。同时满足则画 L 形折线(先水平再垂直或反之)。
- 原始种子像素保持不变;原矩形块保持不变;背景保持不变。

## 2. 关键证据

- train[0]:3x3 绿色块(行 1-4,列 2-4),黄色种子(3,9)同行→水平延长线,紫色种子(7,7)不同行也不同列→不变。
- train[1]:3x3 蓝色块,红色种子(8,3)同列→垂直线从块底部到种子。
- train[2]:4x4 绿色块,红色种子(0,4)同列→垂直线;种子(6,10)同行→水平线;种子(11,1)既不同行也不同列→不变。
- train[3]:5x5 红色块(行 5-8,列 7-11),多个蓝色种子,仅同行/同列的种子被连接。
- arc-gen 有 262 个样例,一致支持。

## 3. 歧义与风险

- 矩形块的识别:块是连续的矩形区域,颜色唯一。所有样例中块形状规则(矩形),边界明确。风险:low。
- 当种子同时在块的行和列范围内时:应画 L 形折线(水平+垂直)。train[2]种子(6,10)只同行,无此类情况。风险:medium(test 可能遇到)。
- 背景色固定为当前样例中出现最多的颜色,块颜色和种子颜色都是唯一的。风险:low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global(需要扫描全图定位矩形块和种子位置)
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 需要检测矩形块的边界和种子像素位置,属于对象级逻辑。可通过坐标比较判断每个种子是否与块同行/列。
- memory_priority: 将块边界(4 个坐标)作为标量常数存储,对每个种子位置做范围判断,避免展开成逐像素 mask 矩阵。
- fusion_hint: 画线操作可融合为:对每一行/列,判断是否在种子与块之间,批量设置颜色。

## 5. 最终摘要

```yaml
task_id: 064
primitive_types: [line_drawing, object_detection, rectangle, seed_connection]
input_shape_rule: varies (9-19)x(12-21)
output_shape_rule: same as input
formal_rule_short: draw horizontal/vertical line from block edge to each seed that shares its row or column
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: L-shaped path when seed aligns with both block row and column
confidence: high
```
