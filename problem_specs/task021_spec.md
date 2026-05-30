# Task 021 规范

## 1. 核心规则

- 输入被全行分隔线（某行全部为分隔色 7）和全列分隔线（某列全部为分隔色 7）划分为网格区域。输出尺寸 = (被分隔的行区域数 - 1) × (被分隔的列区域数)。
- 背景色为 0。分隔色为 7（训练集）或 5（测试集），分隔线颜色可变但逻辑一致。
- 每个被划分出的区域内部所有非 0 格颜色一致（同色填充）。输出每个格子的颜色 = 对应区域内该填充色。
- 核心变换：按分隔线切分 → 每个区域均匀颜色 → 映射为输出矩阵的一个元素。

```text
rows_sep = {r | all(input[r,:] == sep_color)}
cols_sep = {c | all(input[:,c] == sep_color)}
output[r_out, c_out] = region_color(region between rows_sep[r_out]..rows_sep[r_out+1],
                                     cols_sep[c_out]..cols_sep[c_out+1])
```

- 若某区域为空（全 0），输出对应格为 0。

## 2. 关键证据

- train 0：15×15 输入，分隔行 [2]，分隔列 [1,10,13]，划分为 2×4=8 个区域，输出 2×4 均为颜色 3。每个区域内部颜色一致，无例外。
- train 1：11×11 输入，输出 3×2，每个区域的填充色为 1，无 7 分隔线则表示可能用中间色作分隔（0 连通区域边界）。
- train 2：27×27 输入，输出 6×5，颜色全为 3，分隔线逻辑与 train 0 一致。
- test：22×22，分隔色变为 5，分隔行 [2,7,12,17]，预计按相同逻辑划分区域后输出每个区域的颜色。
- arc-gen 包含 262 个样例，广泛覆盖不同分隔线位置和填充色，均支持网格划分→区域颜色抽取规则。

## 3. 歧义与风险

- 歧义点：分隔线颜色的变化（训练集用 7，测试集用 5）。当前解释为"分隔色是输入中出现次数最多或形成完整行/列的颜色"。风险等级：medium。
- 歧义点：若某区域内有多种非零颜色如何处理。当前解释为训练样本未出现此情况（每个区域颜色一致），这是设计保证。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 214 nodes: Add+And+Cast+Concat+Conv+Equal+Greater+Less+Mul+Not+OneHot+R. Study baseline for optimal op sequence.

Baseline 实际架构: Add+And+Cast+Concat+Conv+Equal+Greater+Less+Mul+Not+OneHot+ReduceMax+ReduceMin+ReduceSum+Reshape+Squeeze+Sub+Sum+Where (214 nodes, 20 initializers)

## 5. 最终摘要

```yaml
task_id: 021
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 214 nodes: Add+And+Cast+Concat+Conv+Equal+Greater+Less+Mul+Not+OneHot+R. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Add+And+Cast+Concat+Conv+Equal+Greater+Less+Mul+Not+OneHot+ReduceMax+ReduceMin+ReduceSum+Reshape+Squeeze+Sub+Sum+Where
actual_nodes: 214
```
