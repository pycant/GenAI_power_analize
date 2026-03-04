# 实验状态总览

**更新时间**: 2026-03-03 18:55

## 当前状态

### ✅ 已完成实验 (1/9)

| 模型 | 状态 | 完成时间 | 任务数 | 结果位置 |
|------|------|---------|--------|---------|
| Gemma3 4B (Ollama) | ✅ 完成 | 17:16:30 | 40/40 | `data/gemma_4b_ol_q4km/` |

### ⏳ 待运行实验 (11/12)

#### Ollama 模型 (3个)

| # | 模型 | 参数量 | 量化 | 显存需求 | 预计时间 |
|---|------|--------|------|---------|---------|
| 2 | DeepSeek-R1 8B | 8B | Q4_K_M | ~5.2GB | 1.5h |
| 3 | Qwen3 4B | 4B | Q4_K_M | ~2.5GB | 1h |
| 4 | Qwen3 8B | 8B | Q4_K_M | ~5.2GB | 1.5h |

#### HuggingFace 模型 - 量化对比 (8个)

| # | 模型 | 参数量 | 量化 | 显存需求 | 预计时间 |
|---|------|--------|------|---------|---------|
| 5 | Gemma 2B (4-bit) | 2B | 4-bit | ~2-3GB | 1h |
| 6 | Gemma 2B (8-bit) | 2B | 8-bit | ~4-5GB | 1.5h |
| 7 | Phi-3 Mini (4-bit) | 3.8B | 4-bit | ~3-4GB | 1.5h |
| 8 | Phi-3 Mini (8-bit) | 3.8B | 8-bit | ~5-6GB | 2h |
| 9 | Qwen 2.5 3B (4-bit) | 3B | 4-bit | ~2-3GB | 1h |
| 10 | Qwen 2.5 3B (8-bit) | 3B | 8-bit | ~4-5GB | 1.5h |
| 11 | Qwen 2.5 7B (4-bit) | 7B | 4-bit | ~5-6GB | 2h |
| 12 | Qwen 2.5 7B (8-bit) | 7B | 8-bit | ~7-8GB | 2.5h |

**预计剩余总时间**: 15-18 小时

## 实验配置

### 测试用例分布

每个模型 40 个测试用例，均衡分布：

| 任务类型 | 数量 | 语言 | 说明 |
|---------|------|------|------|
| code | 5 | EN | Python 代码生成 |
| creative | 5 | ZH | 创意写作 |
| math | 5 | EN | 数学问题求解 |
| multi_turn | 5 | ZH | 多轮对话 |
| qa | 5 | EN | 问答任务 |
| reasoning | 5 | ZH | 逻辑推理 |
| summary | 5 | ZH | 文本摘要 |
| translation | 5 | EN↔ZH | 跨语言翻译 |

**总任务数**: 480 (12 模型配置 × 40 任务)

### 语言分布

- **中文任务**: 20 个/模型
- **英文任务**: 20 个/模型
- **跨语言任务**: 5 个/模型（包含在上述统计中）

## 快速开始

### 运行所有剩余实验

```bash
conda activate bartscore
scripts\run_all_experiments_complete.bat
```

### 运行单个模型

```bash
conda activate bartscore

# Ollama 模型示例
python experiments/experiment_runner.py \
  --config data/qwen_4b_ol_q4km/test_cases.json \
  --output-dir data/qwen_4b_ol_q4km \
  --skip-bartscore

# HuggingFace 模型示例
python experiments/experiment_runner.py \
  --config data/gemma_2b_hf_4bit/test_cases.json \
  --output-dir data/gemma_2b_hf_4bit \
  --skip-bartscore
```

## 系统要求

### 硬件

- **GPU**: NVIDIA RTX 4060 8GB
- **CPU**: Intel i7-13700H (14核20线程)
- **内存**: 16GB
- **存储**: 至少 20GB 可用空间

### 软件

