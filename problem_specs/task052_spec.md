# Task 052 规范

## 1. 核心规则

- 核心变换：行一致检测：一行中3个元素全部相同则输出灰色(5)，否则全黑。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点：若某行全为 0 是否填 5。当前解释：全零行在样例中不存在，推断全零行也符合"全同"规则但 0 不会被选为输出颜色（输出只有 0 和 5，全零行输出为 5 的概率低）。风险等级：low。
- 歧义点：是否存在全 5 输入。当前解释：5 不出现在输入中（cin 为 [1,2,3,4,6,7,9]），不会混淆。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 10 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Equal+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum+Where (10 nodes, 12 initializers)

## 5. 最终摘要

```yaml
task_id: 052
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 10 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Equal+Mul+Pad+ReduceMax+ReduceSum+Slice+Sub+Sum+Where
actual_nodes: 10
```
