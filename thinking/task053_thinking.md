# Task 053 思考日志

## Round 1 — Conv + Constant + Add + Mul 方案

### 任务分析
- 输入/输出均为3x3，固定尺寸。
- 变换规则：所有非零图案向下平移1行。row 0空出为背景（0），row 2移出。
- 在30x30画布上，3x3网格位于左上角 (0,0)-(2,2)。

### 网络设计
**架构**: 3x3 Conv (shift) + Constant (bg restore) + Add + Constant (mask) + Mul

- **Conv**: W[ch, ch, (-1, 0)] = 1.0，将所有通道下移1行
- **bg_fix**: channel 0 的 row 0, cols 0-2 = 1.0（恢复被移空的首行背景）
- **mask**: row 3, cols 0-2 = 0.0（消除移出网格边界的溢出）

关键发现：单层Conv无法保持one-hot编码（边缘处padding产生全零而非背景）。Add+Mul的常量组合可以修复边缘效应。

### 基线快照
- 架构: Conv → Add(bg) → Mul(mask)
- 参数量: 900 (10×10×3×3)
- 内存: 144000 bytes
- Cost: 144000 + 18900 = 162900 (? units)
- 得分: 12.999 points
- 通过: ARC-AGI 6/6, ARC-GEN 54/54

### 结论
Add+Mul+Constant模式是修复Conv空间变换边缘效应的有效方法，可用于其他平移/裁剪类任务。
标记 DONE。
