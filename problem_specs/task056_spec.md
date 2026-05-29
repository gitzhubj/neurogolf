# Task 056 规范

## 1. 核心规则

- 输入固定 3×3，输出固定 1×1（单个颜色值）。
- 核心变换：模式识别 → 输出颜色。根据 3×3 中非零格的几何排列（形状）输出对应的颜色代码。
- 形状-颜色映射表（从 train 样例推导）：
  - X 形（对角线上 3 个非零格，其余为零，如 [5,5,0],[5,0,5],[0,5,0] 或颜色在四角和中心）→ 输出 1 或 2
  - 十字形/加号形（中心+四个正交邻格非零）→ 输出 6
  - L 形/角落集中（非零格集中在右下角，形成 L 形块）→ 输出 3
- 具体映射：输入颜色值不决定输出，仅形状（非零格的模式）决定输出颜色。

```text
shape_type = classify_pattern(nonzero_mask)
output = shape_to_color[shape_type]
```

## 2. 关键证据

- train 0 ([5,5,0],[5,0,5],[0,5,0]) → 1（X 形变体）
- train 1 ([8,0,8],[0,8,0],[8,0,8]) → 2（标准 X 形）
- train 3 ([0,1,1],[0,1,1],[1,0,0]) → 3（L 形）
- train 6 ([0,5,0],[5,5,5],[0,5,0]) → 6（加号形）
- test 支持：加号形(8) → 6, X 形变体(7) → 1, X 形(2) → 2。

## 3. 歧义与风险

- 歧义点：train 0 和 train 5（颜色 4/5 的类似 X 形）为何输出 1 而非 2。当前解释：中心格是否被占用的差异。风险等级：medium。
- 歧义点：是否有更多形状模式未出现在 train 中。当前解释：arc-gen 36 例应覆盖主要形状。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required（模式分类器，非单层 Conv 可表达）
- locality: global（需要观察 3×3 全局布局）
- single_linear_conv_possible: no（需要形状识别和查表）
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes

## 5. 最终摘要

```yaml
task_id: 056
primitive_types: [pattern_recognition, shape_classification, downscale_to_1x1]
input_shape_rule: fixed 3x3
output_shape_rule: fixed 1x1
formal_rule_short: classify the 3x3 non-zero pattern shape (X, cross, L) and output a corresponding color code
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: shape-to-color mapping may have more types than observed
confidence: medium
```
