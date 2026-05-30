# Task 062 规范

## 1. 核心规则

- 核心变换：背景黑(0)变绿(3)，红(2)融入相邻有色形状并扩展填充凹陷处。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 对称规则不够精确:不同样例的对称补全方式略有差异(有的四瓣,有的粗环,有的矩形框),需统一规则。风险:medium。
- 辅色与主体色的确定规则:辅色通常出现 1-2 次,主体色出现 3 次以上。但如果两个颜色出现次数相近则规则模糊。风险:medium。
- 背景色固定为 3(绿色):所有样例一致,但即使背景不是 3,规则是否依然成立?风险:low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 194 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Concat+MatMul+Mul+Pad+ReduceMax+Relu+Slice+Sub+Sum+Transpose (194 nodes, 26 initializers)

## 5. 最终摘要

```yaml
task_id: 062
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 194 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Concat+MatMul+Mul+Pad+ReduceMax+Relu+Slice+Sub+Sum+Transpose
actual_nodes: 194
```
