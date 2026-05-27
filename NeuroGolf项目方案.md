# NeuroGolf — ARC-AGI ONNX 神经网络压缩比赛方案

## 一、比赛概述

**目标**：为 ARC-AGI v1 公开训练集的每个任务（~400个），构建能正确复现变换的 **ONNX 神经网络**，并最小化其 **参数量 + 内存占用**。

**与 Code Golf 项目的关系**：

| | Code Golf | NeuroGolf |
|---|---|---|
| 最小化目标 | Python 源码字节数 | ONNX 参数量 + 内存字节数 |
| 表达形式 | `p=lambda g:...` | .onnx 神经网络文件 |
| 测试数据 | 同一批 ARC-AGI JSON | 同左 + ARC-GEN-100K + 私有集 |
| 核心约束 | 仅标准库、独立文件 | 静态形状、算子白名单、≤1.44MB |

**评分公式**：
```
cost  = 总参数量 + 总内存占用量(字节)
score = max(1, 25 - ln(cost))
```

**硬约束**：
- 所有张量形状必须静态定义
- 禁止算子：`Loop`、`Scan`、`NonZero`、`Unique`、`Script`、`Function`
- 每个 .onnx ≤ 1.44MB
- 必须通过：原始 ARC-AGI + ARC-GEN-100K + 私有测试集（防过拟合）

---

## 二、核心工作流：基线→思考→优化 闭环

这是从 Code Golf 项目继承的核心理念。**不是一次性完成，而是每任务多轮迭代**。

```
┌──────────────────────────────────────────────────────────┐
│                    每任务的迭代闭环                        │
│                                                          │
│  Step 1: 构建基线网络                                      │
│  (手工权重 或 训练，得到一个能通过全部测试的可行网络)         │
│         │                                                │
│         ▼                                                │
│  Step 2: 生成 thinking/task{id}_thinking.md              │
│  (记录基线架构、cost、关键观察、变换规律分析)                │
│         │                                                │
│         ▼                                                │
│  Step 3: 基于思考日志进行优化                               │
│  (尝试更小的架构、手工精炼权重、量化、剪枝)                   │
│         │                                                │
│         ▼                                                │
│  Step 4: 测试 & 对比                                       │
│  (若 cost 下降 → 更新基线 + 追加思考日志)                   │
│  (若 cost 不变 → 记录失败原因，换方向)                       │
│         │                                                │
│         ▼                                                │
│  重复 Step 3-4，直到无法进一步压缩                          │
│         │                                                │
│         ▼                                                │
│  输出: output/task{id}_cost{}.onnx                        │
└──────────────────────────────────────────────────────────┘
```

### 2.1 Step 1：构建基线（首次求解）

对每个任务，目标是先得到一个 **能 100% 通过所有测试用例** 的网络。此时不追求体积最小，只追求正确。

两种路径：

- **路径 A — 手工权重**（优先）：分析 train 用例的变换规律，直接手写卷积核权重。适合规律清晰的任务。
- **路径 B — 训练权重**（备选）：对规律不明显的任务，用训练数据学习权重。使用最简单的可行架构。

```python
# 基线网络示例（1×1 Conv，手工权重）
def weight(channel_out, channel_in, kernel_coord):
    # 简单颜色映射：1→2, 2→4, 3→6
    if kernel_coord == (0, 0):
        if channel_in == 1 and channel_out == 2: return 1.0
        if channel_in == 2 and channel_out == 4: return 1.0
        if channel_in == 3 and channel_out == 6: return 1.0
    return 0.0

network = neurogolf_utils.single_layer_conv2d_network(weight, kernel_size=1)
```

### 2.2 Step 2：生成个性化思考日志

**每任务一个独立的思考 MD 文件**，是后续优化的核心上下文。格式参照 Code Golf 项目的 `thinking/task{id}_thinking.md`：

