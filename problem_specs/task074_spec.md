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

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Multi-op custom architecture (18 nodes). Study baseline directly.
- `fusion_hint`: Ops used: ArgMax+Cast+Equal+Max+Mod+Pad+Slice+Transpose...

Baseline 实际架构: ArgMax+Cast+Equal+Max+Mod+Pad+Slice+Transpose (18 nodes, 13 initializers)

## 5. 最终摘要

```yaml
task_id: 074
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
memory_priority: Multi-op custom architecture (18 nodes). Study baseline directly.
fusion_hint: Ops used: ArgMax+Cast+Equal+Max+Mod+Pad+Slice+Transpose...
main_risk: high — complex architecture, refer to baseline
confidence: medium
actual_ops: ArgMax+Cast+Equal+Max+Mod+Pad+Slice+Transpose
actual_nodes: 18
```
