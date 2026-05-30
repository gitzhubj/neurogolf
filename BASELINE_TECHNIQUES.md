# NeuroGolf Baseline 技巧总结

从他人高分 baseline 的 400 个 ONNX 文件中反向工程出的完整架构模式和优化技巧。

---

## 一、全局统计

| 指标 | 数值 |
|---|---|
| 总任务数 | 400 |
| 总 ONNX 大小 | ~14.2 MB |
| 平均文件大小 | ~37 KB |
| 最小 | 158 B (task016) |
| 最大 | 1.29 MB (task209) |
| 算子种类 | 30+ |
| 最常用算子 | Slice(290), Pad(275), Mul(267), Sub(266), Cast(249), ReduceSum(243), Greater(213), Concat(195), Where(195) |

### 复杂度分布

| 级别 | 大小范围 | 数量 | 典型架构 |
|---|---|---|---|
| tiny | < 500B | 18 | 单 Gather / Transpose |
| small | 500B-2KB | 54 | Slice+Pad / 简单 Reduce |
| medium | 2KB-10KB | 213 | Conv+logic / Reduce+Where |
| large | 10KB-100KB | 96 | 多层 Conv 展开 |
| huge | 100KB-500KB | 9 | 大规模空间展开 |
| oversized | > 500KB | 10 | 极端尺寸对象追踪 |

---

## 二、核心架构模式

### 模式 I: Gather 查表（替换 1×1 Conv）

**原理**：ONNX 的 Gather 算子可以沿 channel 轴做索引重排，一次操作完成所有颜色映射。

```
Gather(axis=1, indices=[new_ch_order])
input:  (1, 10, H, W)
output: (1, 10, H, W)  — 通道按 indices 重排
```

**task016 实例** — 4对颜色互换（1↔5, 2↔6, 3↔4, 8↔9）：
```python
indices = [0, 5, 6, 4, 3, 1, 2, 7, 9, 8]
# 含义: 输出ch0 ← 输入ch0 (背景保持)
#       输出ch1 ← 输入ch5 (原色5 → 新色1位)
#       输出ch2 ← 输入ch6 (原色6 → 新色2位)
#       输出ch3 ← 输入ch4
#       输出ch4 ← 输入ch3
#       输出ch5 ← 输入ch1
#       输出ch6 ← 输入ch2
#       输出ch7 ← 输入ch7 (不变)
#       输出ch8 ← 输入ch9
#       输出ch9 ← 输入ch8
```
- **参数量**: 10（仅 index 数组）
- **vs 1×1 Conv**: 10 params vs 100 params（10x savings）
- **ONNX 节点数**: 1
- **适用条件**: 变换是纯逐像素颜色映射，且是排列（permutation）而非线性组合

**构建代码模板**：
```python
import numpy as np
import onnx
from onnx import helper

_CH, _H, _W = 10, 30, 30
_GS = [1, _CH, _H, _W]
_DT = onnx.TensorProto.FLOAT

def build_gather_lookup(channel_order: list[int]) -> onnx.ModelProto:
    indices = helper.make_tensor(
        name="idx",
        data_type=onnx.TensorProto.INT64,
        dims=[len(channel_order)],
        vals=channel_order,
    )
    node = helper.make_node("Gather", ["input", "idx"], ["output"], axis=1)
    
    x = helper.make_tensor_value_info("input", _DT, _GS)
    y = helper.make_tensor_value_info("output", _DT, _GS)
    graph = helper.make_graph([node], "g", [x], [y], [indices])
    return helper.make_model(graph, ir_version=8,
                             opset_imports=[helper.make_opsetid("", 13)])
```
**opset 注意**：Gather 的 axis 属性在 opset 11+ 才支持。baseline 使用了 opset 10-13。

**使用此模式的任务（99个）**：task016, task053, task116 等。

---

### 模式 J: Gather 空间变换（替换 3×3 Conv 移位）

**原理**：Gather 沿空间轴（axis=2 行 / axis=3 列）做索引重排，实现平移、翻转、循环移位。

```
Gather(axis=2, indices=[row_order])   # 行重排
Gather(axis=3, indices=[col_order])   # 列重排
```

