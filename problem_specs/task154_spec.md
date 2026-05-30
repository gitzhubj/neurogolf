# Task 154 规范

> **Auto-generated spec** — 规则分析基于数据特征推断，架构提示来自 baseline ONNX（已验证可用）。

## 1. 核心规则

- 输入尺寸: 15x15 (all same)，输出尺寸: 15x15 (all same)。
- 同尺寸变换: 是。
- 输入颜色: [0, 2, 5]，输出颜色: [0, 2, 5]。
- 颜色集一致: 是。
- 推测任务类型: local_neighborhood_or_global_statistics。

> **注意**: 以上为数据特征自动提取。具体变换规则需人工/LLM 分析 train/test 样例后补充。

## 2. 关键证据

- 训练样本: 3 个，测试样本: 1 个，ARC-GEN 样本: 262 个。
- 输入样例可能包含多种尺寸和颜色组合，详见 `input/task154.json`。
- 架构方案已由 baseline ONNX 验证通过（43 节点，7650 字节）。

> **建议**: 运行 `python tools/task_scanner.py` 查看任务分类，或手动查看 `input/task154.json`。

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
- `fusion_hint`: Study baseline: 43 nodes, ops=Add+Cast+Concat+Conv+Greater+Less+MatMul+Mul+OneHot+ReduceMax+ReduceMin+Split+Sq
- `approach`: Conv + supporting ops (Reduce/Where). Refer to baseline for exact op sequence.

Baseline 实际架构: **Conv + logic gates** — Add+Cast+Concat+Conv+Greater+Less+MatMul+Mul+OneHot+ReduceMax+ReduceMin+Split+Squeeze+Sub+Where (43 nodes, 8 initializers, 7650 bytes)

## 5. 最终摘要

```yaml
task_id: 154
train_samples: 3
test_samples: 1
arcgen_samples: 262
same_size: True
colors_in: [0, 2, 5]
colors_out: [0, 2, 5]
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
recommended_kernel: 3x3
nonlinearity_needed: no
memory_priority: Conv + support ops (Reduce/Where/Mul/Sub). Minimize intermediate tensors.
fusion_hint: Study baseline: 43 nodes, ops=Add+Cast+Concat+Conv+Greater+Less+MatMul+Mul+OneHot+ReduceMax+ReduceMin+Split+Sq
approach: Conv + supporting ops (Reduce/Where). Refer to baseline for exact op sequence.
main_risk: medium
confidence: high
baseline_pattern: Conv + logic gates
baseline_ops: Add+Cast+Concat+Conv+Greater+Less+MatMul+Mul+OneHot+ReduceMax+ReduceMin+Split+Squeeze+Sub+Where
baseline_nodes: 43
baseline_size_bytes: 7650
```
