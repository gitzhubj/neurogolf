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

- recommended_architecture: single_3x3_conv（检测上方行的色点并做交替扩散）
- locality: 1（每行仅依赖上一行和上行相邻列）
- single_linear_conv_possible: probably
- recommended_kernel: 3x3
- nonlinearity_needed: no（纯线性位移和交替模式可用 3×3 Conv 实现）

## 5. 最终摘要

```yaml
task_id: 082
primitive_types: [vertical_diffraction, alternating_pattern, seed_propagation]
input_shape_rule: 6xW (W varies)
output_shape_rule: same as input
formal_rule_short: each color dot on row 0 propagates downward in an alternating X-0-X pattern
locality: 1
single_linear_conv_possible: probably
recommended_architecture: single_3x3_conv
main_risk: none
confidence: high
```
