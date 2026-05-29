# Task 074 规范

## 1. 核心规则

- 输入/输出尺寸相同(30x30)，背景色为 0。
- 输入包含颜色 0-9 全色域。颜色 9(栗色)构成一个或多个矩形"空洞"区域。
- 输出将颜色 9 全部移除，替换为通过"镜像反射"从周围区域推算出的颜色。

```text
for each cell (r,c):
    if input[r,c] == 9:
        # fill by reflecting the content across the 9-region boundary
        output[r,c] = reflected_color(r, c)
    else:
        output[r,c] = input[r,c]
```

- 颜色 9 的矩形区域被用作"镜面"：将矩形一侧的图案对称复制到另一侧(垂直/水平/对角反射)，从而填充矩形内部。
- 非 9 的所有其他颜色完全保持不变。颜色 9 本身在输出中不存在。

## 2. 关键证据

- 所有 4 个 train 样例和 1 个 test 样例均为 30x30 且全色域。
- train[0]: 中心有 9 色矩形区域(~78px)，输出被替换为周围图案的镜像(包括 1,3,4,5,6,7,8 等颜色)，形成完整对称的装饰图案。
- train[1]/[2]/[3]: 类似, 9 色区域被反射填充而非简单 9→0。
- 所有非 9 颜色在输入输出间完全一致(逐像素相同)。
- arc-gen 含 262 个额外样例，全部遵循镜像填充规则。

## 3. 歧义与风险

- 反射轴如何确定？取决于 9 色区域的形状和位置。可能是沿矩形中心线反射。风险: `low`。
- 多个 9 区域互相重叠或相邻时反射规则是否复杂化？当前各样例中的 9 区域独立。风险: `low`。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: global (反射需要全局信息)
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 很难用纯 Conv 实现。反射填充需要全局位置感知。
- 可考虑: (1) 用 Conv 检测 9 区域边界和矩形范围；(2) 用坐标 transform 实现反射映射，即 `out[r,c] = in[reflect_r(r), reflect_c(c)]`；(3) 将 9 区域的输出替换为反射位置的像素值。
- 注意保留非 9 区域的原始值(即非 9 区域 output = input)。
- 避免大量中间张量：用 mask 合并输入和反射结果。

## 5. 最终摘要

```yaml
task_id: 074
primitive_types: [mirror_reflection, inpainting, symmetry_completion]
input_shape_rule: 30x30
output_shape_rule: 30x30
formal_rule_short: Replace maroon(9) rectangular patches with mirror-reflected content from surrounding area
locality: global
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
memory_priority: Generate reflection coordinates as indices, not as large intermediate tensors
fusion_hint: Detect 9-region bounding box, compute reflection mapping, apply via gather-like operation
main_risk: Determining reflection axis per example
confidence: high
```
