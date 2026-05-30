# Task 364 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：绿(3)连通组件按拓扑着色：L形/角形(2端点)蓝(1)，T形/Y形(3端点)红(2)，U形/框形品红(6)。


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

- `recommended_architecture`: `gather_based_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `probably`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Gather-based multi-op. No Conv needed.
- `fusion_hint`: Gather + supporting ops. 104 nodes total.
- `approach`: Use Gather-based lookup or spatial permutation — no Conv needed.

Baseline 实际架构: **Gather-based multi-op** — And+Cast+Concat+Gather+Greater+Less+MaxPool+Min+Pad+Slice+Sub+Sum (104 nodes, 57 initializers, 8082 bytes)

## 5. 最终摘要

```yaml
task_id: 364
train_samples: 3
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [0, 3]
colors_out: [0, 1, 2, 6]
locality: varies
single_linear_conv_possible: probably
recommended_architecture: gather_based_multi_op
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Gather-based multi-op. No Conv needed.
fusion_hint: Gather + supporting ops. 104 nodes total.
approach: Use Gather-based lookup or spatial permutation — no Conv needed.
main_risk: medium
confidence: high
baseline_pattern: Gather-based multi-op
baseline_ops: And+Cast+Concat+Gather+Greater+Less+MaxPool+Min+Pad+Slice+Sub+Sum
baseline_nodes: 104
baseline_size_bytes: 8082
```
