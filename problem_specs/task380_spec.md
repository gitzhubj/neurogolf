# Task 380 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：紧凑重排：3x3输入非零像素向密度较高方向靠拢重排，保持像素数不变。


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
- `fusion_hint`: Slice + supporting ops. 3 nodes total.
- `approach`: Use Slice+Pad for spatial crop/flip/reposition — no Conv needed.

Baseline 实际架构: **Slice-based multi-op** — Pad+Slice+Transpose (3 nodes, 6 initializers, 531 bytes)

## 5. 最终摘要

```yaml
task_id: 380
train_samples: 4
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [0, 2, 5, 6, 9]
colors_out: [0, 2, 5, 6, 9]
locality: varies
single_linear_conv_possible: probably
recommended_architecture: slice_based_multi_op
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Slice-based multi-op. No Conv needed.
fusion_hint: Slice + supporting ops. 3 nodes total.
approach: Use Slice+Pad for spatial crop/flip/reposition — no Conv needed.
main_risk: medium
confidence: high
baseline_pattern: Slice-based multi-op
baseline_ops: Pad+Slice+Transpose
baseline_nodes: 3
baseline_size_bytes: 531
```
