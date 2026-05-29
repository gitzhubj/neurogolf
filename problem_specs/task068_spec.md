# Task 068 规范

## 1. 核心规则

- 输入/输出尺寸相同(10x10)。输入散落着各种颜色的孤立像素(0 为背景)。
- 核心规则:找到**唯一出现恰好一次的颜色**对应的像素位置,在其周围画一个 3×3 的红色(2)边框,中心为该唯一色,边框为 2。

```text
unique_color = the color value that appears exactly once in the input
(r0, c0) = position of that unique_color pixel
output is all zeros except:
for dr in [-1, 0, 1], dc in [-1, 0, 1]:
    if (dr, dc) == (0, 0):
        output[r0+dr, c0+dc] = unique_color
    else:
        output[r0+dr, c0+dc] = 2  (red)
```

- 输出中其余所有位置为 0。
- 红色(2)不一定是输入中出现次数最多的颜色,但必须存在于输入中。

## 2. 关键证据

- train[0]:唯一色 4(黄色)出现 1 次在(6,1);其余颜色(1,2,3,5,8)均出现多次。输出(5,0)-(7,2)的 3×3 框,中心 4,边框 2。
- train[1]:唯一色 6(紫色)出现 1 次在(2,7);输出 3×3 框(1,6)-(3,8),中心 6,边框 2。
- train[2]:唯一色 3(绿色)出现 1 次在(8,6);输出 3×3 框(7,5)-(9,7),中心 3,边框 2。
- test[0]:唯一色 9 出现 1 次在(6,5);输出 3×3 框(5,4)-(7,6),中心 9,边框 2。
- arc-gen 有 262 个样例,一致支持。

## 3. 歧义与风险

- 唯一颜色的定义:出现次数恰好为 1 的颜色。所有样例均满足此条件。风险:low。
- 边框颜色固定为 2(红色):所有样例都使用 2,但规则是否依赖 2 的存在?train 中 2 均存在。风险:low。
- 当唯一色像素位于网格边缘时,3×3 框部分超出边界:当前样例均在内部(距边界至少 1)。风险:low。
- 可能输入中有多个颜色出现 1 次:当前没有出现,但如有,需额外规则选择。风险:medium。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global(需要全局颜色计数)
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 需要全局颜色直方图统计找出唯一色,定位其坐标。这属于对象逻辑。
- memory_priority: 颜色统计可用 10 个标量累加器,非常轻量。3×3 框的绘制只需操作 9 个像素。
- fusion_hint: 颜色统计(Histogram)+ArgMin(计数为 1 的颜色)、坐标定位(Where)、框绘制(ScatterND)三个步骤,各自独立、张量极小。

## 5. 最终摘要

```yaml
task_id: 068
primitive_types: [color_histogram, unique_detection, bounding_box_drawing]
input_shape_rule: 10x10
output_shape_rule: 10x10
formal_rule_short: find color appearing exactly once, draw 3x3 red(2) box centered at its position
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: multiple singletons or unique color at edge
confidence: high
```
