# Task 070 规范

## 1. 核心规则

- 输入/输出尺寸相同(17x17)。网格中有零散的颜色 1(蓝色)和颜色 8(浅蓝)像素,其余为 0。
- 核心规则:颜色 8 形成容器壁,颜色 1 形成纹理背景。8 所包围内部区域中的**部分 0 单元格变为 3**(绿色)。

```text
walls = color 8
interior = 4-directionally enclosed region bounded by walls and/or color 1 edges
for each 0-cell:
    if it is adjacent (4-dir) to a wall(8) AND inside the enclosed region:
        output = 3
    else:
        output = input
other cells (1, 8) unchanged
```

- 填充区域为 8 围成的内部空腔中紧邻 8 的 0 单元格。部分不紧邻墙壁的内部 0 可能不填充。
- 颜色 1 构成背景纹理,在 8 形成的容器外部保持不变。

## 2. 关键证据

- train[0]:8 在行 2-6,列 5-9 形成 C 形围栏,内部靠近 8 的 0→3;远离 8 的 0 保持 0;1 纹理和边界保持。
- train[1]:8 在行 7-9,列 0-9 附近形成包围,内部临近 8 的 0→3。
- train[2]:8 形成两个小包围区域,内部 0→3。
- test[0]:8 在行 11-14,列 6-13 附近形成包围,邻近 8 的 0→3。
- arc-gen 有 262 个样例,支持"8 围栏内的 0 填充 3"规则。

## 3. 歧义与风险

- 填充范围:只有紧邻 8 的 0→3,还是内部所有 0→3?样例显示靠近 8 的 0 填充,但内部远端的 0 可能保持。确切规则有待厘清。风险:medium。
- 8 的包围判定:并非所有 8 都形成封闭围栏;只有形成足够围堵的 8 形状才触发填充。风险:medium。
- 颜色 1 的作用:1 似乎是背景纹理填充,不作为墙壁。但 1 可能影响连通性判断。风险:low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 71 nodes: And+Cast+Conv+Greater+Mul+Pad+ReduceMax+Slice+Sum. Study baseline for optimal op sequence.

Baseline 实际架构: And+Cast+Conv+Greater+Mul+Pad+ReduceMax+Slice+Sum (71 nodes, 16 initializers)

## 5. 最终摘要

```yaml
task_id: 070
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 71 nodes: And+Cast+Conv+Greater+Mul+Pad+ReduceMax+Slice+Sum. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: And+Cast+Conv+Greater+Mul+Pad+ReduceMax+Slice+Sum
actual_nodes: 71
```
