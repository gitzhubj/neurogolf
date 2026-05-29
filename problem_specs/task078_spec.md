# Task 078 规范

## 1. 核心规则

- 输入/输出尺寸相同(10x10)，仅使用颜色 0(背景)、1(蓝)、2(红)。
- 蓝色(1)构成一个连通的不规则多边形。红色(2)位于蓝色多边形外部的某些位置。
- 红色(2)像素"流入"蓝色多边形的凹入/空洞区域，原红色(2)位置变为背景(0)。交换数量严格相等(0→2 的计数 = 2→0 的计数)。
- 等价描述：蓝色(1)像素保持不变。找出蓝色多边形内部的"空洞"(被蓝包围的 0 像素)，用红色填充。同时，所有原红色(2)像素变为 0。

```text
# Step 1: Identify the blue(1) region shape
# Step 2: Find all background(0) pixels that are "inside" or "concave pockets" of the blue region
# Step 3: Fill those 0s with red(2)
# Step 4: Set all original red(2) pixels to 0
```

- 结果：红色像素的总数不变，但位置从外部迁移到蓝色形状的凹陷/空洞中。

## 2. 关键证据

- train[0]: 蓝(1)形状有垂直凹槽在列 4。输入红(2)在行 7-9 列 4。输出凹槽填红(2)，原红变 0。0→2(3px)=2→0(3px)。
- train[1]: 蓝形状更复杂。输入红在底部区域，输出红填充到蓝形状的多个凹陷处。0→2(5px)=2→0(5px)。
- train[2]: 蓝形状有多个凹槽(列 3,4,6,8)。输入红在底部两列，输出填充这些凹陷。0→2(11px)=2→0(11px)。
- 所有样例 0→2 计数严格等于 2→0 计数，不是简单删减而是位置置换。

## 3. 歧义与风险

- "内部"的判断标准？当前看是蓝色(1)形状的 4-邻域凹槽。风险: `medium`。
- 蓝色形状边界是否参与判断？蓝色(1)本身不变，只影响 0→2 的位置选择。风险: `low`。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global (需感知蓝色多边形形状)
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 需要识别蓝色多边形的内部空洞/凹槽。这类似于"flood fill"操作：从蓝色形状的外部区域开始填充，无法到达的 0 像素即为"内部"空洞。
- 可考虑：用多层卷积逐步"收缩"蓝色边界，检测被完全包围的 0 区域。
- 内存注意: 避免对整个 10x10 进行逐像素 flood fill 展开。可用形态学操作(腐蚀/膨胀)的 Conv 变体来近似。

## 5. 最终摘要

```yaml
task_id: 078
primitive_types: [flood_fill, concave_filling, shape_aware_recoloring]
input_shape_rule: 10x10
output_shape_rule: 10x10
formal_rule_short: Red(2) pixels fill concavities/holes inside blue(1) shape; original red becomes background; total red count preserved
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
memory_priority: Use morphological Conv operations rather than explicit flood fill
fusion_hint: Use Conv-based region growing to detect interior cavities, then mask-based color swap
main_risk: Definition of "interior" may vary; 4- vs 8-connectivity not explicitly verified
confidence: medium
```
