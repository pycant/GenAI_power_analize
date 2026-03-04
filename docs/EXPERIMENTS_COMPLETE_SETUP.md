# 完整实验配置报告

## 完成时间
2026-03-03

## 状态
✅ 所有 8 个模型的实验配置已生成并就绪

---

## 模型总览

### Ollama 模型 (4个)

| 模型 | 参数量 | 量化 | 显存 | 配置路径 |
|------|--------|------|------|----------|
| gemma3:4b | 4B | Q4_K_M | ~3.3GB | `data/experiments_gemma3/` |
| qwen3:4b | 4B | Q4_K_M | ~2.5GB | `data/experiments_qwen3_4b/` |
| qwen3:8b | 8B | Q4_K_M | ~5.2GB | `data/experiments_qwen3_8b/` |
| deepseek-r1:8b | 8B | Q4_K_M | ~5.2GB | `data/experiments_deepseek_r1_8b/` |

### HuggingFace 模型 (4个)

| 模型 | 参数量 | 量化 | 显存 | 配置路径 |
|------|--------|------|------|----------|
| Gemma 2B | 2B | FP16 | ~4GB | `data/experiments_gemma_2b_hf/` |
| Phi-3 Mini | 3.8B | 4-bit | ~2.5GB | `data/experiments_phi3_mini_hf/` |
| Qwen 2.5 3B | 3B | 4-bit | ~2GB | `data/experiments_qwen25_3b_hf/` |
| Qwen 2.5 7B | 7B | 4-bit | ~4.5GB | `data/experiments_qwen25_7b_hf/` |

---

## 配置详情

### 统一配置

所有 8 个模型使用相同的配置：
- **任务数量**: 40 个
- **随机种子**: 42（确保可复现）
- **任务分布**: 8 种类型，每种 5 个
- **语言分布**: 中文 20 + 英文 20
- **max_tokens**: 优化值（640-1200）

### 任务类型分布

| 任务类型 | 数量 | 占比 |
|---------|------|------|
| code | 5 | 12.5% |
| creative | 5 | 12.5% |
| math | 5 | 12.5% |
| multi_turn | 5 | 12.5% |
| qa | 5 | 12.5% |
| reasoning | 5 | 12.5% |
| summary | 5 | 12.5% |
| translation | 5 | 12.5% |

---

## 运行方式

### 方式 1: 完整批量运行（推荐）

运行所有 8 个模型：

```bash
scripts\run_all_experiments_complete.bat
```

**特点**:
- 自动依次运行 8 个模型
- 先运行 Ollama 模型（4个）
- 再运行 HuggingFace 模型（4个）
- 失败时自动停止
- 预计总时间: 8-12 小时

### 方式 2: 分批运行

#### 仅运行 Ollama 模型

```bash
scripts\run_all_experiments.bat
```

#### 仅运行 HuggingFace 模型

```bash
conda activate bartscore

# Gemma 2B HF
python experiments/experiment_runner.py \
  --config data/experiments_gemma_2b_hf/test_cases.json \
  --output-dir data/experiments_gemma_2b_hf \
  --skip-bartscore

# Phi-3 Mini HF
python experiments/experiment_runner.py \
  --config data/experiments_phi3_mini_hf/test_cases.json \
  --output-dir data/experiments_phi3_mini_hf \
  --skip-bartscore

# Qwen 2.5 3B HF
python experiments/experiment_runner.py \
  --config data/experiments_qwen25_3b_hf/test_cases.json \
  --output-dir data/experiments_qwen25_3b_hf \
  --skip-bartscore

# Qwen 2.5 7B HF
python experiments/experiment_runner.py \
  --config data/experiments_qwen25_7b_hf/test_cases.json \
  --output-dir data/experiments_qwen25_7b_hf \
  --skip-bartscore
```

---

## 模型对比分析

### 参数量对比

| 参数量 | Ollama 模型 | HF 模型 |
|--------|------------|---------|
| 2B | - | Gemma 2B |
| 3-4B | gemma3:4b, qwen3:4b | Phi-3 Mini (3.8B), Qwen 2.5 3B |
| 7-8B | qwen3:8b, deepseek-r1:8b | Qwen 2.5 7B |

### 量化对比

| 量化方式 | 模型数量 | 模型列表 |
|---------|---------|---------|
| Q4_K_M (Ollama) | 4 | gemma3:4b, qwen3:4b, qwen3:8b, deepseek-r1:8b |
| 4-bit (HF) | 3 | Phi-3 Mini, Qwen 2.5 3B, Qwen 2.5 7B |
| FP16 (HF) | 1 | Gemma 2B |

### 显存占用对比

| 显存范围 | 模型数量 | 模型列表 |
|---------|---------|---------|
| < 3GB | 2 | qwen3:4b (2.5GB), Qwen 2.5 3B HF (2GB) |
| 3-4GB | 2 | gemma3:4b (3.3GB), Gemma 2B HF (4GB) |
| 4-5GB | 2 | Phi-3 Mini HF (2.5GB), Qwen 2.5 7B HF (4.5GB) |
| > 5GB | 2 | qwen3:8b (5.2GB), deepseek-r1:8b (5.2GB) |

---

## 时间估算

### 单个模型

| 模型类型 | 平均时间 |
|---------|---------|
| Ollama 4B | 60-90 分钟 |
| Ollama 8B | 90-120 分钟 |
| HF 2-4B | 60-90 分钟 |
| HF 7B | 90-120 分钟 |

