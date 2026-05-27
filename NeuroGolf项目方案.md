# NeuroGolf — ARC-AGI ONNX 神经网络压缩比赛方案

## 一、比赛概述

**目标**：为 ARC-AGI v1 的 400 个任务构建最小 ONNX 神经网络，100% 通过所有测试。

**评分**：`score = max(1, 25 - ln(params + memory_bytes))`

**硬约束**：静态形状 · 算子白名单（禁止 Loop/Scan/NonZero/Unique/Script/Function/Compress）· ≤1.44MB · 通过私有测试集

---

## 二、实际项目结构

```
neurogolf/                          # github.com/gitzhubj/neurogolf
├── input/                          # 官方数据（不提交 git，太大 ~95MB）
│   ├── task001.json ~ task400.json # ARC-AGI 测试数据 (train+test+arc-gen)
│   └── neurogolf_utils/            # 官方工具库原始文件
│
├── networks/                       # ★ 网络源码（git 跟踪，可重建 ONNX）
│   └── task{id}.py                 # weight_fn + build()，入口脚本
│
├── onnx_export/                    # 构建产物（不提交 git）
│   └── task{id}.onnx               # 从 networks/ 运行生成
│
├── thinking/                       # ★ 每任务思考日志（git 跟踪）
│   └── task{id}_thinking.md        # 分析→设计→验证→结论，多轮迭代
│
├── tools/
│   ├── neurogolf_utils.py          # 官方工具库（已适配本地 input/ 路径）
│   ├── local_runner.py             # 本地开发入口
│   └── test_network.py             # 正确性验证
│
├── .github/                        # CI/CD（3 条流水线 + 5 个脚本）
│   ├── workflows/                  # pr-validate / merge-to-main / scheduled-submit
│   ├── scripts/                    # validate_onnx / compute_cost / compare / update / submit
│   └── config/task_registry.json   # 版本注册表（唯一真相源）
│
├── output/                         # 最终提交 .zip
├── AGENTS.md                       # 系统提示词
└── .gitignore                      # input/*.json / onnx_export/*.onnx / profiling*.json
```

### Git 策略

| 提交 | 不提交 |
|---|---|
| `networks/*.py`（源码） | `input/*.json`（太大，95MB） |
| `thinking/*.md`（思考日志） | `onnx_export/*.onnx`（构建产物） |
| `tools/`、`.github/`、`AGENTS.md` | `profiling*.json`（运行时临时文件） |

ONNX 是构建产物：从 `networks/task{id}.py` 运行 `verify_network` 即可重新生成。

### 实际环境

```bash
pip install onnx onnxruntime numpy onnx_tool matplotlib ipython kaggle
```

- Kaggle 账号：`zjzhujie`，比赛 slug：`neurogolf-2026`
- GitHub 仓库：`github.com/gitzhubj/neurogolf`
- SSH 推送（HTTPS 被墙）

---

## 三、实战工作流（已跑通）

### 每任务的完整闭环

```
Step 1: 快速扫描 → 识别任务复杂度 → 选最简单的入手
    │
    ▼
Step 2: 分析变换规律 → 推导映射关系（制表）
    │
    ▼
Step 3: 手写 weight_fn → 构建网络 → verify_network 验证
    │
    ├─ 100% 通过 → Step 4
    └─ 有错误 → 分析失败用例 → 修正 → 重试
    │
    ▼
Step 4: 生成/更新 thinking/task{id}_thinking.md
    │  (记录映射表、权重代码、验证结果、cost、结论)
    │
    ├─ 可继续压缩 → 尝试优化 → 回到 Step 3
    └─ 已达理论下界 → 标记 DONE
    │
    ▼
Step 5: git commit → push（networks/ + thinking/）
```

### 任务分析——从 train 用例推导变换规律

直接打印 train/test 用例，肉眼分析输入→输出的映射关系：

```bash
python -c "
import json
with open('input/task016.json') as f:
    d = json.load(f)
for i, ex in enumerate(d['train']):
    print(f'--- train[{i}] ---')
    print('input:', ex['input'])
    print('output:', ex['output'])
"
```

对每个任务问三个问题：
1. **尺寸变了吗？** → 同尺寸用 1×1，放大/缩小可能需要空间卷积
2. **是逐像素映射吗？** → 如果是，1×1 Conv 直接解
3. **有条件逻辑吗？** → 如果需要 if-then，单层 Conv 不够（需要非线性）

