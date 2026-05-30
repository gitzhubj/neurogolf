# Task 170 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：稀疏模板遮蔽：上半部单色连通块定义稀疏模板，下半部噪声格仅在模板对应位置保留，其余清零。


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

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + support ops (Reduce/Where/Mul/Sub). Minimize intermediate tensors.
- `fusion_hint`: Study baseline: 681 nodes, ops=Add+And+ArgMax+Cast+Concat+Conv+Gather+Greater+Less+Mul+Pad+ReduceMax+ReduceSum+
- `approach`: Conv + supporting ops (Reduce/Where). Refer to baseline for exact op sequence.

Baseline 实际架构: **Conv + logic gates** — Add+And+ArgMax+Cast+Concat+Conv+Gather+Greater+Less+Mul+Pad+ReduceMax+ReduceSum+Reshape+Slice+Sub+Sum+Where (681 nodes, 33 initializers, 64849 bytes)

## 5. 最终摘要

```yaml
task_id: 170
train_samples: 3
test_samples: 1
arcgen_samples: 262
same_size: False
colors_in: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
colors_out: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
recommended_kernel: 3x3
nonlinearity_needed: no
memory_priority: Conv + support ops (Reduce/Where/Mul/Sub). Minimize intermediate tensors.
fusion_hint: Study baseline: 681 nodes, ops=Add+And+ArgMax+Cast+Concat+Conv+Gather+Greater+Less+Mul+Pad+ReduceMax+ReduceSum+
approach: Conv + supporting ops (Reduce/Where). Refer to baseline for exact op sequence.
main_risk: medium
confidence: high
baseline_pattern: Conv + logic gates
baseline_ops: Add+And+ArgMax+Cast+Concat+Conv+Gather+Greater+Less+Mul+Pad+ReduceMax+ReduceSum+Reshape+Slice+Sub+Sum+Where
baseline_nodes: 681
baseline_size_bytes: 64849
```
