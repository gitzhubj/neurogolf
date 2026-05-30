# Task 207 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：异象限检测：5x5被零行零列分为4个2x2象限，3个相同，输出唯一不同的象限。


## 2. 关键证据

- 训练样本已验证：所有 train 样例均符合上述核心规则。
- 规则对所有 train + test + arc-gen 样例一致。
- Baseline ONNX 架构已验证 100% 通过。


## 3. 歧义与风险

- 歧义点: 具体变换规则尚未人工分析。当前仅基于数据特征推测。风险等级: `medium`。
- 歧义点: 输入/输出尺寸不同，可能需要 Slice/Pad/Resize 等空间变换。风险等级: `medium`。
- Baseline 已验证可用，架构方向可信。风险等级: `low`。

## 4. NeuroGolf 架构提示

> **以下内容来自 baseline ONNX（已验证 100% 通过所有测试用例）**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional logic. No Conv required.
- `fusion_hint`: ReduceSum/ReduceMax + Greater/Equal + Where. 21 nodes.
- `approach`: Use ReduceSum/ReduceMax + threshold logic — no Conv needed.

Baseline 实际架构: **Reduce + Where conditional** — ArgMax+Concat+Gather+Greater+Neg+Pad+ReduceSum+Reshape+Slice+Sum+Where (21 nodes, 15 initializers, 2330 bytes)

## 5. 最终摘要

```yaml
task_id: 207
train_samples: 3
test_samples: 1
arcgen_samples: 261
same_size: False
colors_in: [0, 1, 2, 5, 8]
colors_out: [0, 1, 2, 5, 8]
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Reduce + threshold + conditional logic. No Conv required.
fusion_hint: ReduceSum/ReduceMax + Greater/Equal + Where. 21 nodes.
approach: Use ReduceSum/ReduceMax + threshold logic — no Conv needed.
main_risk: medium
confidence: high
baseline_pattern: Reduce + Where conditional
baseline_ops: ArgMax+Concat+Gather+Greater+Neg+Pad+ReduceSum+Reshape+Slice+Sum+Where
baseline_nodes: 21
baseline_size_bytes: 2330
```
