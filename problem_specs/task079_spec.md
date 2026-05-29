# Task 079 规范

## 1. 核心规则

- 输入尺寸 14x14，输出尺寸 3x3。输出维度远小于输入。
- 输入包含分散的非零像素(共 15-40 个)，形成若干空间簇(cluster)。每个簇对应 3x3 输出的一个单元格。
- 变换规则：将输入的非零像素按空间位置分为最多 9 组，每组对应 3x3 输出中的一个位置。如果某组存在，则输出该组的"代表色"(该组中出现最多的非零颜色)，否则输出 0。

```text
# Approximate rule:
for each output cell (i,j) in 0..2:
    region = input pixels in the spatial region corresponding to (i,j)
    if region has >= threshold non-zero pixels:
        output[i][j] = dominant_nonzero_color(region)
    else:
        output[i][j] = 0
```

- 分块方式近似于将 14x14 均匀划分为 3x3 网格(约 5 行/列每块)。每块内的非零像素决定输出。
- 输出颜色和代表色均为该输入中"最普遍的非零颜色"。

## 2. 关键证据

- train[0]: 14x14 输入含天蓝(8, 15 处)和红(2, 10 处)。输出为 8 的 X 形: [8,0,8],[0,8,0],[8,0,8]。
- train[1]: 14x14 输入含黄(4)、蓝(1)、红(2)等。输出为 4 的"拐角"形: [4,0,0],[0,4,4],[4,0,0]。
- train[2]: 14x14 输入含天蓝(8, 多数)和品红(6, 少数)。输出为 8 的十字形: [0,8,0],[8,8,8],[0,8,0]。
- 输出颜色总是输入中出现最多的非零颜色(8 或 4)。
- arc-gen 含 262 个额外样例。

## 3. 歧义与风险

- 空间分组的具体边界不完全确定。当前假设每块约 5 行 x 5 列(最后一块为 4)。风险: `medium`。
- 判定一个块是否"激活"的阈值未知(可能要求至少 4-5 个非零像素)。风险: `medium`。
- 输出颜色选取规则不完全明确(为何 train[1] 选 4 而非 1？可能选"结构性"更强的颜色)。风险: `medium`。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: global (需要空间聚合)
- single_linear_conv_possible: no
- recommended_kernel: larger (至少 5x5 下采样)
- nonlinearity_needed: yes
- 本质是 14x14 → 3x3 的下采样分类任务。可用 stride=5 的 5x5 Conv + 阈值池化 + 映射。
- 由于输出尺寸极小(9 像素)，可考虑用全局池化 + 小 MLP 做分类，再 reshape 到 3x3。
- 避免按块独立切片——用 stride Conv 统一采样更高效。

## 5. 最终摘要

```yaml
task_id: 079
primitive_types: [downsampling, spatial_clustering, pattern_recognition]
input_shape_rule: 14x14
output_shape_rule: 3x3
formal_rule_short: Partition 14x14 input into 3x3 grid of regions; output dominant non-zero color per active region
locality: global
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
memory_priority: Use stride Conv for direct downsampling; avoid per-region scatter/gather
fusion_hint: Strided Conv (5x5, stride 5) + threshold + per-channel argmax for 3x3 output
main_risk: Region boundaries and activation threshold not precisely determined
confidence: medium
```
