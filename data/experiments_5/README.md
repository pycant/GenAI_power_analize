# Experiment 5

## 概述

本实验使用从标准测试集抽取的 80 个综合测试用例，评估 4 个 LLM 模型的质效比。

## 配置

- **创建时间**: 2026-03-02 22:43:13
- **原始任务数**: 80
- **模型数量**: 4
- **总测试用例数**: 320 (4 模型 × 80 任务)
- **模型列表**: qwen3:4b, qwen3:8b, deepseek-r1:8b, gemma3:4b

## 任务分布

{
  "qa": 18,
  "math": 12,
  "code": 12,
  "translation": 10,
  "reasoning": 10,
  "summary": 6,
  "creative": 6,
  "multi_turn": 6
}

## 数据来源

{
  "MMLU": 18,
  "GSM8K": 12,
  "HumanEval": 12,
  "FLORES-200": 10,
  "Manual": 28
}

## 测试用例格式

每个测试用例包含以下字段：
- `model`: 模型规格（如 "qwen3:4b"）
- `prompts`: 提示词（字符串或数组）
- `task_type`: 任务类型
- `max_tokens`: 最大生成token数
- `temperature`: 温度参数
- `top_p`: Top-p采样参数
- `idle_measurement_duration`: 空闲基线测量时长（秒）
- `reference_text`: 参考文本（可选，用于质量评估）
- `keep_context`: 是否保持上下文（多轮对话）
- `per_turn_monitoring`: 是否分轮监控（多轮对话）

## 目录结构

```
experiments_5/
├── config.py              # Python 配置文件
├── config.json            # JSON 配置文件
├── test_cases.json        # 测试用例（符合 EXPERIMENT_RUNNER_GUIDE.md 格式）
├── raw/                   # 原始实验结果（按模型分类）
├── texts/                 # 文本输出（按模型分类）
└── summary/               # 汇总结果
    ├── results.csv        # 详细结果
    └── stats.csv          # 统计摘要
```

## 运行实验

```bash
# 使用实验运行器
python experiments/experiment_runner.py --config data/experiments_5/test_cases.json --output-dir data/experiments_5

# 或使用快速测试脚本（如果存在）
python scripts/run_experiment_5.py
```

## 分析结果

```bash
# 运行分析脚本
python scripts/analyze_experiments_5.py
```

## 注意事项

1. 测试用例格式遵循 `docs/EXPERIMENT_RUNNER_GUIDE.md` 规范
2. 每个模型会运行所有 80 个任务
3. 多轮对话任务会自动启用 `keep_context`
4. 所有任务都启用了空闲基线测量（10秒）
5. 运行时间预估：约 640 分钟（假设每个测试用例平均2分钟）

---

生成时间: 2026-03-02 22:43:13
