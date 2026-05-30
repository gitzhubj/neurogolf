# Task 273 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 输入尺寸: 10x10 (all same)，输出尺寸: 10x10 (all same)。
- 同尺寸变换: 是。
- 输入颜色: [0, 4]，输出颜色: [0, 2, 4]。
- 颜色集一致: 否。
- 推测任务类型: local_neighborhood_or_global_statistics。

> **注意**: 以上为数据特征自动提取。具体变换规则需人工/LLM 分析 train/test 样例后补充。

## 2. 关键证据

- 训练样本: 3 个，测试样本: 1 个，ARC-GEN 样本: 262 个。
- 输入样例可能包含多种尺寸和颜色组合，详见 `input/task273.json`。
- 架构方案已由 baseline ONNX 验证通过（22 节点，2414 字节）。

> **建议**: 运行 `python tools/task_scanner.py` 查看任务分类，或手动查看 `input/task273.json`。

## 3. 歧义与风险

- 歧义点: 具体变换规则尚未人工分析。当前仅基于数据特征推测。风险等级: `medium`。
- 歧义点: 风险等级: `low`。
- Baseline 已验证可用，架构方向可信。风险等级: `low`。

## 4. NeuroGolf 架构提示

> **以下内容来自 baseline ONNX（已验证 100% 通过所有测试用例）**

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Complex multi-op architecture (22 nodes). Study baseline directly.
- `fusion_hint`: Ops: And+CumSum+Equal+Greater+Mul+Not+Pad+Slice+Sum+Where...
- `approach`: Study baseline ONNX directly for optimal architecture.

Baseline 实际架构: **Custom multi-op** — And+CumSum+Equal+Greater+Mul+Not+Pad+Slice+Sum+Where (22 nodes, 13 initializers, 2414 bytes)

## 5. 最终摘要

```yaml
task_id: 273
train_samples: 3
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [0, 4]
colors_out: [0, 2, 4]
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
recommended_kernel: varies
nonlinearity_needed: unknown
memory_priority: Complex multi-op architecture (22 nodes). Study baseline directly.
fusion_hint: Ops: And+CumSum+Equal+Greater+Mul+Not+Pad+Slice+Sum+Where...
approach: Study baseline ONNX directly for optimal architecture.
main_risk: high
confidence: medium
baseline_pattern: Custom multi-op
baseline_ops: And+CumSum+Equal+Greater+Mul+Not+Pad+Slice+Sum+Where
baseline_nodes: 22
baseline_size_bytes: 2414
```
