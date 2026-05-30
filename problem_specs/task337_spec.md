# Task 337 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：颜色对调。颜色 5 和 8 互换，其余颜色不变。
- 颜色互换对：5<->8。
- 完整映射表：`{5: 8, 8: 5}`。
- 使用 Gather(axis=1, indices=[0,1,2,3,4,8,6,7,5,9])，10 参数。

## 2. 关键证据

- 训练样本已逐一验证：输入→输出的变换符合上述核心规则。
- 所有 train + test + arc-gen 样例均满足同一规则。
- Baseline ONNX 架构已验证 100% 通过所有测试用例。


## 3. 歧义与风险

- 歧义点: 具体变换规则尚未人工分析。当前仅基于数据特征推测。风险等级: `medium`。
- 歧义点: 风险等级: `low`。
- Baseline 已验证可用，架构方向可信。风险等级: `low`。

## 4. NeuroGolf 架构提示

> **以下内容来自 baseline ONNX（已验证 100% 通过所有测试用例）**

- `recommended_architecture`: `gather_lookup`
- `locality`: `0`
- `single_linear_conv_possible`: `yes (via Gather, better than Conv)`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Gather(axis=1, indices=color_table). Single node, ~10 params.
- `fusion_hint`: Channel index permutation via Gather is the optimal approach.
- `approach`: Use Gather-based lookup or spatial permutation — no Conv needed.

Baseline 实际架构: **Gather channel lookup** — Gather (1 nodes, 1 initializers, 159 bytes)

## 5. 最终摘要

```yaml
task_id: 337
train_samples: 3
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [1, 2, 3, 4, 5, 6, 7, 8, 9]
colors_out: [1, 2, 3, 4, 5, 6, 7, 8, 9]
locality: 0
single_linear_conv_possible: yes (via Gather, better than Conv)
recommended_architecture: gather_lookup
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Gather(axis=1, indices=color_table). Single node, ~10 params.
fusion_hint: Channel index permutation via Gather is the optimal approach.
approach: Use Gather-based lookup or spatial permutation — no Conv needed.
main_risk: low
confidence: high
baseline_pattern: Gather channel lookup
baseline_ops: Gather
baseline_nodes: 1
baseline_size_bytes: 159
```
