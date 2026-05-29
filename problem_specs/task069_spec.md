# Task 069 规范

## 1. 核心规则

- 输入/输出尺寸相同(10x10)。背景为 0。
- 输入包含若干**连通形状块**。其中一块为"源模式"(颜色组合不包含 8),其余为"目标块"(全部由颜色 8 组成)。
- 核心规则:**所有目标块(颜色 8)被替换为源模式的副本**,保持其形状(行列布局)不变,颜色取自源模式对应位置的像素。

```text
source = the connected component that contains NO color-8 pixels
targets = all connected components that consist ENTIRELY of color 8
for each target component:
    overlay the source pattern onto the target's shape (same row/col count)
    for each cell in target:
        output[cell] = source[row_offset, col_offset]
```

- 源模式保留原位置不变;非 8 非源模式的零散像素保持不变。

## 2. 关键证据

- train[0]:源模式为 2×2 色块(7,6)/(9,4)在左上;3 个 2×2 的 8 块均被替换为该模式,左上角布局对应(7,6),右下角(9,4)。
- train[1]:源模式为 2×3 不规则块(7,7)/(6,6,6);所有 2×3 的 8 块被替换为同样布局的颜色。
- test[0]:源模式为 3×4 不规则块(4,4)/(3,4,3,3)/(0,0,3);所有形状匹配的 8 块被替换。
- arc-gen 有 261 个样例,支持模式复制解释。

## 3. 歧义与风险

- 源模式的识别:"不包含颜色 8 的连通块"在所有样例中均成立。但如果存在多个不含 8 的块,需要额外规则选择(当前样例中只有一个)。风险:medium。
- 目标块的形状匹配:目标块必须与源模式的形状(逐行像素数)完全一致,否则无法直接替换。目前所有目标块形状相同。风险:medium(test 可能不同)。
- 源模式的"对齐":源模式左上角对齐到目标块的左上角。风险:low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global(需要连通组件分析)
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 需要连通组件标记、形状匹配和模式复制。Conv 无法完成。
- memory_priority: 源模式像素可存储为静态常量小张量(最多约 12 像素);每个目标块只需一次写操作。
- fusion_hint: 目标块的替换可融合为:对每个 8 所在位置,根据相对偏移从源模式查表赋值。

## 5. 最终摘要

```yaml
task_id: 069
primitive_types: [pattern_transfer, connected_component, texture_replacement, shape_matching]
input_shape_rule: 10x10
output_shape_rule: 10x10
formal_rule_short: replace all color-8 connected components with the pattern of the non-8 source component, preserving shape
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: multiple non-8 source candidates or mismatched target shapes
confidence: medium
```
