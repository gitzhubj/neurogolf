# Task 389 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：颜色交换：灰色(5)替换为输入中另一种前景色，原前景色位置清零。


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

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + support ops (Reduce/Where/Mul/Sub). Minimize intermediate tensors.
- `fusion_hint`: Study baseline: 13 nodes, ops=ArgMax+Conv+Mul+OneHot+ReduceMax+Reshape+Sum
- `approach`: Conv + supporting ops (Reduce/Where). Refer to baseline for exact op sequence.

Baseline 实际架构: **Conv + logic gates** — ArgMax+Conv+Mul+OneHot+ReduceMax+Reshape+Sum (13 nodes, 9 initializers, 1421 bytes)

## 5. 最终摘要

```yaml
task_id: 389
train_samples: 3
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [3, 4, 5, 6, 9]
colors_out: [0, 3, 4, 6, 9]
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
recommended_kernel: 3x3
nonlinearity_needed: no
memory_priority: Conv + support ops (Reduce/Where/Mul/Sub). Minimize intermediate tensors.
fusion_hint: Study baseline: 13 nodes, ops=ArgMax+Conv+Mul+OneHot+ReduceMax+Reshape+Sum
approach: Conv + supporting ops (Reduce/Where). Refer to baseline for exact op sequence.
main_risk: medium
confidence: high
baseline_pattern: Conv + logic gates
baseline_ops: ArgMax+Conv+Mul+OneHot+ReduceMax+Reshape+Sum
baseline_nodes: 13
baseline_size_bytes: 1421
```
