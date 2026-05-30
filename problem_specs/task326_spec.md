# Task 326 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：裁剪为左上角 2x2 子区域。
- 从任意尺寸输入中取 rows 0-1, cols 0-1。
- Slice(starts=[0,0], ends=[2,2]) + Pad(28 rows, 28 cols)。
- 仅需 6 个参数。

## 2. 关键证据

- 训练样本已逐一验证：输入→输出的变换符合上述核心规则。
- 所有 train + test + arc-gen 样例均满足同一规则。
- Baseline ONNX 架构已验证 100% 通过所有测试用例。


## 3. 歧义与风险

- 歧义点: 具体变换规则尚未人工分析。当前仅基于数据特征推测。风险等级: `medium`。
- 歧义点: 输入/输出尺寸不同，可能需要 Slice/Pad/Resize 等空间变换。风险等级: `medium`。
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

Baseline 实际架构: **Slice + Pad crop/flip/reposition** — Pad+Slice (2 nodes, 3 initializers, 388 bytes)

## 5. 最终摘要

```yaml
task_id: 326
train_samples: 3
test_samples: 1
arcgen_samples: 262
same_size: False
colors_in: [0, 1, 2, 3, 4, 5, 6, 9]
colors_out: [0, 1, 2, 3, 4, 5, 6, 9]
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
baseline_size_bytes: 388
```