**task053 实例** — 整体下移一行（3×3 网格在 30×30 画布中）：
```python
indices = [2, 0, 1, 29, 29, 29, 29, 29, 29, 29, 29, 29,
           29, 29, 29, 29, 29, 29, 29, 29, 29, 29, 29,
           29, 29, 29, 29, 29, 29, 29]
# 含义: output_row_0 ← input_row_2 (下移：最底行到顶)
#       output_row_1 ← input_row_0
#       output_row_2 ← input_row_1
#       output_row_3..29 ← input_row_29 (padding/背景区)
```

**task116 实例** — 行列同时变换：
```python
indices = [2, 1, 0, 0, 1, 2, 3, 3, ...]  # 30个元素
# 前6个索引处理3x3网格的行重排+反射
```

- **参数量**: 30（index 数组）
- **vs 3×3 Conv**: 30 params vs 900 params（30x savings）
- **局限**: 只能做置换（permutation），不能做加权组合

**构建代码模板**：
```python
def build_gather_spatial(row_indices: list[int], col_indices: list[int] = None):
    nodes, inits = [], []
    
    # 行重排
    row_idx = helper.make_tensor("row_idx", onnx.TensorProto.INT64,
                                  [len(row_indices)], row_indices)
    inits.append(row_idx)
    nodes.append(helper.make_node("Gather", ["input", "row_idx"], ["row_perm"], axis=2))
    
    # 列重排（可选）
    if col_indices:
        col_idx = helper.make_tensor("col_idx", onnx.TensorProto.INT64,
                                      [len(col_indices)], col_indices)
        inits.append(col_idx)
        nodes.append(helper.make_node("Gather", ["row_perm", "col_idx"], ["output"], axis=3))
    else:
        nodes[-1].output[0] = "output"
    
    # ... 构建 graph
```

---

### 模式 K: Transpose 空间交换

**原理**：用 Transpose 交换 H 和 W 维度，0 参数。

```
Transpose(perm=[0, 1, 3, 2])
input:  (1, 10, H, W)
output: (1, 10, W, H)  — 空间维度交换（等价于 90° 旋转+镜像）
```

**task179/241 实例** — 矩阵转置：
```python
# perm=[0,1,3,2] = [batch, channel, width, height]
# 输入 shape (1,10,3,3) → 输出 shape (1,10,3,3)
# 效果: output[c][r][c'] = input[c][c'][r]
```

- **参数量**: 0
- **ONNX 节点数**: 1
- **适用**: 90° 旋转、镜像翻转、对角线对称

**⏡ 重要**：Transpose 前后 shape 相同（3×3 → 3×3），仅像素位置变化。对于方形网格，这是最节省的变换。

---

### 模式 L: Slice + Pad 裁剪/翻转/重定位

**原理**：Slice 提取子区域（可带 step 实现翻转），Pad 补回 30×30。

```
Slice(axes=[2,3], starts=[r0,c0], ends=[r1,c1], steps=[sr,sc])
  → Pad(pads=[0,0,0,0, top, bottom, left, right])
```

#### 子模式 L1: 裁剪+重定位
**task135** — 从 9×9 输入中裁出右下角 3×3（cols 6-8, rows 0-2）：
```python
Slice(starts=[0, 6], ends=[3, 9], axes=[2, 3])  # 裁 3×3
  → Pad(pads=[0,0,0,0, 0,0, 0,27])  # 补到 30×30
```
- 参数量: 6（starts + ends）
- 节点数: 2

#### 子模式 L2: 水平翻转
**task087** — 左右镜像：
```python
Slice(starts=[2,2], ends=[-inf,-inf], axes=[2,3], steps=[-1,-1])  # 反向读取
  → Pad(...)  # 补到 30×30
```
- 参数量: 4（starts + ends + output_pads）
- 节点数: 2
- **step=-1 实现翻转**，0 额外参数

#### 子模式 L3: 提取左上角
**task326** — 从 6×6 输入中裁左上 2×2：
```python
Slice(starts=[0, 0], ends=[2, 2], axes=[2, 3])
  → Pad(pads=[0,0,0,0, 0,0, 28,28])
```

**构建模板**：
```python
def build_crop_and_pad(crop_start, crop_end, axes=[2,3]):
    starts = helper.make_tensor("s", onnx.TensorProto.INT64, [2], crop_start)
    ends = helper.make_tensor("e", onnx.TensorProto.INT64, [2], crop_end)
    ax = helper.make_tensor("a", onnx.TensorProto.INT64, [2], axes)
    steps = helper.make_tensor("st", onnx.TensorProto.INT64, [2], [1, 1])
    
    nodes = [
        helper.make_node("Slice", ["input", "s", "e", "a", "st"], ["cropped"]),
        helper.make_node("Pad", ["cropped", "pads"], ["output"],
                        mode="constant", value=0.0),
    ]
    # pads: [0,0,0,0, pad_top, pad_bottom, pad_left, pad_right]
    # ...
```

