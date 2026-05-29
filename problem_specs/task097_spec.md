# Task 097 规范

## 1. 核心规则

- 输入与输出尺寸相同。背景色为 0。
- 输入在各种位置散布大量同色像素（颜色因样例而异：8、6、5、4、3）。输出仅保留有邻接的像素。
- 核心规则：移除所有在 8-连通（包含对角线）意义下没有同色邻居的孤立像素。保留所有至少有一个 8-连通同色邻居的像素。

```text
for each non-zero cell (r,c):
    has_neighbor_8conn = False
    for each neighbor (nr, nc) in 8-directional neighborhood:
        if input[nr,nc] == input[r,c]:
            has_neighbor_8conn = True
    output[r,c] = input[r,c] if has_neighbor_8conn else 0
```

- 4-连通邻居不满足条件，需要对角邻居也算在内。

## 2. 关键证据

- train[0]: color 8，孤立像素如 (2,7),(2,9),(5,8),(6,6) 等被移除（无 8-连通同色邻居）。对角像素对 (0,1)+(1,0) 被保留。
- train[1]: color 6，孤立像素如 (2,14) 等被移除。保持了对角邻接簇如 (1,1) 等。
- train[3]: color 4，较小网格（9x17），孤立像素按 8-连通规则被正确移除/保留。
- 所有被保留的非零像素均在输入中有至少一个 8-连通同色邻居。
- arc-gen 含 262 个样例覆盖多种颜色和密度。

## 3. 歧义与风险

- 歧义点：8-连通 vs 4-连通。当前解释：8-连通（对角算邻居）。风险等级：low（已验证多个对角对保留）。
- 歧义点：是否执行多轮迭代（移除孤立后产生新的孤立）。当前解释：仅一轮，基于原始输入判断。风险等级：low。

## 4. NeuroGolf 架构提示

- recommended_architecture: single_kxk_conv
- locality: 1（3x3 邻域即足够检测 8-连通邻居）
- single_linear_conv_possible: probably
- recommended_kernel: 3x3
- nonlinearity_needed: yes
- 实现：用 3x3 Conv（固定 kernel，所有权重为 1）对每个颜色通道做邻域求和。若 sum >= 2（自身+至少 1 个邻居），则保留。需要非线性（大于等于比较）。

## 5. 最终摘要

```yaml
task_id: 097
primitive_types: [noise_removal, connectivity_filter, morphological_operation]
input_shape_rule: variable size
output_shape_rule: same as input
formal_rule_short: remove pixels without any 8-connected same-color neighbor
locality: 1
single_linear_conv_possible: probably
recommended_architecture: single_kxk_conv
memory_priority: efficient single-pass 3x3 Conv per color channel; avoids iterative processing
fusion_hint: use 3x3 Conv with all-ones kernel on each color channel, then threshold >=2
main_risk: none identified
confidence: high
```
