# Task 083 规范

## 1. 核心规则

- 输入固定 3×4，输出固定 6×8（恰好高宽各 ×2）。
- 核心变换：2×2 对称平铺。将 3×4 输入作为左上象限，通过镜像生成其余三个象限。
- 输出布局：
  - 左上 3×4 = 原始输入
  - 右上 3×4 = 输入的左右镜像（水平翻转）
  - 左下 3×4 = 输入的上下镜像（垂直翻转）
  - 右下 3×4 = 输入的 180° 旋转（水平+垂直镜像）
- 原始颜色不变。

```text
for r in 0..2, c in 0..3:
    output[r][c]           = input[r][c]          # 左上
    output[r][7-c]         = input[r][c]          # 右上（水平镜像）
    output[5-r][c]         = input[r][c]          # 左下（垂直镜像）
    output[5-r][7-c]       = input[r][c]          # 右下（180° 旋转）
```

## 2. 关键证据

- train 0：X 形 8 图案经 4 重对称生成 6×8 对称图案。
- train 1：颜色 3 的复杂图案经 4 重对称生成十字对称图案。
- train 2：C 形颜色-3 边框经对称生成完整矩形边框。
- 所有 train/test 样例输出严格遵循四象限对称规律。

## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Multi-op custom architecture (1 nodes). Study baseline directly.
- `fusion_hint`: Ops used: GridSample...

Baseline 实际架构: GridSample (1 nodes, 1 initializers)

## 5. 最终摘要

```yaml
task_id: 083
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
memory_priority: Multi-op custom architecture (1 nodes). Study baseline directly.
fusion_hint: Ops used: GridSample...
main_risk: high — complex architecture, refer to baseline
confidence: medium
actual_ops: GridSample
actual_nodes: 1
```
