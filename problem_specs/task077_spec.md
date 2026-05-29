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

- recommended_architecture: single_1x1_conv
- locality: 0
- single_linear_conv_possible: yes
- recommended_kernel: 1x1
- nonlinearity_needed: no
- 这是典型的逐像素颜色重映射。1x1 Conv(in=10, out=10)即可实现：
  - 红(2)→2, 黄(4)→4, 所有其他非零色→4, 0→0
  - 具体: W[4, X] = 1.0(将所有非红非背景色映射到 4), W[2,2] = 1.0, W[0,0] = 1.0
- 由于颜色 X 因样例而异，需要确定哪个颜色应被替换。但这在 1x1 Conv 中只需调整对应输入 channel 到输出 channel 4 的权重。

## 5. 最终摘要

```yaml
task_id: 077
primitive_types: [color_replacement, selective_recoloring, red_preservation]
input_shape_rule: variable (14x14 to 17x18)
output_shape_rule: same as input
formal_rule_short: All non-red, non-background pixels become yellow(4); red(2) and background(0) unchanged
locality: 0
single_linear_conv_possible: yes
recommended_architecture: single_1x1_conv
memory_priority: Minimal - single 1x1 Conv, no intermediate tensors
fusion_hint: Single 1x1 Conv maps all non-red non-zero channels to output channel 4
main_risk: none
confidence: high
```
