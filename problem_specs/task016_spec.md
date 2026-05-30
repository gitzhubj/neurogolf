# Task 016 规范

## 1. 核心规则

- 核心变换：逐像素颜色映射（同尺寸，4对颜色互换）。
- 颜色互换对：1<->5, 2<->6, 3<->4, 8<->9。
- 完整映射表：`{1:5, 2:6, 3:4, 4:3, 5:1, 6:2, 8:9, 9:8}`。
- 未出现的颜色(0,7)保持恒等映射。
- 使用 Gather(axis=1, indices=[0,5,6,4,3,1,2,7,9,8])，仅 10 参数。

## 2. 关键证据

- 训练样本已逐一验证：输入→输出的变换符合上述核心规则。
- 所有 train + test + arc-gen 样例均满足同一规则。
- Baseline ONNX 架构已验证 100% 通过所有测试用例。


## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `gather_lookup`
- `locality`: `0`
- `single_linear_conv_possible`: `yes`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Use Gather(axis=1, indices=[color_table]) instead of 1x1 Conv. Saves 90% params.
- `fusion_hint`: Single Gather node. Channel index permutation is all that is needed.

Baseline 实际架构: Gather (1 nodes, 1 initializers)

## 5. 最终摘要

```yaml
task_id: 016
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: 0
single_linear_conv_possible: yes
recommended_architecture: gather_lookup
memory_priority: Use Gather(axis=1, indices=[color_table]) instead of 1x1 Conv. Saves 90% params.
fusion_hint: Single Gather node. Channel index permutation is all that is needed.
main_risk: low — pattern confirmed by baseline
confidence: high
actual_ops: Gather
actual_nodes: 1
```
