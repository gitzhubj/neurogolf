# Task 076 规范

## 1. 核心规则

- 输入/输出尺寸相同(13x13)，背景色为 0。
- 黄色(4)像素构成多个矩形框架或轮廓。每个黄色框架内部包含蓝色(1)、绿色(3)、红色(2)等像素构成的图案。
- 变换规则：每个黄色框架内部的图案被"对称补全"——缺失的内部像素通过反射或复制从已有的内部像素填充。

```text
for each yellow-outlined region:
    region_pattern = extract interior pixels of the region
    filled = symmetrically_complete(region_pattern)
    output = place(filled, into region)
```

- 本质是"模式对称化"：黄色框架内部已有的彩色像素被作为种子，将区域内所有原本为 0 的像素填充为对称位置对应的颜色。

## 2. 关键证据

- train[0]: 右侧有两个黄色(4)框架区域(行 2-6,列 9-12 和行 7-9,列 2-6)，内部零散分布蓝色(1)和绿色(3)。输出在这些区域内填充了对称位置的 1 和 3(如列 9 中出现 3, 行 11 出现 1)。
- train[1]: 类似，黄色框架内缺少的部分被对称填充。输出在右下角和左下角添加绿色(3)和蓝色(1)。
- train[2]: 底部黄色(4)区域内缺失的对称点被补全。
- test[0] 尺寸不同(14x15)但规则一致。
- arc-gen 含 262 个额外样例。

## 3. 歧义与风险

- 对称轴如何确定？似乎以黄色框架的中心线为对称轴进行反射。风险: `medium`。
- 不同框架之间是否有交互(跨框架复制)？当前未观察到跨框架复制，只在框架内操作。风险: `medium`。
- 如果黄色框架不是矩形会怎样？所有样例中黄色框架均为矩形轮廓。风险: `low`。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global (对称填充需感知区域范围)
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 首先需要检测黄色(4)形成的矩形边框范围。然后提取框内已有彩色像素，计算对称映射，填充框内 0。
- 可能实现途径：(1) 用 Conv 检测黄色框架的边界线，确定矩形范围；(2) 在矩形内部做局部反射；(3) 将反射结果与原始输入融合。
- 避免按框架展开为大量独立张量；可考虑用一个固定大小的 Conv Kernel 遍历全图做局部反射检测。

## 5. 最终摘要

```yaml
task_id: 076
primitive_types: [symmetry_completion, pattern_filling, region_based_reflection]
input_shape_rule: 13x13 (variable)
output_shape_rule: 13x13 (input-dependent)
formal_rule_short: Fill missing interior pixels in yellow-framed regions via symmetry reflection of existing pattern
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
memory_priority: Use fixed-size sliding window for symmetry detection; avoid per-region slicing
fusion_hint: Detect yellow frames with Conv, then use per-channel mask to fill reflected interiors
main_risk: Symmetry axis detection may vary per example
confidence: medium
```
