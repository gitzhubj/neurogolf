# Task 003 规范

## 1. 核心规则

- 输入输出同尺寸。输入尺寸可变（观测 8..16 行，8..16 列）。
- 背景色为 0。每种非零颜色 k（1..9）在输出中保持原色不变，无重染色。
- 核心变换：将每个同色 8-连通非零对象执行"右剪切"——对象最底行保持原位，其余行向右平移 1 格，移动后若超出对象自身右边界则被夹回右边界。
- 连通性按 8-邻接（含对角线）判断；每个颜色独立分割对象。

```text
for each same-color 8-connected object C with color k:
    bottom = max row in C
    right = max col in C
    for each pixel (r,c) in C:
        if r == bottom:
            target = (r, c)      # 底行保持不动
        else:
            target = (r, min(c+1, right))  # 右移 1，但不超出对象右界
        output[target] = k
```

## 2. 关键证据

- train 0（14x9）：颜色 6 对象 bbox 行 1..5、列 1..6。顶行列 1..3 变为 2..4；第 4 行列 3 变为列 4，但列 6 已在右边界保持不动；最底行（行 5）完全保持不变。颜色 2 对象同理独立移动。
- train 1（8x9）：颜色 8 对角臂对象底行为行 5，非底行右移但行 4 的右端列 8 被夹住不越界。
- train 2（11x10）：多对象场景，每对象按自身 bbox 独立右剪切，非按全图统一右边界。
- arc-gen 涵盖多种对象形状和颜色，均支持同色 8-连通独立右剪切规则。

## 3. 歧义与风险

- 歧义点：连通性使用 4-邻接还是 8-邻接。当前解释：8-邻接（含对角线），因斜向相邻段在 4-邻接下会被拆成两个对象，导致错误结果。风险等级：low。
- 歧义点：两个对象右剪切后若目标坐标冲突，如何裁决。当前解释：可见样例无冲突，覆盖规则未定义。风险等级：medium。
- 歧义点：底行保持是指整行像素还是仅水平底边。当前解释：整行（因可见对象底行均为水平连续段，二者等价）。风险等级：medium。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `reduce_with_where`
- `locality`: `global`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_needed`
- `nonlinearity_needed`: `no`
- `memory_priority`: Reduce + threshold + conditional. No Conv needed.
- `fusion_hint`: Baseline uses 39 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.

Baseline 实际架构: Cast+Concat+Less+Mul+Pad+ReduceSum+Slice+Sub+Sum+Where (39 nodes, 10 initializers)

## 5. 最终摘要

```yaml
task_id: 003
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: global
single_linear_conv_possible: no
recommended_architecture: reduce_with_where
memory_priority: Reduce + threshold + conditional. No Conv needed.
fusion_hint: Baseline uses 39 nodes. Key: ReduceSum/ReduceMax + Greater/Equal + Where.
main_risk: medium — check baseline for exact op sequence
confidence: high
actual_ops: Cast+Concat+Less+Mul+Pad+ReduceSum+Slice+Sub+Sum+Where
actual_nodes: 39
```
