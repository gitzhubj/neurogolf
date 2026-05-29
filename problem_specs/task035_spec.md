# Task 035 规范

## 1. 核心规则

- 输入与输出尺寸相同，均为 10x10。
- 关键颜色：0（背景），8（矩形块填充色），以及其他颜色（1–9 中除 0,8 外的颜色，作为"探针色"）。
- 核心规则：输入中包含一个由值为 8 的格子组成的矩形区域（连续块），以及散落在矩形外部（上下左右边缘附近）的探针色像素。探针色像素沿其所在行或列向内"投射"到 8-矩形的边界上——被投射到的 8 变为探针色。
- 形式化描述：
  ```text
  对每个探针色像素 (r, c) 其颜色为 P：
      找到 8-矩形在行 r 或列 c 上的最近边界格 (r', c')
      if (r', c') 在原图中为 8：
          output[r', c'] = P
  ```
- 投射方向：探针在矩形左侧→向右投射到矩形左边界；右侧→向左投射；上方→向下投射；下方→向上投射。
- 其他 8 保持不变，其他 0 保持不变。

## 2. 关键证据

- Train 0：探针 9(顶)、6(左)、4(底)，8-矩形在中间。输出中矩形边界对应位置变为 9,6,4。
- Train 1：探针 7(顶)、6(左)、3(左)、2(右)、1(底)。输出中矩形边界有对应的颜色替换。
- Train 2：探针 4(顶)、3(左)、2(左)、7(底)、6(右)、2(右)。输出符合投射规则。
- 所有 train 样例中探针颜色严格投射到矩形的对应行/列边界上。
- arc-gen 样例均一致支持该规则。

## 3. 歧义与风险

- 歧义点：当多个探针投射到同一位置时，取哪个颜色？（train 中未出现此冲突）
- 当前采用的解释：按扫描顺序，后来的可能覆盖。
- 风险等级：`low`

## 4. NeuroGolf 架构提示

- `recommended_architecture`: `object_logic_required`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_single_conv`
- `nonlinearity_needed`: `yes`
- 原因：需要检测 8-矩形的边界位置和探针位置，然后将探针颜色沿行/列投射。涉及全局形状识别和条件颜色替换，单层 Conv 无法完成。

## 5. 最终摘要

```yaml
task_id: "035"
primitive_types: [object_detection, color_projection]
input_shape_rule: 10x10
output_shape_rule: 10x10
formal_rule_short: 边缘探针颜色沿行/列投射到 8-矩形边界
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 多探针冲突处理
confidence: high
```
