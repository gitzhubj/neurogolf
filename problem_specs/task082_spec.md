# Task 082 规范

## 1. 核心规则

- 输入/输出尺寸相同（6×W）。
- 输入仅在 row 0 有若干离散的非零颜色点（颜色如 2, 4, 3, 6, 7, 8），其余行为全零。
- 核心变换：每个 row 0 的色点沿列方向向下产生交替衍射图案。
- 衍射图案规则：种子格 (0,c) 颜色为 K。对每个后续行 r：
  - 若 r 为奇数：在 (r, c-1) 和 (r, c+1) 填入 K（形成左右扩散）。
  - 若 r 为偶数：在 (r, c) 填入 K（中心回归）。
- 图案在每个色点下方独立叠加。

```text
for each seed at (0, c) with color K:
    for row r from 1 to H-1:
        if r % 2 == 1:
            output[r][c-1] = K, output[r][c+1] = K
        else:
            output[r][c] = K
```

## 2. 关键证据

- train 0：6×10。row 0 有颜色 2（col 1）和 8（col 5）。输出：2 向下衍射（奇数行扩散到 col 0,2；偶数行回到 col 1），8 同理。
- train 1：6×7。仅有颜色 4（col 1），衍射图案完美向下传播。
- test 0：6×12。颜色 3（col 2）、6（col 6）、7（col 9）三个种子点，各自独立产生衍射条纹。

## 3. 歧义与风险

- 歧义点：衍射图案超出网格边界时的处理。当前解释：超出边界的部分截断不输出。风险等级：low。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 18 nodes: Concat+Conv+Mul+Pad+ReduceSum+Slice+Sub+Sum. Study baseline for optimal op sequence.

Baseline 实际架构: Concat+Conv+Mul+Pad+ReduceSum+Slice+Sub+Sum (18 nodes, 10 initializers)

## 5. 最终摘要

```yaml
task_id: 082
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 18 nodes: Concat+Conv+Mul+Pad+ReduceSum+Slice+Sub+Sum. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: Concat+Conv+Mul+Pad+ReduceSum+Slice+Sub+Sum
actual_nodes: 18
```
