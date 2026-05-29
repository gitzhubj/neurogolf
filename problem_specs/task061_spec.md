# Task 061 规范

## 1. 核心规则

- 输入/输出尺寸相同(18x18)。
- 背景色为 0(空洞/缺失),其余颜色生成周期性的乘法表模式。
- 核心规则:用公式 `output[r,c] = ((r * c) + 1) mod M`(结果 0 映射为 M)补全所有 0 单元格,其中 M = 输入中最大非零颜色值。
- 每个训练样例的 M 不同(train[0] M=5, train[1] M=6, train[2] M=7, train[3] M=8, test M=9)。
- 非零像素在输入中已有正确值,仅需填充 0 位置。

```text
M = max(nonzero_color_values)
for each cell (r,c):
    if input[r,c] == 0:
        v = (r * c + 1) % M
        output[r,c] = M if v == 0 else v
    else:
        output[r,c] = input[r,c]
```

- 模式周期为 M,仅依赖于位置(r,c)和 M。

## 2. 关键证据

- 所有样例均为 18x18 输入→18x18 输出。
- 每个样例的 M 等于使用的最大颜色号,且 M 逐步递增(5→6→7→8→9)。
- 输出是一个乘法表模式,周期为 M: rows 0 和 M 全为 1; row 1 为 [1,2,...,M]; row k 为 row 1 乘以 k 再调整到[1..M]。
- 非零输入像素与输出公式完全一致,0 为唯一需要补全的值。
- arc-gen 有 262 个验证样例支持该规则。

## 3. 歧义与风险

- M 的确定方式:取最大颜色值还是最大颜色值+1?当前解释取最大颜色值(非零),对 test M=9 成立。风险:low。
- 公式 `(r*c+1) mod M` 中 0 映射为 M:验证所有样例均一致。风险:low。
- 输入中可能有多种非零颜色,公式只依赖于 M(最大颜色),与具体分布无关。风险:low。

## 4. NeuroGolf 架构提示

- recommended_architecture: object_logic_required
- locality: global(输出依赖(r,c)坐标而非邻域)
- single_linear_conv_possible: no
- recommended_kernel: not_single_conv
- nonlinearity_needed: yes
- 该任务不适合单层 Conv,因为输出公式依赖于坐标(r,c)和全局统计量 M。需先计算 M(ReduceMax),再对每个位置计算模运算。或者将 9 种可能的 M 对应的完整模式作为静态权重存储(9×30×30),通过 M 索引选择后掩膜替换 input 中 0 的位置。后者用更多静态权重换取更少动态中间张量,memory 更优。
- memory_priority: 避免逐元素展开大量中间张量;推荐预先计算所有 M 的模式网格为常量,运行时仅通过 M 索引和掩膜替换。
- fusion_hint: 将 M 计算(全局 max)、模式生成(查表)、0 掩膜替换融合为最少步骤。

## 5. 最终摘要

```yaml
task_id: 061
primitive_types: [periodic_pattern, inpainting, modular_arithmetic, position_dependent]
input_shape_rule: 18x18
output_shape_rule: 18x18
formal_rule_short: output[r,c] = input[r,c] if non-zero else ((r*c+1) mod M) with 0->M, where M = max_color
locality: global
single_linear_conv_possible: no
recommended_architecture: object_logic_required
main_risk: M determination from max color value
confidence: high
```
