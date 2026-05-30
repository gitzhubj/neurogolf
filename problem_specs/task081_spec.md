# Task 081 规范

## 1. 核心规则

- 输入/输出均为 7×7。
- 输入中包含颜色 8 的"L 形"片段（2-3 个相邻斜对角单元格），其余为 0。
- 核心变换：对每个 8-连通分量的"外角"，在斜对角方向相邻的空格（颜色 0）填入颜色 1。
- 具体地：若某 8 格同时有水平相邻和垂直相邻的 8-邻居，则两者的对角线方向空格填入 1。
- 原始 8-图案保持不变。

## 2. 关键证据

- train 0：两个 8-L 形图案。左侧图案在 (1,1)-(2,2)，斜对角空格 (1,2) 填 1；右侧图案在 (3,4)-(4,5)，空格 (4,4) 填 1。
- train 1：多个 8-L 形分散分布，每个图案对应一个 1 填入其斜对角方向。
- test 0：4 个 L 形图案，各填 1 个空格为 1，均符合规则。
- arc-gen 261 例全部支持。

## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Multi-op custom architecture (35 nodes). Study baseline directly.
- `fusion_hint`: Ops used: And+Concat+Greater+Not+Or+Pad+Slice...

Baseline 实际架构: And+Concat+Greater+Not+Or+Pad+Slice (35 nodes, 17 initializers)

## 5. 最终摘要

```yaml
task_id: 081
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
memory_priority: Multi-op custom architecture (35 nodes). Study baseline directly.
fusion_hint: Ops used: And+Concat+Greater+Not+Or+Pad+Slice...
main_risk: high — complex architecture, refer to baseline
confidence: medium
actual_ops: And+Concat+Greater+Not+Or+Pad+Slice
actual_nodes: 35
```