```markdown
# 任务 {id} 思考日志

## Round 1 — 基线

### 任务分析
- 输入：3×3 grid，10 通道（颜色 0-9）
- 输出：3×3 grid，10 通道
- 变换规律：[具体描述，如"将颜色5包围的区域填充为颜色0"]
- 参考 ATCoder 描述：[如有]

### 基线快照
- 架构：1×1 Conv, 10→10 channels, no bias
- 参数量：100
- 内存占用：XX bytes
- Cost：XXX
- 通过情况：train 5/5, test 1/1, arc-gen 262/262 ✓

### 观察
- [关键发现，如"只有通道1和通道3参与变换，其余通道恒等映射"]
- [约束条件，如"输出grid尺寸与输入相同"]

### 实验
1. 尝试去除非相关通道 → cost 降至 XX ✓
2. 尝试 1×1 替代 3×3 → 部分用例失败 ✗

### 下一步
- 尝试将权重全部量化为整数
- 研究是否可用更少的输出通道实现相同变换

---

## Round 2 — 通道压缩

### 当前状态
- 在上轮基础上将中间通道从 10→3
- Cost：XXX → YYY

### 实验
...
```

### 2.3 Step 3-4：迭代优化

每轮优化的核心问题：
1. 这个任务真正需要的最小计算量是多少？
2. 权重中哪些是冗余的（始终为 0 或可合并）？
3. 能否用更小的核、更少的通道、更少的层实现相同结果？

每轮结束后更新思考日志，记录本轮尝试了什么、哪些成功了、哪些失败了。

### 2.4 难度分层策略（继承自 Code Golf）

与 Code Golf 相同：如果同时处理多个任务，**从简单到困难排序**。简单的任务可能 1-2 轮就完成，困难的任务投入更多轮次。可以放弃极困难的任务，集中精力攻克可行的。

---

## 三、项目目录结构

```
neurogolf/
├── data/
│   └── training/                  # ARC-AGI 训练任务 JSON
│       ├── task001.json
│       ├── ...
│       └── task400.json
│
├── baseline/
│   └── task{id}.py                # 基线网络定义（Python，未经压缩）
│
├── networks/
│   └── task{id}.py                # 优化后的网络定义
│
├── onnx_export/
│   └── task{id}.onnx              # 导出的 ONNX 模型
│
├── thinking/                      # ★ 核心：每任务的个性化思考日志
│   ├── task001_thinking.md
│   ├── task002_thinking.md
│   └── ...
│
├── output/                        # 最终提交文件
│   └── task{id}_cost{}.onnx       # 文件名嵌入 cost
│
├── ATCoder/                       # 每任务的中/英文问题描述（辅助理解）
│   ├── TASK001_ZH.md
│   ├── TASK001_EN.md
│   └── ...
│
├── tools/
│   ├── neurogolf_utils.py         # 官方工具库
│   ├── task_analyzer.py           # 自动分析变换规律
│   ├── validate_onnx.py           # ONNX 合规性检查
│   ├── test_network.py            # 在全部测试集上验证正确性
│   ├── compute_cost.py            # 计算 cost = params + memory
│   └── batch_runner.py            # 批量处理所有任务
│
├── analysis/                      # 整体分析文档
│   ├── task_difficulty.csv        # 任务难度分级
│   └── architecture_stats.md      # 各架构使用统计
│
├── txts.txt                       # 批量提示词文本
└── AGENTS.md                      # 系统提示词
```

---

## 四、技术方案

### 4.1 网络架构选择策略

| 复杂度 | 任务特征 | 推荐架构 | 典型 cost |
|---|---|---|---|
| 简单 | 逐像素颜色映射 | 1×1 Conv, 10→Nch, 手工权重 | ~100-500 |
| 中等 | 局部邻域操作 | 3×3 Conv, 手工权重 | ~500-2000 |
| 复杂 | 几何变换、多步操作 | 多层 Conv 或 3×3 手工权重 | ~2000-10000 |
| 极复杂 | 条件逻辑、多对象交互 | 多层训练 + 手工精炼 | ~5000-50000 |

### 4.2 手工权重设计原则

参考官方示例中的 `neurogolf_utils.single_layer_conv2d_network(weight, kernel_size=K)`：

```python
def weight(channel_out, channel_in, kernel_coord):
    """
    channel_out: 输出通道 (0..C_out-1)
    channel_in:  输入通道 (0..C_in-1)，通常 0..9 对应颜色
    kernel_coord: 卷积核坐标 (row_offset, col_offset)
    
    返回该位置的权重值
    """
```

