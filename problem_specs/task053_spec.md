# Task 053 规范

## 1. 核心规则

- 核心变换：整体下移一行。第一行清空为背景(0)，原行0→行1，原行1→行2，原行2移出。
- 输入 3x3 网格，输出 3x3 网格。
- 行映射：output[0]=background(0), output[1]=input[0], output[2]=input[1]。
- 使用 Gather(axis=2) 行索引重排。

## 2. 关键证据

- 训练样本已逐一验证：输入→输出的变换符合上述核心规则。
- 所有 train + test + arc-gen 样例均满足同一规则。
- Baseline ONNX 架构已验证 100% 通过所有测试用例。


## 3. 歧义与风险

- 歧义点：最底行图案下移是否应包裹回顶行。当前解释：直接丢弃（arc-gen 中无包裹回顶的证据）。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `gather_spatial`
- `locality`: `1`
- `single_linear_conv_possible`: `yes`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Use Gather(axis=2/3, indices=[row/col_order]) instead of Conv. Saves 96% params.
- `fusion_hint`: Single Gather node on spatial axis for permutation.

Baseline 实际架构: Gather (1 nodes, 1 initializers)

## 5. 最终摘要

```yaml
task_id: 053
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: 1
single_linear_conv_possible: yes
recommended_architecture: gather_spatial
memory_priority: Use Gather(axis=2/3, indices=[row/col_order]) instead of Conv. Saves 96% params.
fusion_hint: Single Gather node on spatial axis for permutation.
main_risk: low — pattern confirmed by baseline
confidence: high
actual_ops: Gather
actual_nodes: 1
```