---

### 模式 M: Reduce + Where 条件逻辑

**原理**：用 ReduceSum/ReduceMax 沿空间维度统计，用 Greater/Equal/Less 做阈值判定，用 Where 做条件分支，Mul/Sub 做通道选择。

#### 子模式 M1: 行统计+阈值（task052）
**规则**：如果一行的 3 个像素同色 → 该行输出颜色 5，否则 0。

```
Slice(3×3) → ReduceSum(axis=W) → ReduceMax(axis=CH) → Equal(3.0)
  → Where → channel select (ch5 vs ch0) → Pad(30×30)
```

关键张量：
- `ones_w [1,1,1,3]` — 行内广播掩码
- `ch5_vec [1,10,1,1]` — channel 5 选择器
- `ch0_vec [1,10,1,1]` — channel 0（背景）选择器
- `threshold = 3.0` — 阈值

伪代码：
```python
content = input[0:3, 0:3]                      # Slice
row_sums = sum(content, axis=W)                  # ReduceSum → [1,10,3,1]
max_per_row = max(row_sums, axis=CH)             # ReduceMax → [1,1,3,1]
is_uniform = (max_per_row == 3.0)                # Equal → bool
uniform_mask = where(is_uniform, ones_w, 0)      # Where → [1,1,3,3]
output_ch5 = ch5_vec * uniform_mask              # Mul → color 5 for uniform rows
output_ch0 = ch0_vec * (1 - uniform_mask)        # Mul → color 0 for other
output = output_ch5 + output_ch0                 # Sum → final
output = pad(output, to 30×30)                   # Pad
```

- 参数量: ~43
- 节点数: 10
- 核心技巧: **ReduceSum + ReduceMax 双重归约找到行最大值**

#### 子模式 M2: 列占用计数+阈值（task067）
**规则**：从 3×9 输入中提取周期为 3 的重复模式。

```
ReduceMax(axis=[1,2]) → Conv(1×30, cumsum) → ReduceSum → Div(total/3) → Greater → Where
```

- 参数量: ~33
- 核心技巧: **Conv 用于 cumsum（累积和）**，kernel=[1,1,...,1]

#### 子模式 M3: XOR 逻辑（task072）
**规则**：输入分左右两半，XOR 后输出。

```
Slice(left) → Sub(1 - left) → Sub(1 - right) → Abs → 通道组装 → Pad
```

- 核心技巧: **用 Sub+Abs 实现 XOR**（|(1-L) - (1-R)| = |R - L| = XOR 当值∈{0,1}）

---

### 模式 N: Conv + 逻辑门（多层）

当单层 Conv 不够时，baseline 使用 Conv 配合 Reduce/Where/逻辑运算。

**典型架构 A** — AND 检测（task006 等）：
```
Conv(3×3, 计数邻域) → Mul(mask) → ReduceMax → threshold → channel mapping → Pad
```

**典型架构 B** — 对象路径追踪（task025）：
```
大量 Slice(channel-wise) → 逐通道 Greater → Or → 逐像素 ReduceSum → 
  逐区域 Sub → Cast → 逐位置 Where → OneHot → ArgMax → Pad
```
- 文件大小: 827KB
- 参数量: ~65K
- 这类任务极其复杂，baseline 选择了**空间展开**策略（对每个可能的位置/通道做独立处理）

---

### 模式 O: Slice + Concat + 多通道组装（task072 等）

```
Slice(ch0, left_half)  → Sub(1-L) → Sub(1-R) → Abs → 
Slice(ch0, right_half) → Sub(1-R) → ... →
Concat(ch0_out, zero_ch1, zero_ch2, xor_result, zero_ch4, ...) → Pad
```

- 核心技巧: **逐通道独立处理，最后 Concat 合并**
- 只处理实际使用的通道，未使用的通道用 zero constant 填充

---

## 三、关键优化技巧对比

### 我们之前的方式 vs baseline 的正确方式

