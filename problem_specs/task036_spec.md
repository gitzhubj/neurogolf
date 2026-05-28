# Task 036 规范

## 1. 核心规则

- 输入尺寸：30x30。输出尺寸：由提取的形状决定（通常为 HxW，H 和 W 均较小，如 5x3）。
- 关键颜色：输入包含两类颜色——"噪声色"（作为孤立单像素出现）和"信号色"（形成连通组件的颜色）。
- 核心规则：找到输入中唯一以连通形状（而非孤立单像素）出现的颜色 C，提取该颜色所有像素的 minimal bounding box，输出该 crop 区域（颜色 C 保持不变，背景为 0）。
- 判别信号色的方法：检查每种非零颜色，统计其像素是否全部为孤立单像素（8-邻域内无同色像素）。若有颜色的像素存在 8-邻域同色连接，则该颜色为信号色。
- 形式化：
  ```text
  for each color C in {1..9}:
      if any pixel of C has a neighbor of same C (8-connected):
          signal_color = C
          break
  crop = bounding_box(all pixels of signal_color)
  output = input[crop]
  ```

## 2. 关键证据

- Train 0：30x30 输入，1 和 5 为孤立散点，3 形成连通图形（十字加方形）。输出 5x3 的 3-图形。
- Train 1：30x30 输入，2 为孤立散点，4 形成连通图形。输出为 4-图形的 bounding box。
- Train 2：30x30 输入，信号色形成特定形状。输出为对应提取。
- Test：30x30 输入。arc-gen 样例大量支持。
- 所有样例均遵循"提取唯一连通颜色"的规则。

## 3. 歧义与风险

- 歧义点：如果多个颜色都有连通组件怎么办（train 中未出现）。
- 当前采用的解释：取第一个检测到的连通色。
- 风险等级：`low`

## 4. NeuroGolf 架构提示

- `recommended_architecture`: `object_logic_required`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_single_conv`
- `nonlinearity_needed`: `yes`
- 原因：需要逐颜色检查连通性（8-邻域），然后计算 bounding box 并裁剪。涉及连通组件分析和条件选择，超过单层 Conv 能力。

## 5. 最终摘要

```yaml
task_id: "036"
primitive_types: [connectivity, object_extraction, crop]
input_shape_rule: 30x30
output_shape_rule: bounding_box(连通形状)
formal_rule_short: 提取唯一形成连通组件的颜色，crop 其 bounding box
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 多连通色的处理
confidence: medium
```
