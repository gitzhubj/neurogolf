# Task 075 规范

## 1. 核心规则

- 输入/输出尺寸相同(9x13)，背景色为 0。
- 第 3 列(索引 3)固定为灰色(5)分隔线。左侧为 3 列宽(索引 0-2)的源图案区，右侧为 9 列宽(索引 4-12)的粘贴区。
- 源图案是 3x3 的彩色块，位于行 0-2、列 0-2。
- 右侧区域有蓝色(1)标记点，每个标记点指示一个 3x3 粘贴位置。蓝色(1)标记位于目标 3x3 块的中心。
- 变换规则：在每个蓝色(1)标记处，将源图案复制到以该标记为中心的 3x3 区域。蓝色(1)像素本身被源图案对应位置的像素值覆盖。

```text
source = input[0:3, 0:3]   # the 3x3 source pattern
for each (r,c) where input[r,c] == 1:
    # paste a copy of source centered at (r,c)
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            output[r+dr, c+dc] = source[1+dr, 1+dc]
# Gray separator column remains unchanged
# Source region remains unchanged
```

## 2. 关键证据

- 所有样例左侧 3x3 源图案各不相同: train[0]=422/262/644, train[1]=273/233/377, train[2]=386/982/999。
- 右侧蓝色(1)标记位置直接对应输出中 3x3 拷贝的中心。train[0] 标记在(1,5),(4,8),(7,8)→输出中三个 3x3 拷贝。
- train[2] 有两个并列拷贝(列 4-6 和列 10-12)，分别对应(1,5)和(1,11)两个蓝点。
- 灰色(5)分隔列的像素值始终不变。
- arc-gen 含 261 个额外样例，全部符合模式复制规则。

## 3. 歧义与风险

- 蓝色标记是否一定位于目标 3x3 块的正中心？所有样例均如此。风险: `low`。
- 如果两个蓝色标记距离过近导致 3x3 块重叠会怎样？未在样例中出现。风险: `low`。

## 4. NeuroGolf 架构提示

- recommended_architecture: multi_layer_conv_relu
- locality: 1 (感知 3x3 块)
- single_linear_conv_possible: no
- recommended_kernel: 3x3
- nonlinearity_needed: yes
- 关键是检测蓝色(1)标记位置，然后在每个标记处执行 3x3 复制。
- 可用 3x3 Conv 检测蓝色标记(核权重使 conv 响应中心为蓝色的模式)，再用 mask 操作将源图案复制到标记位置。
- 另一种方式: 如果源图案固定，可用静态权重将 3x3 图案编码到 Conv 核中。框架：一个 3x3 Conv(检测蓝色)+一个像素级 mask 复制。

## 5. 最终摘要

```yaml
task_id: 075
primitive_types: [pattern_copy, template_pasting, marker_based_replication]
input_shape_rule: 9x13
output_shape_rule: 9x13
formal_rule_short: Copy 3x3 source pattern to each blue(1) marker location in right-side area
locality: 1
single_linear_conv_possible: no
recommended_architecture: multi_layer_conv_relu
memory_priority: Use Conv to detect markers and static kernel to encode source pattern; avoid dynamic slicing
fusion_hint: Combine marker detection and pattern pasting into a single Conv+mask operation
main_risk: none
confidence: high
```
