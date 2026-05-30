# Task 229 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：众数保持：3x3中最频繁颜色保持不变，其他非零像素替换为灰色(5)。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点: 具体变换规则尚未人工分析。当前仅基于数据特征推测。风险等级: `medium`。
- 歧义点: 风险等级: `low`。
- Baseline 已验证可用，架构方向可信。风险等级: `low`。

## 4. NeuroGolf 架构提示

> **以下内容来自 baseline ONNX（已验证 100% 通过所有测试用例）**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional logic. No Conv required.
- `fusion_hint`: ReduceSum/ReduceMax + Greater/Equal + Where. 13 nodes.
- `approach`: Use ReduceSum/ReduceMax + threshold logic — no Conv needed.

Baseline 实际架构: **Reduce + Where conditional** — ArgMax+Equal+Mul+Pad+ReduceSum+Reshape+Slice+Sub+Sum+Where (13 nodes, 12 initializers, 1735 bytes)

## 5. 最终摘要

```yaml
task_id: 229
train_samples: 4
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [1, 2, 3, 4, 8]
colors_out: [1, 2, 3, 4, 5]
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Reduce + threshold + conditional logic. No Conv required.
fusion_hint: ReduceSum/ReduceMax + Greater/Equal + Where. 13 nodes.
approach: Use ReduceSum/ReduceMax + threshold logic — no Conv needed.
main_risk: medium
confidence: high
baseline_pattern: Reduce + Where conditional
baseline_ops: ArgMax+Equal+Mul+Pad+ReduceSum+Reshape+Slice+Sub+Sum+Where
baseline_nodes: 13
baseline_size_bytes: 1735
```
