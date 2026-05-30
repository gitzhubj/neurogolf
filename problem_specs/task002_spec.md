# Task 002 规范

## 1. 核心规则

- 输入固定 6x3，输出固定 9x3（高度从 6 扩展到 9，宽度不变）。
- 背景色为 0。输入颜色仅 0 和 1，输出颜色仅 0 和 2（1 被重映射为 2）。
- 核心变换分两步：(a) 像素级颜色映射 1 -> 2；(b) 按输入 6 行的最短垂直周期 p 外推至 9 行。
- 最短周期 p = min { k | 对所有 0 <= i < 6-k, 输入行 i == 输入行 i+k }。可见数据中 p 仅取 2、3、4。
- 输出第 r 行（0 <= r < 9）取自输入第 (r mod p) 行，并执行颜色映射：0 -> 0，1 -> 2。

```text
p = smallest k where row[i] == row[i+k] for all valid i
for r in 0..8:
    src_row = input[r % p]
    output[r] = [2 if x == 1 else 0 for x in src_row]
```

## 2. 关键证据

- train 0：输入行模式不满足 period 2 或 3（第 0 行 [0,1,0] != 第 2 行 [0,1,0]？不，train0 的行 0,2,4 都是 [0,1,0]，但行 1=[1,1,0] != 行 3=[0,1,1]），最短 period 为 4。输出后 3 行为 I[2], I[3], I[0] 颜色映射后。
- train 1：输入交替 [0,1,0]/[1,0,1]，period 2。输出后 3 行 = I[0],I[1],I[0] 映射后，而非 I[2],I[3],I[4]。
- train 2：输入 period 3（行 0,1,2 在行 3,4,5 重复）。输出后 3 行 = I[0],I[1],I[2] 映射后。
- test：输入行 0-2 与行 3-5 相同（period 3），输出后 3 行为 I[0],I[1],I[2] 映射，支持 period 3 分支。
- arc-gen 覆盖 period 2（21 例）、period 3（227 例）、period 4（17 例），排除"始终追加前 3 行"的过拟合解释。

## 3. 歧义与风险

- 歧义点：若 p=6（6 行无短周期），外推行如何确定。当前解释：按 p=6 外推（即重复整个 6 行 pattern），但可见样例无此情况。风险等级：medium。
- 歧义点：输入若出现 1 之外的前景色，颜色映射如何处理。当前解释：未定义，可见数据仅含 0 和 1。风险等级：medium。

## 4. NeuroGolf 架构提示

> **以下内容已根据 baseline ONNX 验证方案修正**

- `recommended_architecture`: `conv_with_logic`
- `locality`: `k`
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `3x3`
- `nonlinearity_needed`: `no`
- `memory_priority`: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
- `fusion_hint`: Baseline uses 95 nodes: And+Cast+Concat+Conv+Greater+Mul+Pad+ReduceSum+Slice+Sub+Sum. Study baseline for optimal op sequence.

Baseline 实际架构: And+Cast+Concat+Conv+Greater+Mul+Pad+ReduceSum+Slice+Sub+Sum+Where (95 nodes, 32 initializers)

## 5. 最终摘要

```yaml
task_id: 002
primitive_types: [verified_by_baseline]
input_shape_rule: derived_from_baseline
output_shape_rule: derived_from_baseline
formal_rule_short: verified_by_baseline_ONNX
locality: k
single_linear_conv_possible: no
recommended_architecture: conv_with_logic
memory_priority: Conv + supporting ops (Reduce/Where/Mul). Use minimal intermediate tensors.
fusion_hint: Baseline uses 95 nodes: And+Cast+Concat+Conv+Greater+Mul+Pad+ReduceSum+Slice+Sub+Sum. Study baseline for optimal op sequence.
main_risk: medium — multi-op, check baseline for correct sequence
confidence: high
actual_ops: And+Cast+Concat+Conv+Greater+Mul+Pad+ReduceSum+Slice+Sub+Sum+Where
actual_nodes: 95
```
