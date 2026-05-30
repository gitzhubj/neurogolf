# Task 262 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：行内灰色定位：3x3每行灰色(5)所在列号决定整行颜色，列0->红(2)列1->黄(4)列2->绿(3)。


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
- `fusion_hint`: Gather + supporting ops. 8 nodes total.
- `approach`: Use Gather-based lookup or spatial permutation — no Conv needed.

Baseline 实际架构: **Gather-based multi-op** — ArgMax+Expand+Gather+OneHot+Pad+Slice+Squeeze+Unsqueeze (8 nodes, 11 initializers, 1329 bytes)

## 5. 最终摘要

```yaml
task_id: 262
train_samples: 4
test_samples: 1
arcgen_samples: 6
same_size: True
colors_in: [0, 5]
colors_out: [2, 3, 4]
locality: varies
single_linear_conv_possible: probably
recommended_architecture: gather_based_multi_op
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Gather-based multi-op. No Conv needed.
fusion_hint: Gather + supporting ops. 8 nodes total.
approach: Use Gather-based lookup or spatial permutation — no Conv needed.
main_risk: medium
confidence: high
baseline_pattern: Gather-based multi-op
baseline_ops: ArgMax+Expand+Gather+OneHot+Pad+Slice+Squeeze+Unsqueeze
baseline_nodes: 8
baseline_size_bytes: 1329
```
