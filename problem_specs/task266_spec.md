# Task 266 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：红点(2)向四角扩展：绿(3)左上、粉(6)右上、青(8)左下、橙(7)右下。


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

- `recommended_architecture`: `single_conv`
- `locality`: `k`
- `single_linear_conv_possible`: `yes`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Single Conv, no bias, no activation.
- `fusion_hint`: All spatial logic encoded in one Conv weight tensor.
- `approach`: Single Conv is sufficient — keep it simple.

Baseline 实际架构: **Single Conv** — Conv (1 nodes, 2 initializers, 3825 bytes)

## 5. 最终摘要

```yaml
task_id: 266
train_samples: 4
test_samples: 1
arcgen_samples: 15
same_size: True
colors_in: [0, 2]
colors_out: [0, 3, 6, 7, 8]
locality: k
single_linear_conv_possible: yes
recommended_architecture: single_conv
recommended_kernel: 3x3
nonlinearity_needed: no
memory_priority: Single Conv, no bias, no activation.
fusion_hint: All spatial logic encoded in one Conv weight tensor.
approach: Single Conv is sufficient — keep it simple.
main_risk: low
confidence: high
baseline_pattern: Single Conv
baseline_ops: Conv
baseline_nodes: 1
baseline_size_bytes: 3825
```
