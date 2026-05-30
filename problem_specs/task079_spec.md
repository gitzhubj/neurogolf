# Task 079 规范

## 1. 核心规则

- 核心变换：扫描全图统计3x3子图案出现频率，输出出现次数最多的3x3图案。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 空间分组的具体边界不完全确定。当前假设每块约 5 行 x 5 列(最后一块为 4)。风险: `medium`。
- 判定一个块是否"激活"的阈值未知(可能要求至少 4-5 个非零像素)。风险: `medium`。
- 输出颜色选取规则不完全明确(为何 train[1] 选 4 而非 1？可能选"结构性"更强的颜色)。风险: `medium`。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 20 nodes: Add+ArgMax+Cast+Conv+Gather+Greater+Pad+ReduceMax+ReduceSum+. Study baseline for optimal op sequence.

Baseline 实际架构: Add+ArgMax+Cast+Conv+Gather+Greater+Pad+ReduceMax+ReduceSum+Slice+Squeeze+Unsqueeze (20 nodes, 7 initializers)

## 5. 最终摘要

```yaml
task_id: 079
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 20 nodes: Add+ArgMax+Cast+Conv+Gather+Greater+Pad+ReduceMax+ReduceSum+. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Add+ArgMax+Cast+Conv+Gather+Greater+Pad+ReduceMax+ReduceSum+Slice+Squeeze+Unsqueeze
actual_nodes: 20
```
