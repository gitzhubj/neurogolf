# Task 087 规范

## 1. 核心规则

- 核心变换：180° 旋转（等效于水平翻转 + 垂直翻转）。
- output[r][c] = input[H-1-r][W-1-c]。
- 使用 Slice(step=[-1,-1]) 双轴反向 + Pad 恢复到 30x30。
- 仅需 5 个参数（starts, ends, output_pads）。

## 2. 关键证据

- 训练样本已逐一验证：输入→输出的变换符合上述核心规则。
- 所有 train + test + arc-gen 样例均满足同一规则。
- Baseline ONNX 架构已验证 100% 通过所有测试用例。


## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `slice_pad`
- `locality`: `0`
- `single_linear_conv_possible`: `yes`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Slice to crop, Pad to restore 30x30. Minimal memory.
- `fusion_hint`: Two nodes: Slice(extract) + Pad(restore). Step=-1 gives free flip.

Baseline 实际架构: Pad+Slice (2 nodes, 5 initializers)

## 5. 最终摘要

```yaml
task_id: 087
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: 0
single_linear_conv_possible: yes
recommended_architecture: slice_pad
memory_priority: Slice to crop, Pad to restore 30x30. Minimal memory.
fusion_hint: Two nodes: Slice(extract) + Pad(restore). Step=-1 gives free flip.
main_risk: low — pattern confirmed by baseline
confidence: high
actual_ops: Pad+Slice
actual_nodes: 2
```
