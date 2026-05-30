# Task 006 规范

## 1. 核心规则

- 核心变换：左右AND匹配：3x7输入以灰色(5)列分离左右两个3x3区域，逐像素AND运算，结果1替换为2。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：序列的读取方向和起始位置。当前解释：从最小 r+c 值（左上角附近）开始沿反对角线（r+c 递增）读取非零值，用该序列按 (r+c) mod L 平铺。但不同样例中序列起始点在输出中的对齐方式可能不同（如 train 1 输出[0,0] = 序列[1] 而非序列[0]）。风险等级：medium。
- 歧义点：序列长度 L 的确定（何时截断）。当前解释：提取所有反对角线上连续出现的非零值直到遇到全零反对角线。风险等级：low。
- 歧义点：若输入有两个不同反对角线上都有非零值且颜色序列不同。当前解释：取最先遇到（最小 r+c）的序列，但可见数据无此歧义。风险等级：medium。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 10 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Mul+Pad+ReduceMax+Slice+Sub+Sum (10 nodes, 10 initializers)

## 5. 最终摘要

```yaml
task_id: 006
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 10 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Mul+Pad+ReduceMax+Slice+Sub+Sum
actual_nodes: 10
```
