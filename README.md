# NeuroGolf

IJCAI-ECAI 2026 NeuroGolf Championship — 为 ARC-AGI v1 的 400 个任务构建最小 ONNX 神经网络。

## 快速开始

```bash
# 安装依赖
pip install onnx onnxruntime numpy kaggle onnx_tool

# 本地运行一个任务 (使用 local_runner)
python tools/local_runner.py --task 1
```

## 目录结构

```
neurogolf/
├── input/                # 官方数据 + 工具库原始文件 (不提交 git)
│   ├── task*.json        # 400 个 ARC-AGI 测试数据
│   └── neurogolf_utils/  # 官方工具库原始文件
├── networks/             # 网络定义 (Python)
├── onnx_export/          # 导出的 .onnx 文件
├── thinking/             # 每任务的优化思考日志
├── output/               # 最终提交 zip
├── tools/
│   ├── neurogolf_utils.py  # 官方工具库 (含路径适配)
│   ├── local_runner.py     # 本地开发入口
│   └── test_network.py     # ONNX 正确性验证
├── .github/              # CI/CD 配置
│   ├── workflows/        # 3 条 GitHub Actions 流水线
│   ├── scripts/          # validate, compute_cost, compare, update, submit
│   └── config/task_registry.json
└── AGENTS.md             # 智能体系统提示词
```
