# Task 042 规范

## 1. 核心规则

- 输入输出尺寸相同（10x10）。
- 背景色为 0，关键颜色：3 (green) 和 8 (cyan)。
- 核心规则：对于每个 3-colored 连通组件，输出中新增一个 8-colored 组件，该 8-组件是 3-组件的 180 度点反射（关于 3-组件和 8-组件组合的中心）。
- 更准确地说：输入中所有非零像素只有颜色 3。对于每对可配对的 3-组件（或每个 3-组件），在输出中添加一个形状相同但颜色为 8 的组件，放置位置使得 3-组件与 8-组件关于它们联合的 bounding box 中心对称。
- 如果两个 3-像素形成对角线对（如 (r,c) 和 (r+1,c+1)），则两个 8-像素放置于 (r-1,c+2) 和 (r+2,c-1)，形成矩形/菱形四顶点。
- 3-像素本身在输出中保留。

## 2. 关键证据

- train 1：两个对角 3-对分别在 (3,3)/(4,4) 和 (6,7)/(7,6)，输出新增 8 在 (2,4)、(5,5) 及 (5,1)、(8,8)，与 3 形成对称四边形。
- train 2：两个 2x2 的 3-块分别位于左上和中左，输出新增两个 2x2 的 8-块位于左上方和右下方，形状相同。
- train 3：仅两个孤立 3，8 放置在对称对角位置。
- arc-gen 全部支持此对称反射规则：3-组件的形状被复制为 8-组件，位置关于联合中心 180 度旋转。

## 3. 歧义与风险

- 歧义点：当存在 3 个或更多 3-组件时，如何配对？以及配对的全局参考中心是什么？
  - 当前解释：每个 3-组件独立产生一个对应的 8-组件，反射中心为 3-组件自身的中心点或配对组件的联合中心。具体中心可能由全局 grid 中心或组件间相对位置决定，细节不确定。
  - 风险等级：medium
- 歧义点：3-组件是单点 vs 2x2 块 vs 3x3 块时，8-组件的放置规则是否一致？
  - 当前解释：是，规则一致，均为 180 度旋转复制。
  - 风险等级：low

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 原因：需要识别连通组件、计算其中心点、在对称位置生成相同形状的新组件，属于典型的目标检测+生成逻辑，无法用单层 Conv 实现。

## 5. 最终摘要

```yaml
task_id: "042"
primitive_types: ["object_reflection", "copy_shape"]
input_shape_rule: "same as output, 10x10"
output_shape_rule: "same as input"
formal_rule_short: "for each 3-component, add an 8-component at 180-degree rotated position"
locality: "global"
single_linear_conv_possible: "no"
recommended_architecture: "object_logic_required"
main_risk: "多组件时的精确反射中心尚未完全确定"
confidence: "medium"
```