| 任务类型 | 我们的方式 | baseline 方式 | 节省 |
|---|---|---|---|
| 纯颜色映射 | 1×1 Conv (100p) | Gather axis=1 (10p) | **10x params** |
| 空间平移 | 3×3 Conv (900p) + Add + Mul | Gather axis=2/3 (30p) | **30x params** |
| 旋转/镜像 | 3×3 Conv (900p) | Transpose (0p) | **infinite** |
| 裁剪 | Conv + mask | Slice + Pad (6p) | **150x params** |
| 翻转 | Conv + Reverse | Slice step=-1 + Pad (4p) | **225x params** |
| 行/列统计 | 多层 Conv + ReLU | ReduceSum + ReduceMax + Where | **10x simpler** |
| XOR 逻辑 | Conv + ReLU + Conv | Sub + Abs | **更简洁准确** |

### 核心教训

1. **不要默认用 Conv**。先思考：变换是排列吗？→ Gather。是纯空间位移吗？→ Slice/Pad。是旋转/镜像吗？→ Transpose。
2. **Gather 是 1×1 Conv 的超集**（对于排列变换）。1×1 Conv 可以实现任意线性组合，但排列场景不需要线性组合——只需索引重排。
3. **Slice step=-1 免费实现翻转**。不需要任何额外参数。
4. **Reduce + Where 实现条件逻辑**。比 Conv+ReLU 更直接、更易调试。
5. **单通道独立处理 + Concat 合成**。对多通道复杂逻辑，逐通道 Slice→处理→Concat 比全通道 Conv 更可控。
6. **Pad 的 constant mode**。所有 spatial 操作后统一用 Pad 恢复到 30×30，不需要在中间步骤处理尺寸。

---

## 四、算子速查表

| 算子 | 用途 | 关键参数 | 适用场景 |
|---|---|---|---|
| **Gather** | 索引重排 | axis, indices | 颜色映射、空间置换 |
| **Transpose** | 维度交换 | perm | 旋转、镜像 |
| **Slice** | 裁剪/提取 | starts, ends, axes, steps | 子区域提取、翻转(step=-1) |
| **Pad** | 填充至目标尺寸 | pads, mode=constant | 统一恢复 30×30 |
| **ReduceSum** | 沿轴求和 | axes, keepdims | 行/列统计、颜色计数 |
| **ReduceMax** | 沿轴取最大值 | axes, keepdims | 存在性检测、非零检测 |
| **Greater/Less/Equal** | 逐元素比较 | — | 阈值判定、二值化 |
| **Where** | 条件选择 | — | if-then-else 分支 |
| **Mul** | 逐元素乘法 | — | 掩码、广播、通道选择 |
| **Sub** | 逐元素减法 | — | XOR(配合Abs)、差分 |
| **Abs** | 绝对值 | — | XOR 实现 |
| **And/Or** | 逻辑运算 | — | 多条件组合 |
| **Conv** | 空间卷积 | kernel_shape, pads | 邻域特征提取（仅在必要时使用） |
| **Concat** | 张量拼接 | axis | 多通道组装 |
| **Cast** | 类型转换 | to | bool→float 转换 |
| **ArgMax** | 最大值的索引 | axis, keepdims | one-hot 解码 |
| **OneHot** | 索引→one-hot | depth | 颜色编码 |

---

## 五、从 baseline 学到的设计原则

### 原则 1: 最小算子原则
每个问题只用能解决它的最小算子集。能用一个 Gather 就不用 Conv+ReLU+Conv。

### 原则 2: 排列优于组合
如果变换是置换（1→5, 5→1），Gather 直接做索引映射。1×1 Conv 也可以用（设权重为 1.0），但多出 90 个零参数，白占 ONNX 序列化空间。

### 原则 3: 常量编码静态信息
位置掩码、阈值、通道选择器都编码为 Constant 张量，用 Mul/Add/Where 在运行时注入——不需要"学习"或 Conv 隐式编码。

### 原则 4: 逐通道解耦
对多通道复杂逻辑，先按通道 Slice 分开 → 独立处理 → Concat 合并。比全通道联合处理更简单可控。

### 原则 5: Pad 是最后一步
所有 spatial 操作（Slice、Gather spatial、Conv）都在实际网格尺寸上做，最后统一用 Pad 扩展到 30×30。不要在中间步骤维持 30×30 全尺寸。

### 原则 6: opset 版本灵活选择
baseline 使用了 opset 10-13。某些算子（如 Gather axis）在较高 opset 才支持。实际提交时比赛允许的 opset 范围决定你能否用某个算子。
