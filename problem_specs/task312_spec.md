# Task 312 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：所有灰色(5)替换为同行第0列颜色值（行标记色填充该行灰色区域）。


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

- `recommended_architecture`: `slice_based_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `probably`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Slice-based multi-op. No Conv needed.
- `fusion_hint`: Slice + supporting ops. 8 nodes total.
- `approach`: Use Slice+Pad for spatial crop/flip/reposition — no Conv needed.

Baseline 实际架构: **Slice-based multi-op** — Cast+Pad+Slice+Where (8 nodes, 9 initializers, 1202 bytes)

## 5. 最终摘要

```yaml
task_id: 312
train_samples: 2
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [0, 1, 2, 3, 4, 5, 7, 8]
colors_out: [0, 1, 2, 3, 4, 7, 8]
locality: varies
single_linear_conv_possible: probably
recommended_architecture: slice_based_multi_op
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Slice-based multi-op. No Conv needed.
fusion_hint: Slice + supporting ops. 8 nodes total.
approach: Use Slice+Pad for spatial crop/flip/reposition — no Conv needed.
main_risk: medium
confidence: high
baseline_pattern: Slice-based multi-op
baseline_ops: Cast+Pad+Slice+Where
baseline_nodes: 8
baseline_size_bytes: 1202
```
