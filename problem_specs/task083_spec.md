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

- recommended_architecture: constant_or_lookup_like_network（固定坐标映射 + 权重查表）
- locality: global（2× 上采样 + 镜像需要坐标变换）
- single_linear_conv_possible: no（2× 上采样不是单层 Conv 可表达的）
- recommended_kernel: not_single_conv
- nonlinearity_needed: no

## 5. 最终摘要

```yaml
task_id: 083
primitive_types: [2x_upscale, fourfold_symmetry, mirror_tiling]
input_shape_rule: fixed 3x4
output_shape_rule: fixed 6x8
formal_rule_short: double input size by 4-fold Klein symmetry (original + H-mirror + V-mirror + 180-rotate)
locality: global
single_linear_conv_possible: no
recommended_architecture: constant_or_lookup_like_network
main_risk: none
confidence: high
```
