# Task 095 规范

## 1. 核心规则

- 核心变换：每个灰色(5)像素扩展为周围8格蓝色(1)的3x3方块，中心保持灰色(5)。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：当两个 5-像素距离 < 3 时，重叠区域颜色规则。当前解释：5 为中心时优先保留，1 为边框且重叠则按 5 优先。风险等级：medium（当前数据无此类冲突）。
- 歧义点：靠近边界的 5 其 3x3 块被截断。当前解释：边界附近只绘制有效区域内的部分。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `single_conv`
- `locality`: `k`
- `single_linear_conv_possible`: `yes`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Single Conv, bias-free. Keep kernel minimal.
- `fusion_hint`: All logic in one Conv weight tensor.

Baseline 实际架构: Conv (1 nodes, 2 initializers)

## 5. 最终摘要

```yaml
task_id: 095
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: yes
recommended_architecture: single_conv
memory_priority: Single Conv, bias-free. Keep kernel minimal.
fusion_hint: All logic in one Conv weight tensor.
main_risk: low
confidence: high
actual_ops: Conv
actual_nodes: 1
```
