# Task 062 规范

## 1. 核心规则

- 输入/输出尺寸相同(10x10)。
- 输入背景为 0,输出背景变为 3(绿色)。
- 输入中有两个非零颜色:一个"主体颜色"(出现较多)和一个"辅色"(出现极少,通常 1-2 个像素)。
- 核心规则:将输入中的稀疏形状对称补全为沿主轴对称的封闭图案,辅色像素融入主体颜色,所有 0 变为 3。

```text
background 0 → 3
辅色像素 → 主体颜色
形状沿水平和/或垂直轴对称扩展,形成封闭环或矩形
```

- 不同样例的对称轴和最终形状不同,但始终关于通过形状中心的水平/垂直轴对称。

## 2. 关键证据

- train[0]:主体色 4(黄色),辅色 2(红色)2 个像素。输出四瓣对称形状,2→4,背景→3。
- train[1]:主体色 6(紫色),辅色 2(红色)形成 L 形。输出对称的粗环状,2 消失,6 形成封闭形状。
- train[2]:主体色 7(橙色),辅色 2(红色)1 个像素。输出为 7 的对称粗环。
- train[3]:主体色 8(浅蓝),辅色 2(红色)1 个像素。输出为 8 的矩形框。
- arc-gen 有 262 个样例,支持"辅色定位→对称完成"的解释。

## 3. 歧义与风险

- 对称规则不够精确:不同样例的对称补全方式略有差异(有的四瓣,有的粗环,有的矩形框),需统一规则。风险:medium。
- 辅色与主体色的确定规则:辅色通常出现 1-2 次,主体色出现 3 次以上。但如果两个颜色出现次数相近则规则模糊。风险:medium。
- 背景色固定为 3(绿色):所有样例一致,但即使背景不是 3,规则是否依然成立?风险:low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 需要对象级处理:识别两个非零颜色,区分主体/辅色,找到形状边界,计算对称中心,镜像完成形状。这不是单层 Conv 能解决的问题。
- memory_priority: 建议将对称补全操作在静态逻辑中实现,避免动态生成大量坐标映射中间张量。
- fusion_hint: 轴对称可视为坐标映射,通过预先计算对称变换的查表实现,融合进单次写操作。

## 5. 最终摘要

```yaml
task_id: 062
primitive_types: [symmetry_completion, shape_inpainting, mirror, background_fill]
input_shape_rule: 10x10
output_shape_rule: 10x10
formal_rule_short: fill background with 3, mirror sparse shape to form symmetric closed pattern, merge secondary color into primary
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: symmetry axis determination varies across examples
confidence: medium
```
