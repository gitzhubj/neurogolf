# Task 322 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 输入尺寸: 3x3 (all same)，输出尺寸: 3x3 (all same)。
- 同尺寸变换: 是。
- 输入颜色: [0, 2, 3, 4, 6, 7, 8]，输出颜色: [0, 2, 3, 4, 6, 7, 8]。
- 颜色集一致: 是。
- 推测任务类型: pixel_color_mapping_or_permutation。

> **注意**: 以上为数据特征自动提取。具体变换规则需人工/LLM 分析 train/test 样例后补充。

## 2. 关键证据

- 训练样本: 3 个，测试样本: 1 个，ARC-GEN 样本: 262 个。
- 输入样例可能包含多种尺寸和颜色组合，详见 `input/task322.json`。
- 架构方案已由 baseline ONNX 验证通过（9 节点，1194 字节）。

> **建议**: 运行 `python tools/task_scanner.py` 查看任务分类，或手动查看 `input/task322.json`。

## 3. 歧义与风险

- 歧义点: 具体变换规则尚未人工分析。当前仅基于数据特征推测。风险等级: `medium`。
- 歧义点: 风险等级: `low`。
- Baseline 已验证可用，架构方向可信。风险等级: `low`。

## 4. NeuroGolf 架构提示

> **以下内容来自 baseline ONNX（已验证 100% 通过所有测试用例）**

- `recommended_architecture`: `reduce_only`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional logic. No Conv required.
- `fusion_hint`: ReduceSum/ReduceMax + Greater/Equal + arithmetic. 9 nodes.
- `approach`: Use ReduceSum/ReduceMax + threshold logic — no Conv needed.

Baseline 实际架构: **Reduce + arithmetic** — Cast+Concat+MaxPool+Pad+ReduceMax+Slice+Sub (9 nodes, 6 initializers, 1194 bytes)

## 5. 最终摘要

```yaml
task_id: 322
train_samples: 3
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [0, 2, 3, 4, 6, 7, 8]
colors_out: [0, 2, 3, 4, 6, 7, 8]
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_only
recommended_kernel: not_needed
nonlinearity_needed: no
memory_priority: Reduce + threshold + conditional logic. No Conv required.
fusion_hint: ReduceSum/ReduceMax + Greater/Equal + arithmetic. 9 nodes.
approach: Use ReduceSum/ReduceMax + threshold logic — no Conv needed.
main_risk: medium
confidence: high
baseline_pattern: Reduce + arithmetic
baseline_ops: Cast+Concat+MaxPool+Pad+ReduceMax+Slice+Sub
baseline_nodes: 9
baseline_size_bytes: 1194
```
