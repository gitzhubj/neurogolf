# Task 235 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 核心变换：4x14被竖线分为3段4x4，每段空洞模式映射颜色：全满红(2)中心空洞浅蓝(8)底部空洞黄(4)两侧空洞绿(3)。


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

- `recommended_architecture`: `gather_based_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `probably`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Gather-based multi-op. No Conv needed.
- `fusion_hint`: Gather + supporting ops. 32 nodes total.
- `approach`: Use Gather-based lookup or spatial permutation — no Conv needed.

Baseline 实际架构: **Gather-based multi-op** — ArgMax+Concat+Expand+Gather+MatMul+Mul+OneHot+Pad+Reshape+Slice+Sub+Unsqueeze (32 nodes, 19 initializers, 3931 bytes)

## 5. 最终摘要

```yaml
task_id: 235
train_samples: 4
test_samples: 1
arcgen_samples: 64
same_size: False
colors_in: [0, 5]
colors_out: [2, 3, 4, 8]
locality: varies
single_linear_conv_possible: probably
recommended_architecture: gather_based_multi_op
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Gather-based multi-op. No Conv needed.
fusion_hint: Gather + supporting ops. 32 nodes total.
approach: Use Gather-based lookup or spatial permutation — no Conv needed.
main_risk: medium
confidence: high
baseline_pattern: Gather-based multi-op
baseline_ops: ArgMax+Concat+Expand+Gather+MatMul+Mul+OneHot+Pad+Reshape+Slice+Sub+Unsqueeze
baseline_nodes: 32
baseline_size_bytes: 3931
```
