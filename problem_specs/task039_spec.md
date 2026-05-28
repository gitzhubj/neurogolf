# Task 039 规范

## 1. 核心规则

- 输入尺寸：10x10。输出尺寸：3x3。
- 背景色为 0。输入为对称的同心分层图案：不同颜色（如 7, 6, 8, 4）组成从外向内的多个方形/菱形层。
- 核心规则：找到最内层（中心）3x3 区域，提取该区域作为输出。即输出 = 输入中由非零颜色组成的最内 3x3 块的左上角区域。
- 等价描述：input 的对称中心有一个由多种颜色嵌套的图案。从外向内的每层厚度为 1 像素。输出取输入对称图案的"最内 3x3 切片的左上角"。
- 形式化：
  ```text
  center_r, center_c = 图案中心坐标
  output = input[center_r-1:center_r+2, center_c-1:center_c+2]
  ```

## 2. 关键证据

- Train 0：输入有多层嵌套（外 7→6→8→内 4），输出 3x3 为 [[0,0,7],[0,6,8],[7,8,4]]，即中心附近的 3x3 切角。
- Train 1：输入嵌套（外 1→3→5→6→内 2），输出 3x3 为 [[1,0,0],[0,3,6],[0,5,2]]。
- Test：输入嵌套（外 0/8→4→8→3），输出 [[0,0,0],[0,4,4],[8,8,3]]。
- arc-gen 样例均支持该提取规则。

## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

- `recommended_architecture`: `object_logic_required`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_single_conv`
- `nonlinearity_needed`: `yes`
- 原因：需要定位对称图案的中心，然后裁剪固定 3x3 区域。涉及全局结构分析和坐标计算，不是单纯的局部操作。

## 5. 最终摘要

```yaml
task_id: "039"
primitive_types: [pattern_location, crop]
input_shape_rule: 10x10
output_shape_rule: 3x3
formal_rule_short: 提取嵌套对称图案中心附近的 3x3 切角
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 无
confidence: high
```
