# Task 057 规范

## 1. 核心规则

- 输入固定 8×8，输出固定 3×6（H 缩小约 3 倍，W 缩小约 1.3 倍）。
- 输入包含一个小的非零图案（颜色 1/2/8 等），位于 8×8 网格的左半部或上半部，其余为 0。
- 核心变换：提取非零图案的最小包围盒（bounding box），然后将该图案水平拼接两次（形成左右两份副本），输出到 3×6 的网格中。
- 具体地：8×8 中的非零图案被裁剪到其 bounding box（通常为 3×3 或 3×2），然后该 bounding box 内容被复制到输出的左 3×3 和右 3×3（即水平镜像复制）。
- 输出保持原始颜色。

## 2. 关键证据

- train 0：输入有 3×3 的 8-图案在左上角。输出为 3×6，左 3×3 和右 3×3 各含一份该图案的副本。
- train 1：输入有图案在右下区域（颜色 2），输出同样水平复制两份。
- train 2：输入有颜色 1 的 L 形图案，输出两份水平拼接。
- test 0：颜色 3 图案，同理。
- 所有样例中输出高度 = 输入图案高度，输出宽度 = 2 × 输入图案宽度。

## 3. 歧义与风险

- 歧义点：非零图案的 bounding box 裁剪规则（是否裁掉四周零行/列）。当前解释：裁剪所有完全为零的行和列。风险等级：low。
- 歧义点：若输入中有多个不相连的图案。当前解释：视为一个整体图案一起裁剪。风险等级：low（所有样例仅一个紧密图案）。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required（需检测 bounding box + 裁剪 + 拼接）
- locality: global（bounding box 检测需全局扫描）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes

## 5. 最终摘要

```yaml
task_id: 057
primitive_types: [crop_to_content, horizontal_tiling, bounding_box]
input_shape_rule: fixed 8x8
output_shape_rule: fixed 3x6
formal_rule_short: crop non-zero content to its bounding box, then duplicate horizontally to double width
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: multi-object handling undefined
confidence: high
```