### 网络定义模板

```python
# networks/task{id}.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import neurogolf_utils as nu

def weight_fn(ch_out, ch_in, kernel_coord):
    # 在此填充你的权重逻辑
    return 0.0

def build():
    return nu.single_layer_conv2d_network(weight_fn, kernel_size=1)

if __name__ == '__main__':
    task_num = 16  # 修改为实际任务号
    examples = nu.load_examples(task_num)
    network = build()
    nu.verify_network(network, task_num, examples)
```

运行：`python networks/task016.py`

`verify_network` 会：
1. 保存 ONNX 到当前目录
2. 在 train+test 上运行（输出通过/失败数）
3. 在 arc-gen 上运行
4. 输出 params、memory、score

---

## 四、已积累的实战经验

### 4.1 任务复杂度分级

| 级别 | 特征 | 架构 | 示例 | 状态 |
|---|---|---|---|---|
| 简单 | 同尺寸，逐像素颜色映射 | 1×1 Conv | task016 | ✓ DONE |
| 中等 | 局部邻域操作（膨胀、边缘） | 3×3 Conv | — | — |
| 复杂 | 尺寸变化 + 空间平铺 | ≥2 层或 Resize | task001 | 已分析 |
| 极复杂 | 条件逻辑 + 多对象交互 | 多层 + ReLU | — | — |

### 4.2 单层 Conv 的局限性（来自 task001 的分析）

Task001 的变换是：`output = gate × pattern`（如果开关值≠0 则铺图案，否则全零）。

单层 Conv2D 无法表达：它是线性算子（加权求和），做不了乘法/if-then。即使 kernel_size=13 覆盖了全部空间距离（从 output[8][8] 回溯 input[0][0]，最大偏移 6），也无法实现门控逻辑。

**结论**：需要 ≥2 层（含 ReLU 非线性）或 Resize 算子。优先攻克能用单层解决的任务。

### 4.3 1×1 Conv 的最优性（来自 task016 的验证）

Task016 是纯颜色交换（4 对互换），用 1×1 Conv, 10→10ch, no bias 即达理论最小：
- 非零权重 = 有效的颜色映射数（8）+ 恒等映射（2）= 10
- 参数量 = 10×10 = 100（无法更少：输入 10 通道是固定的）
- 已标记 DONE，无需进一步优化

**可复用模式**：颜色映射表 → 1×1 Conv weight_fn

### 4.4 思考日志标准格式

```markdown
# Task {id} 思考日志

## Round 1 — 基线
### 任务分析（尺寸、变换规律、映射表）
### 网络设计（架构、参数、预期 cost）
### 基线权重函数（完整代码块）
### 验证结果（ARC-AGI X/Y, ARC-GEN X/Y, cost, score）
### 结论（标记 DONE 或规划下一步优化）

## Round 2 — 优化（如适用）
...
```

---

## 五、后续推进策略

### 当前进度：1/400

### 下一步按优先级：

1. **批量扫描** 400 个任务，自动分类（同尺寸/不同尺寸、颜色映射/空间变换）
2. **优先攻克简单级**：所有能用 1×1 Conv 解决的颜色映射任务
3. **中等任务**：搭建 3×3 Conv 模板，逐个分析邻域操作规律
4. **困难任务**：设计 ≥2 层网络构建工具（目前仅有单层 helper）
5. **极困难任务**：考虑训练 or 放弃

### Git 工作流

```bash
# 每完成一个任务
git add networks/task{id}.py thinking/task{id}_thinking.md
git commit -m "feat(task{id}): {简述}, {params}p, {pass_rate} pass"
git push
```

---

## 六、与 Code Golf 项目的对应

| Code Golf | NeuroGolf（实际实现） |
|---|---|
| `thinking/task{id}_thinking.md` | 同，已定版格式 |
| `final/task{id}.py`（压缩壳） | `networks/task{id}.py`（权重源码） |
| `output/`（带指标命名） | `onnx_export/`（构建产物） |
| `raw/`（历史版本） | git history 替代 |
| `compressed/`（旧格式） | 无对应（单层架构不需要） |
| 基线→思考→优化闭环 | 同，已跑通 |
| tester.py | `verify_network()` |
| 从简单到困难排序 | 同，需先批量扫描 |
