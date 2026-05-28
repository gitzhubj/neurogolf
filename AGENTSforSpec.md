# 精简提示词：为 NeuroGolf 生成核心 ARC 变换规范

使用本提示词，让 LLM 从 `input/taskXXX.json` 生成一份**短而可实现**的形式化任务规范。目标是帮助后续设计最小 ONNX 网络，而不是生成完整题解报告。

````text
你是 ARC-AGI 任务分析专家和 NeuroGolf ONNX 实现规划专家。

请分析给定任务 JSON，只输出最核心、最重要的信息：变换规则、关键证据、主要歧义、ONNX 架构提示。

特别注意：NeuroGolf 的目标不是单独最小化参数量，而是最小化 `memory_bytes + params`。很多“参数少”的动态实现会产生大量中间激活张量，最终得分反而更差。因此你的 spec 必须鼓励低内存、少中间张量、算子融合友好的实现，而不是把规则拆成大量 ReduceSum/Mul/Less/Cast/Sum/按块操作。

严格控制长度：最终 Markdown 建议控制在 600-1000 个中文字符；复杂任务最多不超过 1500 个中文字符。不要逐样例展开长篇解释，不要粘贴完整 grid，除非 grid 极小且不可避免。

## 背景约定

- grid 是二维整数数组，颜色为 0..9。
- 坐标使用 0-indexed `(row, col)`，左上角为 `(0,0)`。
- NeuroGolf 输入是 one-hot tensor `(1,10,30,30)`。
- 目标是最小化 `memory_bytes + params`，通常 memory 是主导项。
- 纯逐像素颜色映射优先考虑 `1x1 Conv`。
- 局部邻域规则考虑 `kxk Conv`。
- 可以接受用更多静态权重/常量来换取更少动态中间张量。
- 优先考虑把逻辑压进较少算子，例如 Conv、静态 mask、少量 Reduce、1x1 Conv；避免按位置/按块展开出大量临时张量。
- 如果需要 if-then、AND/OR、乘法、对象选择、连通组件、计数、可变裁剪，通常不是单层线性 Conv 能直接表达。

## 输出位置

如果你能写文件，请保存到：

```text
neurogolf/problem_specs/taskXXX_spec.md
```

不要写入 `thinking/`。`thinking/` 只记录具体解法、实验和优化日志。

如果不能写文件，只输出完整 Markdown，并在开头注明建议保存路径。

## 输入任务 JSON

```json
{{TASK_JSON}}
```

## 必须输出的精简格式

# Task XXX 规范

## 1. 核心规则

用 3-6 条 bullet 描述：

- 输入/输出尺寸关系。
- 背景色和关键颜色。
- 最核心的变换规则。
- 坐标、对象、颜色映射或尺寸公式。
- 如果规则尚不确定，直接写“不确定”。

优先使用形式化表达，例如：

```text
for each cell (r,c):
    output[r,c] = color_map[input[r,c]]
```

或：

```text
crop = bounding_box(non_background_cells)
output = input[crop]
```

## 2. 关键证据

只列 3-5 条最能证明规则的证据。

要求：

- 合并同类样例，不要逐个样例长篇描述。
- 写具体观察，例如尺寸、颜色、bounding box、对象数量、位置关系。
- 如果有 `arc-gen`，只说明它是否支持规则，不展开所有样例。

## 3. 歧义与风险

最多 3 条。

每条写：

- 歧义点。
- 当前采用的解释。
- 风险等级：`low` / `medium` / `high`。

如果没有明显歧义，写：

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

用紧凑 bullet 输出：

- `recommended_architecture`: `single_1x1_conv` / `single_kxk_conv` / `multi_layer_conv_relu` / `object_logic_required` / `unknown`
- `locality`: `0` / `1` / `k` / `global`
- `single_linear_conv_possible`: `yes` / `probably` / `no`
- `recommended_kernel`: `1x1` / `3x3` / `5x5` / `larger` / `not_single_conv`
- `nonlinearity_needed`: `yes` / `no` / `unknown`
- `memory_priority`: 说明如何减少激活/临时张量，而不是只减少 params。
- `fusion_hint`: 说明哪些逻辑应尽量融合进 Conv / mask / 少量 Reduce，哪些动态分解应避免。
- 简短原因，最多 3 句话。

如果是颜色映射任务，给出极简 `weight_fn` 轮廓或颜色映射表。否则不要写完整代码。

架构提示必须体现以下取舍：

- 不要默认选择参数最少的实现。
- 如果“更多静态权重 + 更少动态中间张量”可能更优，应明确推荐这种方向。
- 避免建议生成大量按位置、按块、按对象的 `ReduceSum`、`Mul`、`Less`、`Cast`、`Concat`、`Slice` 中间结果。
- 对每个推荐架构，简短说明它对 memory 的影响。

## 5. 最终摘要

用 YAML 风格给出紧凑摘要：

```yaml
task_id: XXX
primitive_types: [...]
input_shape_rule: ...
output_shape_rule: ...
formal_rule_short: ...
locality: ...
single_linear_conv_possible: ...
recommended_architecture: ...
memory_priority: ...
fusion_hint: ...
main_risk: ...
confidence: high | medium | low
```

## 压缩要求

1. 不输出“执行摘要”“样例统计”“反例假设”“验证计划”等长章节。
2. 不粘贴完整 train/test/arc-gen。
3. 不写泛泛而谈的背景解释。
4. 只保留会影响规则判断、正确性或 `memory_bytes + params` 的信息。
5. 架构建议必须偏向低 profiler memory，而不是偏向最少 params。
6. 复杂任务也要先给最短可用规范；不确定处用风险说明，不要扩写。
````
