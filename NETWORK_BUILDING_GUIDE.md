# NeuroGolf 网络搭建与优化指南

> **当前工作模式**：从 baseline ONNX 转换的 `networks/taskXXX.py` 出发，持续优化降低 cost。400 个任务已有初始方案（从 baseline 生成），现在的重点是**比 baseline 做得更好**。

---

## 优化工作流（当前主要流程）

### Step 0: 起点 — 从 baseline 生成初始方案

```bash
# 全部 400 个任务已生成
python tools/onnx_to_network.py --all

# 单个任务
python tools/onnx_to_network.py --task 16
```

生成的 `networks/taskXXX.py` 包含：
- 变换规则说明（从 `problem_specs/` 读取）
- Baseline 架构信息（算子列表、节点数、文件大小）
- 完整的 `build()` 函数（从 baseline ONNX 直接翻译）
- 标注"待优化"

### Step 1: 理解当前方案

```bash
# 阅读 spec 了解规则
cat problem_specs/task016_spec.md

# 运行 baseline 看当前 cost
python networks/task016.py
```

### Step 2: 寻找优化方向

对照 `BASELINE_TECHNIQUES.md` 的 6 大模式：

| 当前 baseline 用 | 可能的优化 | 典型收益 |
|---|---|---|
| 1×1 Conv 颜色映射 | → Gather(axis=1) | 100p→10p |
| 3×3 Conv 平移 | → Gather(axis=2/3) | 900p→30p |
| Conv 旋转/镜像 | → Transpose | 900p→0p |
| Conv 裁剪 | → Slice+Pad | 900p→6p |
| 粗粒度 Conv+ReLU | → Reduce+Where | 减少中间张量 |
| 过宽的 kernel | → 缩小 kernel_size | params/9 |

### Step 3: 修改 → 验证 → 对比

```bash
# 修改 networks/taskXXX.py 中的 build()
# 运行验证
python networks/taskXXX.py

# 如果 cost 下降且通过率 100%，记录到 thinking/
# 如果失败，debug_compare 分析原因
```

### Step 4: Git 提交 → PR → CI 自动验证 → Kaggle 自动提交

```bash
# 1. 提交代码
git add networks/taskXXX.py thinking/taskXXX_thinking.md
git commit -m "opt(taskXXX): 优化简述, cost从X降到Y"

# 2. 推送并创建 PR
git push origin feat/taskXXX
gh pr create --title "opt(taskXXX): 优化简述" --body "cost: X -> Y"
```

**CI 自动流水线**：
1. PR 触发 `pr-validate.yml`：ONNX 合规性 + 正确性 + cost 对比
2. cost 改善 → 自动合并 → 触发 `merge-to-main.yml`
3. `merge-to-main.yml`：更新 `task_registry.json` + 打包提交 Kaggle
4. Kaggle 评分完成后，本地拉取分数：

```bash
# 拉取 Kaggle 最新分数（CI 已自动提交）
python tools/submit_tracker.py --fetch

# 查看历史趋势
python tools/submit_tracker.py --history
```

**分数反馈**：
1. `--fetch` 获取 Kaggle public score → 对比上次计算 delta
2. 分数上升 → 确认有效，更新 thinking log
3. 分数下降 → 分析原因，可能需要回滚

**建议**：每次 PR 只包含 1-3 个优化过的任务，方便精确归因分数变化。

## 目录结构（更新）

```
neurogolf/
├── input/                        # 官方任务 JSON 数据
│   └── taskXXX.json
├── problem_specs/                # 每个任务的规则规范（含 baseline 验证的架构提示）
│   └── taskXXX_spec.md
├── networks/                     # ★ 每个任务的当前最优实现
│   └── taskXXX.py                # 从 baseline 出发，持续优化
├── baseline/                     # 他人高分 baseline（参考，不是终点）
│   └── taskXXX.onnx
├── onnx_export/                  # 验证通过后 ONNX 输出
│   └── taskXXX.onnx
├── thinking/                     # ★ 思考日志（强制执行，轮次制）
│   └── taskXXX_thinking.md
├── BASELINE_TECHNIQUES.md        # 从 baseline 学到的 6 大算子模式
├── tools/                        # 工具脚本
│   ├── onnx_to_network.py        # baseline ONNX → networks/
│   ├── analyze_task_rules.py     # 自动检测变换规则
│   ├── batch_update_rules.py     # 批量更新 spec
│   ├── task_scanner.py           # 任务优先级扫描
│   ├── neurogolf_utils.py        # 核心工具库
│   └── local_runner.py           # 本地运行器
└── .github/                      # CI/CD 自动化
```

