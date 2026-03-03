# ✅ Experiment 5 配置完成

## 状态：准备就绪 🚀

experiments_5 实验配置已完全准备就绪，所有测试用例格式已验证通过。

## 快速概览

- ✅ **320 个测试用例** (4 模型 × 80 任务)
- ✅ **格式验证通过** (符合 EXPERIMENT_RUNNER_GUIDE.md)
- ✅ **目录结构完整** (raw/, texts/, summary/)
- ✅ **配置文件齐全** (config.py, config.json, README.md)

## 模型配置

| 模型 | 参数量 | 测试用例数 |
|------|--------|-----------|
| qwen3:4b | 4B | 80 |
| qwen3:8b | 8B | 80 |
| deepseek-r1:8b | 8B | 80 |
| gemma3:4b | 4B | 80 |

## 任务分布

| 任务类型 | 数量 | 来源 | 测试用例数 (4模型) |
|---------|------|------|------------------|
| QA | 18 | MMLU | 72 |
| Math | 12 | GSM8K | 48 |
| Code | 12 | HumanEval | 48 |
| Translation | 10 | FLORES-200 | 40 |
| Reasoning | 10 | Manual | 40 |
| Summary | 6 | Manual | 24 |
| Creative | 6 | Manual | 24 |
| Multi-turn | 6 | Manual | 24 |
| **总计** | **80** | - | **320** |

## 立即开始

### 1. 验证配置（可选）

```bash
# 验证测试用例格式
python scripts/verify_test_cases_format.py

# 查看配置
cat data/experiments_5/README.md
```

### 2. 运行实验

```bash
# 完整实验（预计 5-16 小时）
python experiments/experiment_runner.py \
  --config data/experiments_5/test_cases.json \
  --output-dir data/experiments_5
```

### 3. 分析结果

```bash
# 运行分析脚本（实验完成后）
python scripts/analyze_experiments_5.py
```

## 关键特性

### ✅ 格式规范

- 所有测试用例符合 `EXPERIMENT_RUNNER_GUIDE.md` 规范
- 包含必需字段：`model`, `prompts`, `task_type`
- 包含可选字段：`max_tokens`, `temperature`, `top_p`, `idle_measurement_duration`, `reference_text`
- 多轮对话正确配置 `keep_context` 和 `per_turn_monitoring`

### ✅ 质量保证

- 所有 QA/Math/Translation 任务包含 `reference_text` 用于质量评估
- Code 任务包含 `canonical_solution` 作为参考
- 多轮对话任务正确配置上下文保持
- 所有任务启用空闲基线测量（10秒）

### ✅ 参数优化

- 根据任务类型设置合适的 `temperature`
  - QA/Math/Code: 0.0-0.1 (确定性)
  - Translation: 0.2 (稳定性)
  - Reasoning: 0.1 (逻辑性)
  - Summary/Creative: 0.7-0.9 (创造性)
- 根据任务复杂度设置 `max_tokens`
  - QA: 100
  - Math: 300
  - Code: 500
  - Translation/Reasoning: 200-300
  - Summary/Creative: 150-400

## 预估运行时间

| 阶段 | 时间 |
|------|------|
| 单个测试用例 | 1-3 分钟 |
| 单个模型 (80 任务) | 1.5-4 小时 |
| 全部 4 个模型 | 5-16 小时 |

### 优化建议

1. **分批运行**: 先运行小模型验证流程
2. **并行执行**: 如果有多个 GPU，可以并行运行
3. **优先级排序**: 先运行简单任务（QA, Math）

## 文件位置

### 配置文件

- `data/experiments_5/config.py` - Python 配置
- `data/experiments_5/config.json` - JSON 元数据
- `data/experiments_5/test_cases.json` - 320 个测试用例
- `data/experiments_5/README.md` - 实验说明

### 脚本文件

- `scripts/setup_experiment_5.py` - 配置生成脚本 ✅
- `scripts/verify_test_cases_format.py` - 格式验证脚本 ✅
- `scripts/run_experiment_5.py` - 实验运行脚本 ⏳
- `scripts/analyze_experiments_5.py` - 结果分析脚本 ⏳

### 文档文件

- `docs/EXPERIMENT_5_CONFIGURATION_COMPLETE.md` - 详细配置报告
- `docs/EXPERIMENT_RUNNER_GUIDE.md` - 实验运行器指南
- `docs/TEST_CASES_READY.md` - 测试用例准备报告

## 验证结果

```
✅ 总测试用例数: 320
✅ 模型分布: 每个模型 80 个测试用例
✅ 任务类型分布: 8 种任务类型
✅ 格式验证: 无错误，无警告
✅ 必需字段: 全部存在
✅ 可选字段: 正确配置
✅ 多轮对话: 正确配置上下文保持
```

## 系统要求

### 硬件

- **显存**: 至少 8GB (对于 8B 模型)
- **内存**: 至少 16GB
- **磁盘空间**: 至少 10GB

### 软件

- **Ollama**: 0.13.2+ (服务运行中)
- **Python**: 3.8+ (推荐 3.10)
- **Conda 环境**: bartscore

### 模型

确保以下模型已下载：
```bash
ollama list
# 应该看到:
# qwen3:4b
# qwen3:8b
# deepseek-r1:8b
# gemma3:4b
```

## 下一步

1. ✅ **配置完成** - 所有测试用例已生成并验证
2. 🔄 **运行实验** - 使用 experiment_runner.py 运行实验
3. ⏳ **分析结果** - 创建分析脚本并生成报告
4. ⏳ **撰写论文** - 基于实验结果撰写论文

## 相关文档

- [EXPERIMENT_RUNNER_GUIDE.md](docs/EXPERIMENT_RUNNER_GUIDE.md) - 实验运行器完整指南
- [EXPERIMENT_5_CONFIGURATION_COMPLETE.md](docs/EXPERIMENT_5_CONFIGURATION_COMPLETE.md) - 详细配置报告
- [TEST_CASES_READY.md](docs/TEST_CASES_READY.md) - 测试用例准备报告

## 问题排查

如果遇到问题，请检查：

1. **Ollama 服务**: `ollama list` 确认服务运行
2. **模型下载**: 确认所有 4 个模型已下载
3. **Python 环境**: `conda activate bartscore`
4. **文件格式**: `python scripts/verify_test_cases_format.py`

## 联系与支持

如有问题，请参考：
- 实验运行器指南: `docs/EXPERIMENT_RUNNER_GUIDE.md`
- 故障排除: `TROUBLESHOOTING.md`
- 项目文档: `docs/README.md`

---

**配置完成时间**: 2026-03-02  
**状态**: ✅ 准备就绪  
**下一步**: 运行实验
