# Task 007 规范

## 1. 核心规则

- 输入输出同尺寸。输入尺寸可变（观测 9..16 行，8..16 列）。
- 背景色为 0。输出保持输入中所有非零颜色不变，无重染色。
- 核心变换：对象垂直压实——移除对象之间的空白行，使各对象在垂直方向上紧挨排列（上下对象之间不留空白行），但对象内部结构和水平位置保持不变。对象自身的形状和颜色完全保留。
- 压实方向为由上往下堆积：最上方对象保持原位（或滑动到最靠近上方边界），后续对象依次紧接前一对象的底部。
- 对象以 8-连通或 4-连通同色组件识别。压实过程中对象内部像素相对关系不变。

```text
objects = identify connected components (8-connected, same color)
sort objects by min_row ascending
current_top = 0 (or keep first object at its original top)
for each object in sorted order:
    shift object vertically so its top row = current_top
    current_top = object bottom row + 1
    (horizontal positions unchanged)
write shifted objects to output
```

- 若网格顶部有空行，所有对象整体上移至顶部。

## 2. 关键证据

- train 0（14x9）：输入有颜色 2 对象（行 2-3）和颜色 8 对象（行 10-11），中间隔 5 行空白。输出中颜色 2 对象滑至行 8-9，颜色 8 对象保持行 10-11，两对象之间仅隔 1 行（无空白）。
- train 1（9x10）：两对象间有大量空白行，输出中对象垂直压实，之间间距为 0。
- train 2（11x10）：多对象压实，所有垂直空白行被消除，对象保持各自形状和颜色。
- arc-gen 支持多种对象形状、颜色和不同间距的压实场景。

## 3. 歧义与风险

- 歧义点：压实方向是向上还是向下堆积。当前解释：由上往下堆积，顶部对象保持或上移至 grid 顶部，后续对象紧接前一个对象底部。风险等级：low（train 0 中顶部对象下沉而非上移，暗示可能按某种对齐规则）。实际需要更多分析确定精确对齐规则。
- 歧义点：对象水平位置是否改变。当前解释：水平位置不变。但需要验证 train 0 中颜色 2 对象的水平位置变化是压实副作用还是独立规则。风险等级：medium。
- 歧义点：对象间距（压实后相邻对象之间留多少空白行）。当前解释：0 或 1 行空白，取决于具体对齐。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required（需连通组件识别、排序、坐标平移）
- locality: global（对象移动距离取决于前面所有对象的高度累积）
- single_linear_conv_possible: no（需对象级检测、排序和可变平移）
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes

## 5. 最终摘要

```yaml
task_id: 007
primitive_types: [object_movement, connected_component_reasoning, compaction]
input_shape_rule: variable rectangular (9..16 x 8..16)
output_shape_rule: same as input
formal_rule_short: vertically compact objects by removing blank rows between them; objects maintain shape and color
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: exact vertical alignment rule (top-align vs bottom-align vs gap-fill) needs verification; horizontal position changes ambiguous
confidence: medium
```
