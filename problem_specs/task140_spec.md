# Task 140 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：180° 旋转（与 task087 相同）。
- output[r][c] = input[H-1-r][W-1-c]。
- 使用 Slice(step=[-1,-1]) 双轴反向 + Pad 恢复。
- 仅需 5 个参数。

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

- `recommended_architecture`: `slice_pad`
- `locality`: `0`
- `single_linear_conv_possible`: `yes (via Slice+Pad)`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Slice to extract/crop/flip, Pad to restore 30x30.
- `fusion_hint`: Step=-1 in Slice gives free flip. Pad mode=constant for background fill.
- `approach`: Use Slice+Pad for spatial crop/flip/reposition — no Conv needed.

Baseline 实际架构: **Slice + Pad crop/flip/reposition** — Pad+Slice (2 nodes, 5 initializers, 474 bytes)

## 5. 最终摘要

```yaml
task_id: 140
train_samples: 2
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [0, 1, 2, 3, 4, 5, 6, 7, 8]
colors_out: [0, 1, 2, 3, 4, 5, 6, 7, 8]
locality: 0
single_linear_conv_possible: yes (via Slice+Pad)
recommended_architecture: slice_pad
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Slice to extract/crop/flip, Pad to restore 30x30.
fusion_hint: Step=-1 in Slice gives free flip. Pad mode=constant for background fill.
approach: Use Slice+Pad for spatial crop/flip/reposition — no Conv needed.
main_risk: low
confidence: high
baseline_pattern: Slice + Pad crop/flip/reposition
baseline_ops: Pad+Slice
baseline_nodes: 2
baseline_size_bytes: 474
```