常用权重组装模式：
- **恒等映射**：`channel_out == channel_in and kernel_coord == (0,0)` → `1.0`
- **颜色替换**：`channel_in == old_color and channel_out == new_color and kernel_coord == (0,0)` → `1.0`
- **颜色清除**：`channel_in == color_to_clear and kernel_coord == (0,0)` → `-1.0`
- **邻域扩散**：在不同 kernel_coord 上设非零值

### 4.3 训练权重路径

对于难以手工归纳的任务：
1. 将 ARC-AGI train/test JSON 转为 (input_grid, output_grid) 训练对
2. 构建最小可行架构
3. 训练至 100% 准确率
4. 导出 ONNX
5. 对导出的权重进行分析，尝试手工精炼（删除冗余通道、合并对称权重）

### 4.4 ONNX 合规性检查

```python
import onnx

model = onnx.load("task001.onnx")

# 1. 检查静态形状
onnx.checker.check_model(model)

# 2. 形状推断
inferred = onnx.shape_inference.infer_shapes(model)

# 3. 禁用算子检查
FORBIDDEN_OPS = {'Loop', 'Scan', 'NonZero', 'Unique', 'Script', 'Function'}
for node in inferred.graph.node:
    if node.op_type in FORBIDDEN_OPS:
        raise ValueError(f"禁止的算子: {node.op_type}")

# 4. 文件大小检查
import os
assert os.path.getsize("task001.onnx") <= 1.44 * 1024 * 1024
```

### 4.5 Cost 计算

```python
def compute_cost(onnx_path):
    # 参数量 = 所有权重/偏置张量的元素数之和
    # 内存占用 = 参数字节数 + 中间激活字节数
    # 中间激活 = 每层输出的 (batch × H × W × C) × sizeof(dtype)
    
    total_params = sum(
        np.prod(tensor.dims) 
        for initializer in model.graph.initializer
        for tensor in [initializer]
    )
    
    memory = total_params * 4  # FP32 = 4 bytes
    # + 中间激活的内存（取决于网络结构）
    
    return total_params + memory
```

---

## 五、体积优化技巧

### 架构层面

| 技巧 | 说明 | 典型收益 |
|---|---|---|
| 1×1 优先 | 大多数颜色映射只需 1×1 卷积 | 减少 8/9 参数 |
| 去 bias | 对纯变换任务通常不需要 | 减少 C_out 参数 |
| 最小中间通道 | 二分搜索最小可行的中间通道数 | 线性减少参数 |
| 单层优先 | 能单层解决就不加层 | 避免激活内存 |
| 整数权重 | INT8 替代 FP32 权重 | 内存 ÷4 |

### 权重层面

| 技巧 | 说明 |
|---|---|
| 稀疏 → 密集精炼 | 训练出的稀疏权重 → 手工归纳为更少的密集通道 |
| 通道重排 | 将活跃通道集中到前几个索引，删除尾部全零通道 |
| 对称性复用 | 如果变换有对称性，用更少的核 + 输入变换实现 |
| 权重合并 | 将多个线性变换组合为一个（Conv + Conv → 单一 Conv） |

### 验证层面

| 技巧 | 说明 |
|---|---|
| 全用例零容忍 | train + test + arc-gen 须 100% 像素一致 |
| 防过拟合 | 不要在公开集上调参过度——私有测试集才是真正的验证 |
| 批量测试 | 一次运行全部 400 个 ONNX，生成通过率报告 |

---

## 六、从 Code Golf 项目直接复用的经验

| Code Golf 经验 | NeuroGolf 对应实现 |
|---|---|
| thinking/ 目录（334 个 MD） | 同样为每任务维护思考日志 |
| 基线 + 多轮迭代 | 基线网络 → 逐轮压缩 |
| 从简单到困难排序 | 同样策略 |
| ATCoder 任务描述 | 可复用（相同任务） |
| 输出文件命名自文档化 | `task{id}_cost{}.onnx` |
| 手工技巧 > 自动生成 | 手工权重 > 训练权重 |
| 大胆猜测 → 测试 → 修复 | 剪枝 → 验证 → 回退/修复 |
| texts.txt 批量提示词 | 同样可构建批量 prompt |
| AHK UI 自动化 | 如 Kaggle 界面上有类似需求可复用 |
