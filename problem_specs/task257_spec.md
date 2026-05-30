# Task 257 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：四象限优先：9x9由蓝(1)行列分为4个4x4象限，逐像素取4象限中首个非零值。


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

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Complex multi-op architecture (16 nodes). Study baseline directly.
- `fusion_hint`: Ops: Concat+Mul+Pad+Slice+Sub...
- `approach`: Study baseline ONNX directly for optimal architecture.

Baseline 实际架构: **Custom multi-op** — Concat+Mul+Pad+Slice+Sub (16 nodes, 11 initializers, 1669 bytes)

## 5. 最终摘要

```yaml
task_id: 257
train_samples: 6
test_samples: 1
arcgen_samples: 262
same_size: False
colors_in: [0, 1, 4, 6, 7, 8]
colors_out: [0, 4, 6, 7, 8]
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
recommended_kernel: varies
nonlinearity_needed: unknown
memory_priority: Complex multi-op architecture (16 nodes). Study baseline directly.
fusion_hint: Ops: Concat+Mul+Pad+Slice+Sub...
approach: Study baseline ONNX directly for optimal architecture.
main_risk: high
confidence: medium
baseline_pattern: Custom multi-op
baseline_ops: Concat+Mul+Pad+Slice+Sub
baseline_nodes: 16
baseline_size_bytes: 1669
```