---
│   └── taskXXX_thinking.md
├── tools/                        # 官方工具和辅助脚本
│   ├── neurogolf_utils.py        # 核心工具库
│   ├── local_runner.py           # 本地运行器
│   ├── network_builder.py        # 网络构建器
│   └── batch_runner.py           # 批量验证
├── profiler_traces/               # ONNX Runtime profiler 自动生成的 JSON trace 文件
│   └── XXX_2026-MM-DD_*.json      # 验证时自动产生，可定期清理
└── NETWORK_BUILDING_GUIDE.md     # 本文件
```

## 约束条件速览

| 项目 | 值 |
|------|-----|
| 输入/输出形状 | `(1, 10, 30, 30)` |
| 数据类型 | FLOAT (`TensorProto.FLOAT`) |
| IR version | 10 |
| Opset | 10 |
| 黑名单算子 | Loop, Scan, NonZero, Unique, Script, Function, Compress |
| 文件大小上限 | 1.44 MB |
| 输出像素约束 | 每个位置有且仅有一个通道 = 1.0 |

评分公式: `points = max(1.0, 25.0 - ln(max(1.0, memory_bytes + params)))`

---

## 批量任务扫描与优先排序（工作开始前必做）

在逐任务搭建前，必须先做全局扫描，从简单到困难排序。这是 codegolf 的核心经验 —— 不要随机选任务。

### 扫描脚本

```python
import sys; sys.path.insert(0, 'tools')
import neurogolf_utils as nu
import json, os

