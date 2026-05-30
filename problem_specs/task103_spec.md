# Task 103 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：轴对称检测：检测红色(2)像素排列是否轴对称，对称输出蓝(1)，不对称输出橙(7)。


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

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional logic. No Conv required.
- `fusion_hint`: ReduceSum/ReduceMax + Greater/Equal + arithmetic. 11 nodes.
- `approach`: Use ReduceSum/ReduceMax + threshold logic — no Conv needed.

Baseline 实际架构: **Reduce + arithmetic** — Abs+Cast+Gather+Greater+Pad+ReduceSum+Reshape+Slice+Sub (11 nodes, 12 initializers, 1669 bytes)

## 5. 最终摘要

```yaml
task_id: 103
train_samples: 6
test_samples: 2
arcgen_samples: 215
same_size: False
colors_in: [0, 2]
colors_out: [1, 7]
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Reduce + threshold + conditional logic. No Conv required.
fusion_hint: ReduceSum/ReduceMax + Greater/Equal + arithmetic. 11 nodes.
approach: Use ReduceSum/ReduceMax + threshold logic — no Conv needed.
main_risk: medium
confidence: high
baseline_pattern: Reduce + arithmetic
baseline_ops: Abs+Cast+Gather+Greater+Pad+ReduceSum+Reshape+Slice+Sub
baseline_nodes: 11
baseline_size_bytes: 1669
```
