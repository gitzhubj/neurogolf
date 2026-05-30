# Task 077 规范

## 1. 核心规则

- 输入/输出尺寸相同(可变)，背景色为 0。
- 输入包含两种非背景色：红色(2)和另一种颜色 X。
- 颜色 X 的所有像素被替换为黄色(4)。红色(2)完全保持不变，背景(0)保持不变。

```text
for each cell (r,c):
    if input[r,c] == 2: output[r,c] = 2   # red always preserved
    elif input[r,c] == 0: output[r,c] = 0 # background preserved
    elif input[r,c] != 2 and input[r,c] != 0: output[r,c] = 4
    # equivalently: all non-red non-background become yellow(4)
```

- 颜色 X 每次可变(train[0]:蓝 1→4, train[1]:天蓝 8→4, train[2]:绿 3→4, test[0]:栗 9→4)。
- 红色(2)始终被保留且不被修改。

## 2. 关键证据

- train[0]: 17x18 输入，蓝(1)→4(19px)，红(2)0 像素改变。
- train[1]: 15x16 输入，天蓝(8)→4(15px)，红(2)0 改变。
- train[2]: 15x14 输入，绿(3)→4(6px)，红(2)0 改变。
- 所有样例中红色(2)均完全不变。颜色 X 的所有像素(无论位置)全部变为 4。
- arc-gen 含 262 个额外样例全部支持该规则。

## 3. 歧义与风险

> 未发现主要歧义。规则极为明确：第二种非背景色全部映射为黄色(4)，红色(2)保留。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `custom_multi_op`
- `locality`: `varies`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `varies`
- `nonlinearity_needed`: `unknown`
- `memory_priority`: Multi-op custom architecture (72 nodes). Study baseline directly.
- `fusion_hint`: Ops used: And+Cast+Gather+Greater+Less+MaxPool+Mul+Not+Or+Pad+QLinearMatMul+Reshape+Sub+Su...

Baseline 实际架构: And+Cast+Gather+Greater+Less+MaxPool+Mul+Not+Or+Pad+QLinearMatMul+Reshape+Sub+Sum+Transpose+Where (72 nodes, 20 initializers)

## 5. 最终摘要

```yaml
task_id: 077
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: varies
single_linear_conv_possible: no
recommended_architecture: custom_multi_op
memory_priority: Multi-op custom architecture (72 nodes). Study baseline directly.
fusion_hint: Ops used: And+Cast+Gather+Greater+Less+MaxPool+Mul+Not+Or+Pad+QLinearMatMul+Reshape+Sub+Su...
main_risk: high — complex architecture, refer to baseline
confidence: medium
actual_ops: And+Cast+Gather+Greater+Less+MaxPool+Mul+Not+Or+Pad+QLinearMatMul+Reshape+Sub+Sum+Transpose+Where
actual_nodes: 72
```