def classify_task(tid):
    """基于 spec 和实际数据的快速分类"""
    spec_path = f"problem_specs/task{tid:03d}_spec.md"
    data_path = f"input/task{tid:03d}.json"
    
    # 尝试读 spec
    try:
        with open(spec_path) as f:
            spec = f.read()
    except FileNotFoundError:
        spec = ""
    
    # 尝试读数据
    try:
        with open(data_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        return tid, "no_data", {}
    
    # 快速特征
    trains = data.get("train", [])
    info = {
        "train_samples": len(trains),
        "arcgen_samples": len(data.get("arc-gen", [])),
        "same_size": all(
            len(e["input"]) == len(e["output"]) and len(e["input"][0]) == len(e["output"][0])
            for e in trains
        ) if trains else False,
        "spec_says_1x1": "single_1x1_conv" in spec or "1x1 Conv" in spec,
        "spec_says_3x3": "3x3" in spec or "kxk_conv" in spec,
        "spec_says_infeasible": "infeasible" in spec.lower() or "no" in spec,
    }
    
    # 分类
    if not trains:
        tier = "no_data"
    elif info["spec_says_1x1"] and info["same_size"]:
        tier = "tier1"  # 最简单的逐像素映射
    elif info["spec_says_3x3"] and info["same_size"]:
        tier = "tier2"  # 局部邻域
    elif info["same_size"] and not info["spec_says_infeasible"]:
        tier = "tier3"  # 可能可行
    elif info["spec_says_infeasible"]:
        tier = "tier5"  # 大概率不可行
    else:
        tier = "tier4"  # 待研究
    
    return tid, tier, info

# 扫描全部 400 个任务
tiers = {"tier1": [], "tier2": [], "tier3": [], "tier4": [], "tier5": [], "no_data": []}
for tid in range(1, 401):
    _, tier, info = classify_task(tid)
    tiers[tier].append((tid, info))

print("=== 任务优先级排序 ===")
print(f"Tier 1 (简单-1x1): {len(tiers['tier1'])} 个 → 优先攻克")
print(f"Tier 2 (中等-3x3): {len(tiers['tier2'])} 个")
print(f"Tier 3 (待探索):    {len(tiers['tier3'])} 个")
print(f"Tier 4 (困难):      {len(tiers['tier4'])} 个")
print(f"Tier 5 (大概率不可行): {len(tiers['tier5'])} 个")
print(f"No data:           {len(tiers['no_data'])} 个")

# 输出前 20 个最优先任务
print("\n前 20 个优先任务:")
for tid, info in tiers["tier1"][:20]:
    print(f"  task{tid:03d}: trains={info['train_samples']}, arcgen={info['arcgen_samples']}")
```

### 优先级规则

1. **Tier 1 优先** — `single_1x1_conv_possible: yes`，同尺寸，纯颜色映射 → 半小时内可解
2. **Tier 2 其次** — 3×3 Conv 可解，局部邻域 → 1 小时内可解
3. **Tier 3 再其次** — 可能可行，需探索 → 1-2 小时
4. **Tier 4** — 困难，需多层+复杂 bypass → 3 轮无进展即放弃
5. **Tier 5** — 标记 infeasible，写 stub + 原因，转向下一个

**核心原则**：产出速度 >> 攻克一个极难任务。400 个任务中如果有 50 个可解，先全做完再回头攻坚。

---

## 完整搭建流程（从零到提交）

### Step 1: 读取规范文件

```bash
cat problem_specs/taskXXX_spec.md
```

spec 文件结构:
- **核心规则** — 变换逻辑描述（颜色映射、空间变换公式等）
- **关键证据** — 从训练样例中提取的规律
- **歧义与风险** — 不确定的地方和当前假设
- **架构提示** — 推荐架构、kernel 大小、是否需非线性
- **YAML 摘要** — 结构化元信息

**重要**: spec 是初步猜测，不与实际数据保证一致。spec 中标记的 `single_1x1_conv` 等建议可能错误，务必以 `input/taskXXX.json` 的实际数据为准。

### Step 2: 加载数据并验证 spec

```python
import sys; sys.path.insert(0, 'tools')
import neurogolf_utils as nu

ex = nu.load_examples(task_num)

# 快速查看第一个训练样本的 ASCII 网格
nu.show_one(ex['train'][0])

# 统计所有样本的尺寸和颜色
for mode in ['train', 'test']:
    for i, e in enumerate(ex[mode]):
        h, w = len(e['input']), len(e['input'][0])
        oh, ow = len(e['output']), len(e['output'][0])
        inc = sorted(set(c for row in e['input'] for c in row))
        outc = sorted(set(c for row in e['output'] for c in row))
        print(f"{mode}[{i}]: {h}x{w} -> {oh}x{ow}, in={inc}, out={outc}")

# 检查 arc-gen 样本数
print(f"arc-gen: {len(ex.get('arc-gen', []))} examples")
```

**对照清单**:
- [ ] spec 描述的输入/输出尺寸与实际数据一致？
- [ ] spec 描述的颜色集合与实际数据一致？
- [ ] spec 的规则用具体数据代入验证通过？
- [ ] 所有 train 样本是否可以用同一规则解释？

### Step 3: 判断是否可实现

按以下 checklist 判断任务是否可用 ONNX opset 10 实现：

| 特征 | 可实现 | 困难/不可实现 |
|------|--------|---------------|
| 输出仅依赖当前像素 | 1×1 Conv | - |
| 输出依赖固定邻域 (≤9 格) | 3×3~9×9 Conv | - |
| 输出依赖远处但固定偏移 | 宽核 Conv | - |
| 输出依赖行/列全局统计 | Reduce + broadcast | - |
| 输出依赖连通组件 | - | 需要 NonZero/While |
| 输出依赖动态 bounding box | - | 无法用静态算子 |
| 输出尺寸随输入变化 | - | 需要 Loop/动态 shape |
| 对象级条件路由 (if-then-else) | - | 算子不支持分支 |
| 递归/迭代处理 | - | Loop 在黑名单 |

如果判断为可实现，继续下一步。否则在 `networks/taskXXX.py` 中标注为 Stub 并说明原因。

### Step 4: 选择架构模式

架构选择决策树：

```
1. 输出仅依赖当前像素颜色？ → 模式 A (1×1 Conv)
2. 固定方向平移？ → 模式 B (空间平移)
3. 局部邻域检测 (≤k 格)？ → 模式 C (邻域阈值) 或 模式 F-H (多层)
4. 远距离像素比较？ → 模式 C 宽核变体
5. 全局行/列统计？ → 模式 D (Reduce+广播)
6. 多条件逻辑组合？ → 模式 F (AND门) + 模式 G (Clip)
7. 多步时序展开？ → 模式 H (固定步数级联)
8. 以上都不匹配 → 标记 infeasible
```

#### 模式 A: 逐像素颜色重映射 (1×1 Conv)
**适用**: 输出[r,c] 仅依赖 input[r,c] 的颜色，与位置无关，所有位置规则相同。

模板:
```python
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

MAPPING = {1: 5, 5: 1, 2: 6, 6: 2}  # 颜色映射表

def weight_fn(ch_out, ch_in, kc):
    if kc == (0, 0):
        if ch_in in MAPPING and ch_out == MAPPING[ch_in]:
            return 1.0
        if ch_in not in MAPPING and ch_in == ch_out:
            return 1.0
    return 0.0

def build():
    return nu.single_layer_conv2d_network(weight_fn, kernel_size=1)

if __name__ == '__main__':
    task_num = XXX
    ex = nu.load_examples(task_num)
    nu.verify_network(build(), task_num, ex)
```

参考: `networks/task016.py`

#### 模式 B: 空间平移 (3×3 Conv + Constant + Mask)

**适用**: 整体图案向固定方向平移。

模板:
```python
import sys, numpy as np; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu
import onnx

_CH, _H, _W = 10, 30, 30
_GS, _DT = [1, _CH, _H, _W], onnx.TensorProto.FLOAT

def build():
    nodes, inits = [], []

    # 1) Conv 做空间偏移（例: 下移: offset (-1,0) 读上一行）
    K = 3; pad = K // 2
    offsets = list(range(-pad, pad+1))
    w_shape = [_CH, _CH, K, K]
    w_vals = [float(1.0 if ch_o==ch_i and kr==-1 and kc==0 else 0.0)
              for ch_o, ch_i, kr, kc in itertools.product(range(_CH), range(_CH), offsets, offsets)]
    # ... 构建 Conv node

    # 2) Constant 处理边界（如 vacated row/column）
    # ... 构建 Constant + Add/Sub 节点

    # 3) Mul 用 spatial mask 裁剪非 grid 区域

    return onnx.helper.make_model(...)
```

参考: `networks/task053.py`（下移一行）

#### 模式 C: 邻域检测+阈值 (Conv → Add(bias) → ReLU → Conv(1×1))

**适用**: 检测局部模式（如 "3 邻居中有 ≥2 个某颜色"）后映射输出。

核心结构:
```
Conv(K×K) → Add(bias_constant) → ReLU → Add(bg_constant) → Conv(1×1) → Mul(spatial_mask)
```

关键设计:
- Conv 计算邻域特征（对每个通道/位置求和）
- bias 用于阈值判定（如 3 个邻居 → sum=3 → bias=-2.5 → ReLU → 0.5）
- Conv(1×1) 放大信号并映射到输出通道
- bg_constant + W[0,out] 负权重处理背景通道
- spatial_mask 裁剪非输出区域

参考: `networks/task006.py`（AND 检测）, `networks/task095.py`（邻域扩张）, `networks/task097.py`（孤立移除）, `networks/task098.py`（内部挖空）

#### 模式 D: 行/列全局统计 (ReduceSum/Max → Sub → ReLU → Broadcast)

**适用**: 按行或列做统计（计数、最大频率等），阈值判定后广播回整个区域。

核心结构:
```
ReduceSum(axis=W) → ReduceMax(axis=CH) → Sub(threshold) → ReLU → Mul(broadcast_width) → ChannelSelect
```

参考: `networks/task052.py`（行内 3 同色检测）

### 对象级推理的绕过策略

很多 ARC 任务需要"对象级推理"——连通分量检测、边界框提取、条件路由等。
ONNX opset 10 禁用了 Loop/Scan/NonZero，无法直接实现这些能力，但可通过以下策略绕过。

**判断流程**（按优先级尝试）：

```
1. 是否可归约为已验证模式？
   → 如任务实质是邻居计数/阈值，只是表现复杂
   ↓ 否
2. 固定步数展开 (Unrolled Iteration)
   → 把迭代过程展开为 N 个固定层，每层一个时间步
   ↓ 否
3. 位置编码常量 (Position Encoding)
   → 对固定尺寸任务，用 Constant 预置坐标信息
   ↓ 否
4. Reduce + 广播扩展
   → 全局统计后广播回全图
   ↓ 否
5. 标记为 infeasible stub，写明原因
```

#### 策略 1: 归约到已验证模式

很多乍看复杂的任务实质是已验证模式的变体：

| 已验证模式 | 可覆盖的任务特征 |
|-----------|-----------------|
| 3×3 Conv 邻居计数 + 阈值 | 边界检测、内部检测、孤立移除 |
| 宽核 Conv + ReLU | 远距离比较、AND/OR |
| ReduceSum/Max + 广播 | 行/列统计、全局计数 |
| Conv 空间偏移 | 平移、shift |
| 1×1 Conv | 逐像素颜色映射 |

#### 策略 2: 固定步数展开 (Unrolled Iteration)

不用 Loop，把 N 次迭代展开为 N 个固定层堆叠：

```
Conv → ReLU → Conv → ReLU → ... (N 层)
```

每层代表一个时间步的状态。适用场景：
- **Flood fill / 区域填充**：每层从种子点向外扩散 1 步
- **距离变换**：每层传播距离 +1
- **波前传播**：从边界向内部逐层处理

代价：每增加一层就增加约 36KB 中间激活内存。N=5 层 ≈ 180KB 额外 memory。
在 memory+params 评分体系下，多几次层数影响可控（params 通常占主导）。

模板示例（2 步 flood fill）:
```python
# Layer 1: 种子扩散 (颜色 A → 颜色 B 传播 1 步)
Conv(3×3, W[B, A, neighbor]=1.0, W[A, A, center]=1.0)
→ ReLU

# Layer 2: 继续扩散 (新 B → B 再传播 1 步)
Conv(3×3, W[B, B, neighbor]=1.0, W[A, A, center]=1.0)
→ ReLU

# ... 可以继续堆叠
```

#### 策略 3: 位置编码常量 (Position Encoding)

对**固定尺寸**的任务（如所有样本都是 9×9），用 Constant 张量编码坐标：

```python
# 将行坐标写入 channel 1: pos[r,c] = r / 30.0
row_pos = np.zeros(_GS, dtype=np.float32)
for r in range(grid_h):
    row_pos[0, 1, r, :grid_w] = r / 30.0

# 将列坐标写入 channel 2: pos[r,c] = c / 30.0
col_pos = np.zeros(_GS, dtype=np.float32)
for c in range(grid_w):
    col_pos[0, 2, :grid_h, c] = c / 30.0
```

然后通过 Add 或 Mul 将位置信息注入数据流，Conv 即可感知位置。
适用场景：反对角线、特定行/列填充、位置相关的模板覆盖。

**限制**：仅适用于所有样本尺寸相同的任务。若尺寸不统一，此策略不可用。

#### 策略 4: Reduce + 广播扩展

在 task052 的 ReduceSum→ReduceMax→阈值→广播 基础上扩展：
- **边界检测**：找最大/最小非零坐标（用位置编码 × 颜色通道后 ReduceMax）
- **颜色频率统计**：ReduceSum 统计每个颜色像素数后与阈值比较
- **对象计数**：ReduceSum over all channels，判断对象数量

#### 策略 5: 标记 infeasible

当以上策略都不适用时，在 `networks/taskXXX.py` 中明确标注：

```python
"""Task XXX — OBJECT LOGIC REQUIRED
Reason: requires connected-component labeling.
Banned ops needed: NonZero, Loop.
No feasible bypass under opset 10 constraints.
"""
```

### Step 5: 编写网络文件

在 `networks/taskXXX.py` 中实现，文件名必须与任务编号对应。

**文件模板**:
```python
"""Task XXX — 简短描述

规则: ...

架构: ...
"""
import sys, numpy as np, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import neurogolf_utils as nu
import onnx

_CH, _H, _W = 10, 30, 30
_GS = [1, _CH, _H, _W]
_DT = onnx.TensorProto.FLOAT


def build():
    nodes, inits = [], []
    # ... 构建 ONNX graph nodes 和 initializers ...
    x = onnx.helper.make_tensor_value_info("input", _DT, _GS)
    y = onnx.helper.make_tensor_value_info("output", _DT, _GS)
    graph = onnx.helper.make_graph(nodes, "g", [x], [y], inits)
    return onnx.helper.make_model(graph, ir_version=10,
                                   opset_imports=[onnx.helper.make_opsetid("", 10)])


if __name__ == '__main__':
    task_num = XXX
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
```

### Step 6: 本地验证与调试

**运行完整验证**:
```bash
python networks/taskXXX.py
```

成功输出示例:
```
Results on ARC-AGI examples: 4 pass, 0 fail
Results on ARC-GEN examples: 262 pass, 0 fail

Your network IS READY for submission!
It appears to require 288000 bytes + 1000 params, yielding 12.337 points.
```

验证通过后，ONNX 文件自动保存在 `onnx_export/taskXXX.onnx`。

**单样例调试**（失败时定位问题）:
```python
import sys; sys.path.insert(0, 'tools')
import neurogolf_utils as nu
from networks.taskXXX import build

# 文本对比期望 vs 实际（标注差异像素）
nu.debug_compare(build(), task_num=XXX, example_idx=0)
```

**查看原始 tensor 值**:
```python
import onnx, onnxruntime as ort
ex = nu.load_examples(XXX)

network = build()
onnx.save(network, 'onnx_export/_debug.onnx')
san = nu.sanitize_model(onnx.load('onnx_export/_debug.onnx'))
sess = ort.InferenceSession(san.SerializeToString(), ...)

bm = nu.convert_to_numpy(ex['train'][0])
result = sess.run(['output'], {'input': bm['input']})

# 检查特定通道/区域的原始浮点值
print(result[0][0, 2, :5, :5])  # ch=2, rows 0-4, cols 0-4
```

### Step 7: 记录思考日志（强制执行）

**必须使用轮次制格式**，每轮记录观察→实验→下一步。即使实验失败也必须记录，避免重复尝试相同方案。

```markdown
# 任务 XXX 思考日志

## Round 1 — 基线
### 任务分析（变换规律、grid 尺寸、涉及的颜色通道、从 train 用例推导的映射关系）
### 基线快照（架构、参数量、内存、cost、通过情况）
### 观察（问题本质、关键约束、与 spec 的一致性/偏差）
### 实验（列出尝试过的方法及结果——即使失败也要记录）
### 下一步（规划后续尝试方向）

## Round 2 — 优化
### 观察（对上一轮失败/成功的分析）
### 实验（具体尝试及 cost 变化）
### 下一步

... (继续 Round N 直到 DONE)

## Score Tracking
> 以下由 submit_tracker.py 自动更新

| 日期 | Public Score | Delta | 备注 |
|---|---|---|---|
| YYYY-MM-DD HH:MM | X.XX | +0.00 | Kaggle 提交 |
```

保存到 `thinking/taskXXX_thinking.md`。

---

### Step 7b: 迭代优化循环（核心——参考 codegolf 实验驱动流程）

基线通过后，进入系统化的优化循环。这是 codegolf 最关键的流程，也是 AI agent 产出的核心环节。

#### 优化维度（按优先级）

| 优先级 | 方向 | 目标 | 典型收益 |
|--------|------|------|----------|
| 1 | 减少通道数 | 输出通道从 10 减到实际使用的 k 个 | params 减少 k²→10² |
| 2 | 缩小 kernel | 3×3 → 1×1（如果可行） | params ×9 |
| 3 | 合并层 | 把 Add+Mul 逻辑压入一个 Conv 权重 | 减少 1 个中间张量 (~36KB) |
| 4 | 权重稀疏化 | 移除零权重，重排通道使权重连续 | 微小（主要影响 ONNX 序列化大小） |
| 5 | 常数压缩 | 用更小的 Constant 表达相同逻辑 | 几个 KB |

#### 典型优化循环

```
基线通过 (Round 1)
    │
    ▼
尝试减少通道数 → verify
    ├─ 全通过 → 记录 Round 2，标记里程碑
    └─ 有失败 → 分析 debug_compare 输出 → 修正 → 重试
    │
    ▼
尝试缩小 kernel → verify
    ├─ 全通过 → 记录 Round 3
    └─ 有失败 → 分析是否本质需要邻域信息 → 保持 3×3
    │
    ▼
尝试合并层 → verify
    ├─ 全通过 → 记录 Round 4，cost 可能接近理论下界
    └─ 部分失败 → 考虑保留关键层
    │
    ▼
标记 DONE（或放弃：3 轮无进展 → infeasible stub）
```

#### 失败分析工具

```python
# 定位失败用例的具体差异
nu.debug_compare(build(), task_num=XXX, example_idx=0)

# 检查中间层激活值（多层网络调试）
import onnxruntime as ort
sess = ort.InferenceSession('onnx_export/taskXXX.onnx')
# 添加中间输出到 graph，观察每层行为

# 逐用例验证（对大测试集分批验证）
for i, e in enumerate(ex['arc-gen']):
    pred = nu.run_one(build(), e['input'])
    if not match(pred, e['output']):
        print(f"ARC-GEN[{i}] failed")
        nu.show_one(e)
        break
```

#### 废弃策略

- **3 轮规则**：经过 3 轮实验仍无进展 → 标记为 `infeasible` 或 `given_up`
- **进展定义**：cost 下降 > 5%（或 params 减少 > 10%）
- **优先转移**：将时间投入尚未尝试的简单任务（Tier 1-2）
- **记录必写**：即使放弃，也必须在思考日志最后一轮写明原因

### Step 8: Git 提交

```bash
git add networks/taskXXX.py thinking/taskXXX_thinking.md
git commit -m "feat(task{id}): {简述}, {params}p, {memory}mem, {cost}c"
```

提交后 CI 自动：验证 ONNX → 对比 cost → 更新 registry → 提交 Kaggle。

---

## 调试工具速查

```python
import sys; sys.path.insert(0, 'tools')
import neurogolf_utils as nu

# 数据
nu.load_examples(task_num)              # 加载任务 JSON
nu.show_one(example)                    # ASCII 打印单个样例

# 网络
nu.single_layer_conv2d_network(fn, k)   # 构建单层 Conv 网络
nu.verify_network(network, n, examples) # 端到端验证 (ONNX → onnx_export/)
nu.verify_subset(session, examples)     # 只验证子集
nu.debug_compare(network, n, idx)       # 文本对比期望 vs 实际

# 转换
nu.convert_to_numpy(example)            # ARC grid → one-hot (1,10,30,30)
nu.convert_from_numpy(tensor)           # one-hot → ARC grid

# ONNX 工具
nu.sanitize_model(model)                # 清洗节点名称
nu.check_network(filename)              # 检查文件大小
nu.calculate_params(model)              # 计算参数量
nu.calculate_memory(model, trace_path)  # 计算内存占用
```

## 常见陷阱

| 陷阱 | 说明 | 后果 |
|------|------|------|
| Conv kernel index vs spatial offset | `W[co,ci,i,j]` 读取 `input[r+i-pad, c+j-pad]` | 偏移量计算错误导致读取错误像素 |
| 未使用 same-padding | 输出尺寸 ≠ 30×30 → graph 验证失败 | 模型无法加载 |
| 非网格区域通道全为 0 | 留 0 通道时解为"无颜色"(10)，留 ch0=1 时解为黑色(0) | 输出 grid 填充多余黑色行/列 |
| 一个像素多通道为 1 | convert_from_numpy 标记为 "too many colors"(11) | 验证失败 |
| 一个像素零通道为 1 | convert_from_numpy 标记为 "no color"(10) | 验证失败 |
| 权重非整数 | 浮点精度导致值与预期有微小偏差 | 逐像素对比失败 |
| spec 与实际数据不匹配 | 架构建议可能基于错误的任务理解 | 实现完全不 work |
| 变步数迭代 | 部分任务不同样本需要不同迭代次数 (如 1 步 vs 2 步扩张) | 固定深度网络无法覆盖所有样本 |

## 增强模式：多层网络

单层 Conv 能力有限（仅局部邻居检测），但堆叠多层可实现更复杂的逻辑。以下模式已通过实际验证（task086 部分成功 1/4）：

### 模式 F: AND/OR 逻辑门

使用 `Add → bias → ReLU` 实现二值信号的逻辑门：

```python
# AND gate: A AND B = ReLU(A + B - 1.5) × 2
# 要求 A, B 已被 Clip 到 [0, 1]
and_out = ReLU(signal_A + signal_B - 1.5) * 2.0  # 0.5 if both, 0 otherwise
```

### 模式 G: 值裁剪 (Saturating Clip)

将实数值 (如邻居计数 0-8) 裁剪到 [0, 1]，为逻辑门提供二值输入：

```python
# clip(x) = x - ReLU(x - 1.0)
# 必须逐通道操作，保护其他通道不被清零
clipped_ch = original_ch - ReLU(original_ch - 1.0)
```

### 模式 H: 多步级联 (Fixed-Depth Unrolling)

将 N 步 CA 展开为 N 个 Conv+ReLU 层堆叠：

```
Conv → bias → ReLU → Conv → ReLU → Conv → ReLU → ... (N 步)
```

**限制**: N 必须固定。若不同样本需要不同步数（如 task086），则不可行。

### 典型多层架构

```
Conv(3×3) → bias → ReLU          # 第1层: 特征提取 (邻居计数 + identity)
→ Conv(1×1)                      # 第2层: 放大 + 组合特征
→ Clip(逐通道)                     # 裁剪二值化
→ Conv(1×1) → bias → ReLU        # 第3层: AND/OR 逻辑门
→ Conv(1×1)                      # 第4层: 输出通道映射
```

此架构可表达：条件颜色替换、多条件组合、时序 CA 规则等。

**Clip 辅助函数** (可嵌入任意多层网络):

```python
def add_clip(nodes, inits, input_name, output_name, ch_idx):
    """将指定通道裁剪到 [0, 1]，保留其他通道不变。
    
    原理: clipped[ch] = x[ch] - ReLU(x[ch] - 1.0)
    实现: mask 分离目标通道 → 裁剪 → 加回其他通道
    """
    comp = np.ones(_GS, dtype=np.float32); comp[0, ch_idx, :, :] = 0.0
    mask = np.zeros(_GS, dtype=np.float32); mask[0, ch_idx, :, :] = 1.0
    ones_t = np.zeros(_GS, dtype=np.float32); ones_t[0, ch_idx, :, :] = 1.0
    
    # pass-through: input * complement_mask (保留非目标通道)
    nodes.append(onnx.helper.make_node("Mul", [input_name, comp_init], [f"{output_name}_pass"]))
    # extract target: input * mask (只取目标通道)
    nodes.append(onnx.helper.make_node("Mul", [input_name, mask_init], [f"{output_name}_tgt"]))
    # clip: tgt - ReLU(tgt - 1.0)
    nodes.append(onnx.helper.make_node("Sub", [f"{output_name}_tgt", ones_init], [f"{output_name}_tsub"]))
    nodes.append(onnx.helper.make_node("Relu", [f"{output_name}_tsub"], [f"{output_name}_trel"]))
    nodes.append(onnx.helper.make_node("Sub", [f"{output_name}_tgt", f"{output_name}_trel"], [f"{output_name}_tclip"]))
    # combine
    nodes.append(onnx.helper.make_node("Add", [f"{output_name}_pass", f"{output_name}_tclip"], [output_name]))
```

### 多层网络的代价

| 层数 | 额外中间张量 | 额外 Params | 对得分影响 |
|------|-------------|------------|-----------|
| 2 Conv | ~36KB | ~100-900 | 轻微 |
| 3 Conv | ~72KB | ~200-1800 | 中等 |
| 4 Conv + Clip | ~144KB | ~300-2700 | 明显 |
| 5+ Conv | >180KB | >500 | 显著 |

在 memory+params 评分体系下，5 层以内的多层网络通常可行（params 贡献远小于 memory），
但需权衡准确性 vs 得分。

## 已验证可用的 ONNX 算子 (opset 10)

- **Conv**: 最核心算子，控制 kernel_size, pads, strides
- **Relu**: 阈值/非线性
- **Add**: 逐元素加法（bias、组合 Constant）
- **Sub**: 逐元素减法
- **Mul**: 逐元素乘法（mask、broadcast、放大）
- **Abs**: 绝对值（用于 XOR 等）
- **ReduceSum, ReduceMax**: 沿轴归约
- **Constant**: 静态张量常量
- **Slice**: 沿轴切片
- **Reshape**: 形状变换（需静态 shape）

## 当前已实现任务 (9/100)

| Task | 描述 | 模式 | Points |
|------|------|------|--------|
| 006 | 3×7→3×3 左右半 AND | 模式 C | 12.337 |
| 015 | 正交/对角颜色扩展 | 3×3 Conv | 18.198 |
| 016 | 颜色对调 swap | 模式 A | 20.395 |
| 052 | 行内 3 同色检测 | 模式 D | 13.262 |
| 053 | 整体下移一行 | 模式 B | 12.999 |
| 072 | 上下半 XOR | Conv+Slice+Abs | 13.187 |
| 095 | 5→1 八邻域扩张 | 3×3 Conv | 18.198 |
| 097 | 移除孤立像素 | Conv+ReLU+ReduceSum | 12.383 |
| 098 | 矩形挖空 | Conv+ReLU+ReduceSum | 12.383 |

**总计: 9/100 可实现，91/100 标记为 infeasible**

剩余 91 个任务需要的核心能力：
- 连通分量分析（~25 个）
- 动态 bounding box / crop（~21 个）
- 全局位置感知 / 坐标路由（~19 个）
- 条件分支 / if-then-else（~15 个）
- 迭代 / flood fill（~11 个）

这些能力在 ONNX opset 10 的黑名单约束下（禁 Loop, Scan, NonZero）无法直接实现。