- **OS**: Windows
- **CUDA**: 12.6
- **Python**: 3.10 (conda 环境: bartscore)
- **Ollama**: 0.13.2

### 依赖包

```bash
pip install pandas numpy matplotlib seaborn tabulate torch transformers
```

## 实验特点

### 新增功能

1. **Gemma 2B 量化对比**: 首次对比 4-bit vs 8-bit 量化效果
2. **语言公平性**: 中英文任务均衡分布，支持公平性分析
3. **多维度评估**: 质量、效率、能耗、延迟全面监控
4. **跳过 BARTScore**: 使用 `--skip-bartscore` 避免网络超时

### 评估指标

#### 效率指标
- **吞吐量**: tokens/s
- **延迟**: 首 token 时间、平均延迟
- **GPU 能耗**: 焦耳 (J)
- **GPU 利用率**: 百分比
- **显存占用**: MB

#### 质量指标（后续分析）
- **代码任务**: 编译通过率
- **创意任务**: Distinct-2
- **QA/摘要**: BARTScore（可选）
- **翻译**: BLEU/COMET（可选）

## 数据输出

### 每个实验生成

```
data/experiments_<model_name>/
├── test_cases.json                    # 配置文件
├── experiment_results_*_raw.json      # 原始详细结果
└── experiment_results_*_summary.json  # 汇总统计结果
```

### 结果字段

**Raw JSON** 包含:
- 完整对话历史
- 逐秒监控数据（CPU、GPU、内存）
- 事件时间戳（首 token、推理结束等）
- 基线测量数据

**Summary JSON** 包含:
- 性能指标（吞吐、延迟、token 数）
- 资源指标（CPU、GPU、内存、能耗）
- 派生指标（PPW、TPJ、增量能耗）
- 质量指标（文本长度、BARTScore 等）

## 分析计划

### 实验完成后

1. **创建统一分析脚本**: 适配新的 JSON 格式
2. **生成对比报告**: 9 个模型的横向对比
3. **量化效果分析**: Gemma 2B 4-bit vs 8-bit
4. **语言公平性分析**: 中英文任务表现差异
5. **质效比排名**: 综合质量和效率的最优模型

### 可视化输出

- 吞吐量 vs 延迟散点图
- 能耗 vs 质量散点图
- 质效比柱状图（按任务类型）
- 量化效果对比图
- 语言公平性热图
- 综合能力雷达图

## 相关文档

- [Gemma 量化配置说明](docs/GEMMA_QUANTIZATION_SPLIT.md)
- [实验完整设置指南](docs/EXPERIMENTS_COMPLETE_SETUP.md)
- [批量实验指南](docs/EXPERIMENTS_BATCH_GUIDE.md)
- [实验执行器指南](docs/EXPERIMENT_RUNNER_GUIDE.md)
- [README 实验概览](README_EXPERIMENTS.md)

## 故障排除

### 常见问题

1. **显存不足**: 
   - 关闭其他 GPU 应用
   - 使用 `scripts/clear_gpu_memory.py` 清理显存
   - 优先运行小模型（Qwen3 4B, Gemma 2B 4-bit）

2. **BARTScore 超时**:
   - 已使用 `--skip-bartscore` 跳过
   - 如需质量评估，可后续离线运行

3. **Ollama 连接失败**:
   - 确认 Ollama 服务运行: `ollama list`
   - 重启服务: `ollama serve`

4. **HuggingFace 模型加载慢**:
   - 模型已下载到 `models/huggingface/`
   - 首次加载需要初始化，约 1-2 分钟

## 下一步

1. ✅ **配置完成**: 所有 9 个模型配置已就绪
2. ⏳ **运行实验**: 执行 `run_all_experiments_complete.bat`
3. ⏳ **数据收集**: 等待 10-12 小时完成所有实验
4. ⏳ **结果分析**: 创建分析脚本并生成报告
5. ⏳ **论文撰写**: 基于分析结果完善论文

---

**准备就绪！** 可以开始运行批量实验了。
