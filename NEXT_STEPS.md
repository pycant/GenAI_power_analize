# 下一步行动指南

## 当前状态 ✅

### 已完成
1. ✅ NumPy 兼容性问题已修复（降级到 1.26.4）
2. ✅ HuggingFace 下载脚本正常工作
3. ✅ 已下载 3 个 HuggingFace 模型（共 27 GB）
4. ✅ 已有 4 个 Ollama 模型可用（共 16 GB）
5. ✅ 快速测试验证系统功能正常

### 可用模型总览
- **3-4B 模型**: 4 个（Qwen2.5-3B, phi-3-mini-3.8B, qwen3:4b, gemma3:4b）
- **7-8B 模型**: 3 个（Qwen2.5-7B, qwen3:8b, deepseek-r1:8b）
- **总计**: 7 个模型，覆盖小型和中型规模

## 推荐行动路径

### 路径 A：立即开始实验（推荐）⭐

使用现有的 7 个模型开始实验，验证完整的实验流程。

#### 步骤 1：准备测试用例
```bash
# 检查现有测试用例
cat data/test/test_cases.json

# 或创建新的实验测试用例
# 参考：docs/experiment/experiment_design.md
```

#### 步骤 2：运行小规模实验
```bash
# 使用 Ollama 模型快速测试（推荐先用小模型）
python experiments/experiment_runner.py \
  --model "Ollama:qwen3:4b" \
  --test-cases data/test/test_cases.json \
  --output-dir data/experiments_5

# 或使用 HuggingFace 模型
python experiments/experiment_runner.py \
  --model "HF:Qwen/Qwen2.5-3B-Instruct" \
  --test-cases data/test/test_cases.json \
  --output-dir data/experiments_5
```

#### 步骤 3：分析结果
```bash
# 查看生成的结果
cat data/experiments_5/experiment_results_summary_*.json

# 运行分析脚本（如果有）
python scripts/analyze_experiments.py --experiment-dir data/experiments_5
```

### 路径 B：扩展模型库

如果需要更多模型进行对比实验。

#### 选项 B1：下载更多 HuggingFace 模型
```bash
# 下载 Google Gemma 2B（约 4-5 GB）
python scripts/download_hf_model.py \
  --model-name google/gemma-2b-it \
  --quantize 4bit

# 下载 Mistral 7B（约 14 GB）
python scripts/download_hf_model.py \
  --model-name mistralai/Mistral-7B-Instruct-v0.3 \
  --quantize 4bit
```

#### 选项 B2：下载更多 Ollama 模型
```bash
# 小型模型
ollama pull phi3.5:3.8b      # ~2.3 GB
ollama pull smollm3:3b        # ~1.8 GB

# 中型模型
ollama pull mistral:7b        # ~4.2 GB
ollama pull llama3.1:8b       # ~4.8 GB
ollama pull glm4:9b           # ~5.4 GB
```

### 路径 C：完善实验设计

在大规模实验前，完善测试用例和评估指标。

#### 步骤 1：设计测试用例
根据 `docs/experiment/experiment_design.md` 创建完整的测试用例集：
- 知识问答（15-20 题）
- 数学计算（10-15 题）
- 代码生成（10-12 题）
- 逻辑推理（8-10 题）
- 文本摘要（5-8 题）
- 创意写作（5-8 题）
- 多轮对话（5-8 组）
- 上下文检验（8-10 题）

#### 步骤 2：配置实验参数
编辑 `experiments/config.py` 设置：
- 生成参数（温度、max_tokens）
- 监控参数（采样率、空闲基线时间）
- 评估指标权重

#### 步骤 3：准备评估工具
确保以下评估工具可用：
- BARTScore（文本质量评估）
- ROUGE（摘要质量）
- Distinct-N（创意多样性）
- 代码编译器（代码质量）

## 快速命令参考

### 检查系统状态
```bash
# 检查 NumPy 版本
python -c "import numpy; print('NumPy:', numpy.__version__)"

# 检查 GPU 状态
nvidia-smi

# 检查 Ollama 服务
ollama list

# 检查已下载的 HF 模型
cat models/model_registry.json
```

### 运行测试
```bash
# 快速功能测试
python scripts/quick_test_refactoring.py

# 测试 Ollama 连接
python scripts/test_ollama_runner.py

# 测试 HuggingFace 模型加载
python scripts/check_hf_model.py
```

### 清理和维护
```bash
# 清理 Python 缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 检查磁盘空间
du -sh models/huggingface/*
du -sh ~/.ollama/models/*
```

## 实验建议

### 阶段 1：基线实验（1-2 小时）
- 选择 2-3 个模型（如 qwen3:4b, qwen3:8b, phi-3-mini）
- 运行 10-20 个简单测试用例
- 验证数据收集和分析流程

### 阶段 2：量化对比（2-3 小时）
- 选择 1 个模型
- 测试不同量化级别（Q4, Q8, FP16）
- 评估质量-效率权衡

### 阶段 3：全面评估（10-20 小时）
- 使用所有 7 个模型
- 运行完整测试用例集（80-100 题）
- 生成综合分析报告

## 注意事项

### 硬件限制
- **VRAM**: 8GB 限制，7-8B 模型只能用 Q4 量化
- **存储**: 已用 ~43GB，建议预留 60-100GB
- **散热**: 长时间实验注意笔记本散热

### 实验控制
- 每次实验前测量空闲基线功耗
- 任务间间隔 30 秒冷却
- 模型间间隔 5 分钟冷却
- 关闭后台应用减少干扰

### 数据管理
- 每个实验创建独立目录（experiments_N）
- 保留原始数据（raw）和汇总数据（summary）
- 定期备份重要结果

## 相关文档

- [实验设计文档](docs/experiment/experiment_design.md) - 完整实验方法论
- [实验操作指南](docs/experiment/experiment_operation_guide.md) - 操作步骤
- [NumPy 修复总结](docs/NUMPY_FIX_AND_MODEL_DOWNLOAD_SUMMARY.md) - 问题解决记录
- [快速开始指南](docs/QUICK_START_NEW_FORMAT.md) - 新格式快速入门
- [AGENTS 指南](agents.md) - 项目环境和结构

## 获取帮助

如遇到问题，检查以下文档：
- [故障排查](TROUBLESHOOTING.md)
- [测试结果](docs/TEST_RESULTS.md)
- [重构总结](REFACTORING_SUMMARY.md)

## 总结

✅ **系统已就绪**，可以开始实验！

推荐从**路径 A**开始，使用现有模型运行小规模实验，验证整个流程后再扩展到大规模评估。

祝实验顺利！🚀
