# Task 032 规范

## 1. 核心规则

- 输入与输出尺寸完全相同（4x4, 5x5, 6x6 等）。
- 背景色为 0。所有非零颜色（1–9）都是"可下落"的粒子。
- 最核心规则：每列独立执行"重力沉降"——该列中所有非零像素按原有顺序下落到列的底部。
  ```text
  for each column c:
      values = [input[r,c] for r from 0..H-1 if input[r,c] != 0]
      output[H-len(values):, c] = values
      output[:H-len(values), c] = 0
  ```
- 同一列中多个非零像素保持原有的纵向相对顺序，紧贴底部堆叠。
- 不同列之间互不影响。

## 2. 关键证据

- Train 0：4x4 输入，第 0 列 [0,0,0,1] → 输出第 0 列 [0,0,0,1]（已在底部）。第 3 列 [9,0,0,0] → [0,0,0,9]。
- Train 1：6x6 输入，多列有多个非零值（如第 2 列含 7 和 7），输出中它们紧贴底部并保持顺序。
- Train 2：5x5 输入，第 0 列含 6 和 0 交替，第 4 列含 2，均正确下沉。
- Test：5x5，分散的非零值全部落入对应列的底部，与规则一致。
- arc-gen 大量样例均支持此规则。

## 3. 歧义与风险

> 未发现主要歧义。

## 4. NeuroGolf 架构提示

- `recommended_architecture`: `object_logic_required`
- `locality`: `global`（每列需要全局累计）
- `single_linear_conv_possible`: `no`
- `recommended_kernel`: `not_single_conv`
- `nonlinearity_needed`: `yes`
- 原因：每列需要计算非零像素数量并重新排列，涉及排序/累计操作，无法用线性卷积表达。需要列级 argwhere + 重排。

## 5. 最终摘要

```yaml
task_id: "032"
primitive_types: [gravity, column_sort]
input_shape_rule: HxW（≤30x30）
output_shape_rule: 同 HxW
formal_rule_short: 每列非零像素下沉到底部
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: 无
confidence: high
```
