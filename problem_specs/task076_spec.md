# Task 076 规范

## 1. 核心规则

- 核心变换：补全黄色(4)十字核心周围缺失的绿(3)蓝(1)交替边框，红(2)标记端点。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 对称轴如何确定？似乎以黄色框架的中心线为对称轴进行反射。风险: `medium`。
- 不同框架之间是否有交互(跨框架复制)？当前未观察到跨框架复制，只在框架内操作。风险: `medium`。
- 如果黄色框架不是矩形会怎样？所有样例中黄色框架均为矩形轮廓。风险: `low`。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 220 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Add+ArgMax+Cast+Concat+Div+Expand+Gather+GatherElements+Greater+Less+MatMul+Max+MaxPool+Mod+Mul+OneHot+Pad+Pow+ReduceMax+ReduceSum+Reshape+Slice+Squeeze+Sub+TopK+Transpose+Unsqueeze (220 nodes, 44 initializers)

## 5. 最终摘要

```yaml
task_id: 076
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 220 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Add+ArgMax+Cast+Concat+Div+Expand+Gather+GatherElements+Greater+Less+MatMul+Max+MaxPool+Mod+Mul+OneHot+Pad+Pow+ReduceMax+ReduceSum+Reshape+Slice+Squeeze+Sub+TopK+Transpose+Unsqueeze
actual_nodes: 220
```
