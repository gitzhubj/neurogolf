# Task 009 规范

## 1. 核心规则

- 输入输出同尺寸。输入尺寸可变（观测约 8..16 行，9..16 列）。
- 背景色为 0。输出保持所有非零颜色不变，无重染色。
- 核心变换：对象水平压实——将网格中的同色 8-连通对象向左滑动，消除对象之间（及对象与左边界之间）的水平空白列。对象保持各自形状、颜色和垂直位置，仅水平平移。
- 压实方向为由左往右堆积：最左方对象移至贴近左边界（或保持原位），后续对象依次紧接前一对象的右边界。

```text
objects = identify connected components (8-connected, same color)
sort objects by min_col ascending
current_left = 0 (or keep first object's position)
for each object in sorted order:
    shift object horizontally so its leftmost column = current_left
    current_left = object rightmost column + 1 (or + gap)
    (vertical positions unchanged)
write shifted objects to output
```

## 2. 关键证据

- train 0（含颜色 8 的 2x2 block 和颜色 2 的 L 形 cluster）：两个对象均位于输入右侧区域（cols 8-12），中间有水平间隙。输出中两者均向左平移，间隙缩小或消除。
- train 1-2：多对象场景，每个对象水平压实后紧挨排列，验证规则在不同对象形状和颜色组合下均成立。
- arc-gen 支持多种对象排列和间隙的场景，规则一致。

## 3. 歧义与风险

- 歧义点：压实后对象之间是否保留间距（gap=0 或 1）。当前解释：对象紧挨排列（间距 0），但具体间距需要逐例验证。风险等级：medium。
- 歧义点：对象排序按 min_col 还是按某种其他顺序（如颜色优先级）。当前解释：按 min_col 升序（最左优先）。风险等级：low。
- 歧义点：对象垂直位置是否可能变化（如同时垂直压实）。当前解释：仅水平平移，垂直位置不变。但可见数据有限。风险等级：medium。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required（需连通组件分割、排序、水平平移）
- locality: global（对象平移距离取决于前面所有对象的宽度累积）
- single_linear_conv_possible: no（需对象级检测和可变平移）
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes

## 5. 最终摘要

```yaml
task_id: 009
primitive_types: [object_movement, compaction, connected_component_reasoning]
input_shape_rule: variable rectangular
output_shape_rule: same as input
formal_rule_short: horizontally compact objects by sliding them left to eliminate horizontal gaps; maintain shape and vertical position
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: exact gap/spacing between compacted objects needs verification; vertical-only assumption may be incomplete
confidence: medium
```
