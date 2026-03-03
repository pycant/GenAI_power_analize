# 实验配置总览

## 🎯 项目状态

✅ **所有实验配置已完成并就绪**

- **模型总数**: 8 个
- **任务总数**: 320 个 (8 × 40)
- **预计时间**: 8-12 小时
- **配置日期**: 2026-03-03

---

## 📊 模型列表

### Ollama 模型 (4个)

| # | 模型 | 参数 | 量化 | 显存 | 配置目录 |
|---|------|------|------|------|----------|
| 1 | gemma3:4b | 4B | Q4_K_M | 3.3GB | `data/gemma_4b_ol_q4km/` |
| 2 | qwen3:4b | 4B | Q4_K_M | 2.5GB | `data/qwen_4b_ol_q4km/` |
| 3 | qwen3:8b | 8B | Q4_K_M | 5.2GB | `data/qwen_8b_ol_q4km/` |
| 4 | deepseek-r1:8b | 8B | Q4_K_M | 5.2GB | `data/deepseek_8b_ol_q4km/` |

### HuggingFace 模型 (4个)

| # | 模型 | 参数 | 量化 | 显存 | 配置目录 |
|---|------|------|------|------|----------|
| 5 | Gemma 2B | 2B | FP16 | 4GB | `data/experiments_gemma_2b_hf/` |
| 6 | Phi-3 Mini | 3.8B | 4-bit | 2.5GB | `data/experiments_phi3_mini_hf/` |
| 7 | Qwen 2.5 3B | 3B | 4-bit | 2GB | `data/experiments_qwen25_3b_hf/` |
| 8 | Qwen 2.5 7B | 7B | 4-bit | 4.5GB | `data/experiments_qwen25_7b_hf/` |

---

## 🚀 快速开始

### 运行所有实验

```bash
# 完整批量运行（8个模型）
scripts\run_all_experiments_complete.bat

# 或仅运行 Ollama 模型（4个）
scripts\run_all_experiments.bat
```

### 运行单个模型

```bash
conda activate bartscore

# 示例：运行 Gemma3 4B
python experiments/experiment_runner.py \
  --config data/gemma_4b_ol_q4km/test_cases.json \
  --output-dir data/gemma_4b_ol_q4km \
  --skip-bartscore
```

---

## 📋 任务配置

每个模型包含 **40 个任务**，分布如下：

| 任务类型 | 数量 | 说明 |
|---------|------|------|
| code | 5 | Python 代码生成 |
| creative | 5 | 创意写作 |
| math | 5 | 数学推理 |
| multi_turn | 5 | 多轮对话 |
| qa | 5 | 问答任务 |
| reasoning | 5 | 逻辑推理 |
| summary | 5 | 文本摘要 |
| translation | 5 | 跨语言翻译 |

**语言分布**:
- 中文: 20 个任务
- 英文: 20 个任务

---

## ⚙️ 配置特点

### 统一配置

- **随机种子**: 42（确保可复现）
- **任务选择**: 所有模型使用相同的 40 个任务
- **max_tokens**: 优化值（640-1200，根据任务类型）
- **跳过 BARTScore**: 使用 `--skip-bartscore` 避免网络超时

### 优化的 max_tokens

| 任务类型 | Easy | Medium | Hard |
|---------|------|--------|------|
| code | 640 | 800 | 1200 |
| creative | 400 | 500 | 750 |
| math | 320 | 400 | 600 |
| reasoning | 320 | 400 | 600 |
| 其他 | 160-240 | 200-300 | 300-450 |

---

## 📈 收集的指标

### 效率指标

- ✅ 吞吐量 (tokens/s)
- ✅ 延迟 (秒)
- ✅ GPU 能耗 (焦耳)
- ✅ GPU 显存使用
- ✅ CPU/内存使用

### 内容指标

- ✅ 生成文本完整内容
- ✅ 生成文本长度
- ✅ 对话历史

### 质量指标

- ❌ BARTScore（已跳过，可后续补充）

---

## ⏱️ 时间估算

| 阶段 | 时间 |
|------|------|
| Ollama 模型 (4个) | 4-6 小时 |
| HF 模型 (4个) | 4-6 小时 |
| **总计** | **8-12 小时** |

---

## 📁 输出结构

每个模型实验完成后生成：

```
data/experiments_<model>/
├── test_cases.json                          # 配置文件
├── experiment_results_*_raw.json           # 原始结果
└── experiment_results_*_summary.json       # 汇总结果
```

---

## 🔍 对比分析维度

完成所有实验后，可以进行：

1. **框架对比**: Ollama vs HuggingFace
2. **参数量对比**: 2B vs 3-4B vs 7-8B
3. **量化对比**: Q4_K_M vs 4-bit vs FP16
4. **模型系列对比**: Gemma, Qwen, Phi-3, DeepSeek
5. **任务类型对比**: 8 种任务的性能差异
6. **语言对比**: 中文 vs 英文

---

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| [EXPERIMENTS_COMPLETE_SETUP.md](docs/EXPERIMENTS_COMPLETE_SETUP.md) | 完整配置报告 |
| [EXPERIMENTS_BATCH_GUIDE.md](docs/EXPERIMENTS_BATCH_GUIDE.md) | 批量运行指南 |
| [EXPERIMENTS_READY.md](docs/EXPERIMENTS_READY.md) | Ollama 模型就绪报告 |
| [EXPERIMENT_RUNNER_GUIDE.md](docs/EXPERIMENT_RUNNER_GUIDE.md) | 运行器使用说明 |
| [CONFIG_PARAMETERS_REFERENCE.md](docs/CONFIG_PARAMETERS_REFERENCE.md) | 参数参考 |

---

## 🛠️ 工具脚本

| 脚本 | 功能 |
|------|------|
| `scripts/run_all_experiments_complete.bat` | 运行所有 8 个模型 |
| `scripts/run_all_experiments.bat` | 运行 Ollama 模型 |
| `scripts/clear_gpu_memory.py` | 清理 GPU 显存 |
| `scripts/create_experiment_config.py` | 生成实验配置 |

---

## ✅ 实验前检查

- [ ] Ollama 服务运行中
- [ ] HuggingFace 模型已下载
- [ ] GPU 显存已清理
- [ ] Conda 环境已激活
- [ ] 磁盘空间充足（至少 500 MB）
- [ ] 系统保持唤醒
- [ ] 笔记本已插电

---

## 🎯 开始实验

```bash
# 1. 激活环境
conda activate bartscore

# 2. 清理显存
python scripts/clear_gpu_memory.py

# 3. 运行实验
scripts\run_all_experiments_complete.bat
```

---

## 📊 预期成果

完成所有实验后，将获得：

- **8 个模型**的完整性能数据
- **320 个任务**的执行结果
- **效率指标**的横向对比
- **质效比分析**的基础数据
- **多维度评估**的完整报告

---

**创建日期**: 2026-03-03  
**状态**: ✅ 完全就绪  
**下一步**: 运行实验

```bash
scripts\run_all_experiments_complete.bat
```
