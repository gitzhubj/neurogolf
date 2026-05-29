# Task 099 规范

## 1. 核心规则

- 输入与输出尺寸相同（可变，10x10）。背景色为 0。
- 输入包含颜色 1（蓝色）构成的"容器"形状，以及一个位于容器内部的"种子"像素（颜色为 2、3、6、8 等）。
- 核心规则：从种子像素出发，在容器内部执行泛洪填充（flood fill）——将容器内所有被 1 包围且可达的区域填充为种子颜色，同时容器边框和外部保持不变。

```text
for each container outlined by color 1:
    find the seed pixel (non-0, non-1) inside the container
    flood-fill from seed, expanding in 4 directions
    stop when hitting color-1 border or grid boundary
    replace all filled cells with seed color
    color-1 border pixels remain unchanged
```

- 若有多个容器，每个容器独立填充（使用各自的种子颜色）。填充完成后种子像素本身保留为种子颜色。

## 2. 关键证据

- train[0]: 一个 1-容器（rows 1-5, cols 1-5），种子 2 位于 (3,3)。输出中将容器内所有非 1 区域填为 2（"T"形填充）。
- train[1]: 两个容器：左侧种子 2 填为 2-色区域，右侧种子 3 填为 3-色区域。互不干扰。
- train[2]: 种子 6 和种子 8 分别填充各自容器。
- test[0]: 种子 4 和种子 7 分别填充各自容器。
- 容器形状并非严格矩形，但始终由颜色 1 勾勒出完整封闭边界。种子颜色在容器内部仅出现一次。

## 3. 歧义与风险

- 歧义点：容器形状是否必须为单连通（无孔）。当前解释：容器为闭合区域，种子在其中，泛洪填充可达所有内部。风险等级：low。
- 歧义点：多个容器共享边框时的处理。当前解释：容器间由颜色 1 分隔，各自独立填充。风险等级：low。
- 歧义点：若容器内有多个种子像素。当前解释：所有样例仅 1 个种子/容器。风险等级：medium。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global（泛洪填充需要递归/迭代传播）
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 泛洪填充在 ONNX 中很难直接表达。可考虑用迭代形态学膨胀（从种子开始，每次膨胀 1 步，受限掩膜为容器内部）来近似。在颜色 1 边界处停止。

## 5. 最终摘要

```yaml
task_id: 099
primitive_types: [flood_fill, container_detection, seed_expansion]
input_shape_rule: variable, 10x10
output_shape_rule: same as input
formal_rule_short: flood-fill from seed color within color-1 container boundary
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
memory_priority: iterative dilation with mask constraint can approximate flood fill; each iteration creates a temporary tensor, so limit iterations
fusion_hint: use a fixed number of dilation steps (max container size) with AND masking against the container region
main_risk: flood fill is inherently iterative; exact ONNX implementation may require many steps
confidence: high
```
