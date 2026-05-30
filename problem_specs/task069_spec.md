# Task 069 规范

## 1. 核心规则

- 核心变换：彩色模板图案替换全图中所有同形状的天蓝(8)区域。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 源模式的识别:"不包含颜色 8 的连通块"在所有样例中均成立。但如果存在多个不含 8 的块,需要额外规则选择(当前样例中只有一个)。风险:medium。
- 目标块的形状匹配:目标块必须与源模式的形状(逐行像素数)完全一致,否则无法直接替换。目前所有目标块形状相同。风险:medium(test 可能不同)。
- 源模式的"对齐":源模式左上角对齐到目标块的左上角。风险:low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 380 nodes: And+Cast+Conv+Gather+Greater+Less+Mul+OneHot+Pad+ReduceSum+S. Study baseline for optimal op sequence.

Baseline 实际架构: And+Cast+Conv+Gather+Greater+Less+Mul+OneHot+Pad+ReduceSum+Squeeze+Sub+Sum+Where (380 nodes, 43 initializers)

## 5. 最终摘要

```yaml
task_id: 069
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 380 nodes: And+Cast+Conv+Gather+Greater+Less+Mul+OneHot+Pad+ReduceSum+S. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: And+Cast+Conv+Gather+Greater+Less+Mul+OneHot+Pad+ReduceSum+Squeeze+Sub+Sum+Where
actual_nodes: 380
```