### 总时间

- **Ollama 模型 (4个)**: 4-6 小时
- **HF 模型 (4个)**: 4-6 小时
- **总计 (8个)**: 8-12 小时

---

## 实验前准备

### 1. 检查 Ollama

```bash
ollama list
```

应该看到：
- deepseek-r1:8b
- gemma3:4b
- qwen3:8b
- qwen3:4b

### 2. 检查 HuggingFace 模型

```bash
dir models\huggingface
```

应该看到：
- google--gemma-2b-it
- microsoft--phi-3-mini-4k-instruct
- Qwen--Qwen2.5-3B-Instruct
- Qwen--Qwen2.5-7B-Instruct

### 3. 清理 GPU 显存

```bash
python scripts/clear_gpu_memory.py
```

### 4. 激活环境

```bash
conda activate bartscore
```

---

## 预期输出

每个模型实验完成后生成：

```
data/experiments_<model>/
├── test_cases.json                                    # 配置文件
├── experiment_results_YYYYMMDD_HHMMSS_raw.json       # 原始结果
└── experiment_results_YYYYMMDD_HHMMSS_summary.json   # 汇总结果
```

### 总输出文件

- **8 个配置文件** (test_cases.json)
- **8 个原始结果文件** (raw.json)
- **8 个汇总结果文件** (summary.json)
- **总计**: 24 个文件

---

## 收集的指标

### 效率指标

- ✅ 吞吐量 (tokens/s)
- ✅ 延迟 (秒)
- ✅ GPU 能耗 (焦耳)
- ✅ GPU 显存使用 (MB)
- ✅ CPU 使用率 (%)
- ✅ 内存使用 (MB)

### 内容指标

- ✅ 生成文本完整内容
- ✅ 生成文本长度
- ✅ 对话历史（多轮任务）

### 质量指标

- ❌ BARTScore（已跳过）
- ℹ️ 可后续补充

---

## 对比分析维度

完成所有实验后，可以进行以下对比分析：

### 1. 框架对比

- **Ollama vs HuggingFace**: 推理速度、资源占用、易用性

### 2. 参数量对比

- **2B vs 3-4B vs 7-8B**: 性能提升 vs 资源消耗

### 3. 量化对比

- **Q4_K_M vs 4-bit vs FP16**: 质量损失 vs 效率提升

### 4. 模型系列对比

- **Gemma**: Ollama 4B vs HF 2B
- **Qwen**: Ollama 4B/8B vs HF 3B/7B

### 5. 任务类型对比

- 每个模型在 8 种任务类型上的表现

### 6. 语言对比

- 中文 vs 英文任务的性能差异

---

## 注意事项

### Ollama 模型

- ✅ 启动快速
- ✅ API 简单
- ✅ 自动管理显存
- ⚠️ 需要 Ollama 服务运行

### HuggingFace 模型

- ✅ 灵活配置
- ✅ 支持多种量化
- ✅ 直接访问模型
- ⚠️ 首次加载较慢
- ⚠️ 需要手动管理显存

### 显存管理

- Ollama 和 HF 模型不能同时运行
- 切换时需要清理显存
- 建议先运行 Ollama，再运行 HF

---

## 故障排除

### Ollama 模型失败

```bash
# 检查 Ollama 状态
curl http://localhost:11434/api/tags

# 重启 Ollama
taskkill /F /IM ollama.exe
ollama serve
```

### HuggingFace 模型失败

```bash
# 清理显存
python scripts/clear_gpu_memory.py

# 检查模型文件
dir models\huggingface\<model-name>
```

### 显存不足

```bash
# 停止 Ollama
python scripts/clear_gpu_memory.py --ollama-only

# 清理 PyTorch 缓存
python -c "import torch; torch.cuda.empty_cache()"
```

---

## 下一步

### 1. 运行实验

```bash
# 完整批量运行
scripts\run_all_experiments_complete.bat

# 或分批运行
scripts\run_all_experiments.bat  # Ollama only
```

### 2. 验证结果

```bash
# 检查所有结果文件
dir data\experiments_*\experiment_results_*.json
```

### 3. 数据分析

- 加载所有结果文件
- 生成对比图表
- 计算质效比
- 撰写分析报告

---

## 相关文档

- [批量实验指南](EXPERIMENTS_BATCH_GUIDE.md)
- [实验就绪报告](EXPERIMENTS_READY.md)
- [实验运行器指南](EXPERIMENT_RUNNER_GUIDE.md)
- [配置参数参考](CONFIG_PARAMETERS_REFERENCE.md)

---

## 配置文件清单

### Ollama 模型

1. `data/experiments_gemma3/test_cases.json`
2. `data/experiments_qwen3_4b/test_cases.json`
3. `data/experiments_qwen3_8b/test_cases.json`
4. `data/experiments_deepseek_r1_8b/test_cases.json`

### HuggingFace 模型

5. `data/experiments_gemma_2b_hf/test_cases.json`
6. `data/experiments_phi3_mini_hf/test_cases.json`
7. `data/experiments_qwen25_3b_hf/test_cases.json`
8. `data/experiments_qwen25_7b_hf/test_cases.json`

---

**创建日期**: 2026-03-03  
**状态**: ✅ 完全就绪  
**模型数量**: 8 个  
**总任务数**: 320 个 (8 × 40)  
**预计时间**: 8-12 小时

**开始命令**:
```bash
scripts\run_all_experiments_complete.bat
```
