# Task 094 规范

## 1. 核心规则

- 输入与输出尺寸相同（固定 15x15）。
- 背景色为 8（浅蓝），关键颜色：1（蓝色）构成矩形空心框架，6（品红）是填充色。
- 核心规则：对于每个由颜色 1 构成的矩形空心框架，在其内部填充颜色 6，并以其几何中心为基准绘制贯穿全图的十字线（水平线和垂直线同为颜色 6）。

```text
for each rectangular frame of color-1:
    center_r = (top + bottom) // 2
    center_c = (left + right) // 2
    // 填充框架内部（不含边框本身）为 6
    // 画贯穿全图的水平线在 center_r 行
    // 画贯穿全图的垂直线在 center_c 列
```

- 框架本身（颜色 1）在输出中保持不变。背景 8 在未被 6 覆盖的地方保持不变。
- 若有多个框架，每个独立绘制其十字线，最终叠加显示。

## 2. 关键证据

- train[0]: 单个框架（rows 1-5, cols 3-7）。中心 (3,5)。输出在 row 3 全宽水平 6 线，col 5 全高垂直 6 线，且框架内部被 6 填充。
- train[1]: 两个框架（左上 rows 3-7, cols 3-7；右下 rows 9-13, cols 8-12）。输出有两条水平线（row 5 和 row 11）和两条垂直线（col 5 和 col 10）。框架内部均填 6。
- test[0]: 两个框架（左上 + 右下构造），同样画两条十字线，框架内部填 6。
- arc-gen 含 262 个样例验证该规则。

## 3. 歧义与风险

- 歧义点：框架定义——必须是完整闭合的矩形 1-边框，还是任意 1-像素轮廓？当前解释：闭合矩形边框。风险等级：low（所有样例均为清晰闭合矩形）。
- 歧义点：多个框架的十字叠加区域颜色？当前解释：全部为 6，无冲突。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global（十字线贯穿全局）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 需检测颜色 1 形成的矩形框，计算每个框的中心。十字线绘制可以通过构造全行/全列的 mask 然后叠加。多个框的十字线叠加只是元素级 max 操作。

## 5. 最终摘要

```yaml
task_id: 094
primitive_types: [frame_detection, center_calc, crosshair_drawing, interior_fill]
input_shape_rule: fixed 15x15
output_shape_rule: fixed 15x15
formal_rule_short: for each color-1 rectangle, fill interior with 6 and draw full-width/full-height crosshair at center
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
memory_priority: construct horizontal/vertical line masks as constant tensors, avoid per-pixel loops
fusion_hint: frame detection can use Conv edge detection; center calculation needs per-frame bbox
main_risk: assumes all frames are axis-aligned closed rectangles of color 1
confidence: high
```
