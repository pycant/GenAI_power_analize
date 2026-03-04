# 量化实验快速参考

**更新**: 2026-03-03 19:10

## 🎯 实验概览

- **总模型配置**: 12 个
- **量化对比组**: 4 组（每组 4-bit vs 8-bit）
- **总任务数**: 480 个
- **预计时间**: 15-18 小时

## 📊 模型配置列表

### Ollama 模型（4个）

| # | 模型 | 量化 | 显存 | 目录 |
|---|------|------|------|------|
| 1 | Gemma3 4B | Q4_K_M | 3.3GB | `gemma_4b_ol_q4km/` |
| 2 | Qwen3 4B | Q4_K_M | 2.5GB | `qwen_4b_ol_q4km/` |
| 3 | Qwen3 8B | Q4_K_M | 5.2GB | `qwen_8b_ol_q4km/` |
| 4 | DeepSeek-R1 8B | Q4_K_M | 5.2GB | `deepseek_8b_ol_q4km/` |

### HF 量化对比（8个配置 = 4组 × 2量化）

| # | 模型 | 4-bit 目录 | 8-bit 目录 |
|---|------|-----------|-----------|
| 5-6 | Gemma 2B | `gemma_2b_hf_4bit/` | `gemma_2b_hf_8bit/` |
| 7-8 | Phi-3 Mini 3.8B | `phi3_4b_hf_4bit/` | `phi3_4b_hf_8bit/` |
| 9-10 | Qwen 2.5 3B | `qwen25_3b_hf_4bit/` | `qwen25_3b_hf_8bit/` |
| 11-12 | Qwen 2.5 7B | `qwen25_7b_hf_4bit/` | `qwen25_7b_hf_8bit/` |

## 🚀 快速启动

### 运行所有实验

```bash
conda activate bartscore
scripts\run_all_experiments_complete.bat
```

### 运行单个量化对比组

```bash
# Gemma 2B (4-bit vs 8-bit)
python experiments/experiment_runner.py --config data/gemma_2b_hf_4bit/test_cases.json --output-dir data/gemma_2b_hf_4bit --skip-bartscore
python experiments/experiment_runner.py --config data/gemma_2b_hf_8bit/test_cases.json --output-dir data/gemma_2b_hf_8bit --skip-bartscore
```

## 📈 分析目标

### 核心问题

1. **质量损失**: 4-bit 相比 8-bit 损失多少？
2. **效率提升**: 4-bit 相比 8-bit 快多少？
3. **任务敏感性**: 哪些任务对量化更敏感？
4. **模型规模**: 大模型 vs 小模型的量化表现？

### 关键指标

```
质量损失率 = (质量_8bit - 质量_4bit) / 质量_8bit × 100%
效率提升率 = (吞吐_4bit - 吞吐_8bit) / 吞吐_8bit × 100%
质效比 = 质量得分 / (延迟 × 能耗)
```

## 📁 文件结构

```
data/
├── gemma_4b_ol_q4km/                    # Ollama: Gemma3 4B
├── qwen_4b_ol_q4km/                  # Ollama: Qwen3 4B
├── qwen_8b_ol_q4km/                  # Ollama: Qwen3 8B
├── deepseek_8b_ol_q4km/            # Ollama: DeepSeek-R1 8B
├── gemma_2b_hf_4bit/          # HF: Gemma 2B 4-bit
├── gemma_2b_hf_8bit/          # HF: Gemma 2B 8-bit
├── phi3_4b_hf_4bit/         # HF: Phi-3 Mini 4-bit
├── phi3_4b_hf_8bit/         # HF: Phi-3 Mini 8-bit
├── qwen25_3b_hf_4bit/         # HF: Qwen 2.5 3B 4-bit
├── qwen25_3b_hf_8bit/         # HF: Qwen 2.5 3B 8-bit
├── qwen25_7b_hf_4bit/         # HF: Qwen 2.5 7B 4-bit
└── qwen25_7b_hf_8bit/         # HF: Qwen 2.5 7B 8-bit
```

## 🔧 工具脚本

| 脚本 | 功能 |
|------|------|
| `scripts/split_gemma_configs.py` | 分离 Gemma 2B 量化配置 |
| `scripts/split_all_hf_quantization.py` | 分离所有 HF 模型量化配置 |
| `scripts/run_all_experiments_complete.bat` | 批量运行所有 15 个配置 |

## 📚 详细文档

- [量化实验完整说明](docs/QUANTIZATION_EXPERIMENTS_COMPLETE.md)
- [实验状态总览](EXPERIMENT_STATUS.md)
- [Gemma 量化配置](docs/GEMMA_QUANTIZATION_SPLIT.md)
- [批量实验指南](docs/EXPERIMENTS_BATCH_GUIDE.md)

## ⚠️ 注意事项

1. **显存要求**: 
   - 4-bit: 最低 3GB
   - 8-bit: 最低 5GB
   - 建议: 8GB 显存

2. **运行顺序**: 
   - 建议先运行小模型（2B-3B）
   - 再运行大模型（7B-8B）

3. **时间估算**:
   - 小模型（2B-3B）: ~1h/配置
   - 中模型（4B）: ~1.5h/配置
   - 大模型（7B-8B）: ~2h/配置

4. **Flash Attention 警告**:
   - 可以忽略，不影响实验
   - 所有模型环境一致，结果可比

## ✅ 检查清单

- [x] 所有 15 个配置文件已生成
- [x] 批处理脚本已更新
- [x] 文档已完善
- [ ] 开始运行实验
- [ ] 收集实验数据
- [ ] 分析量化效应
- [ ] 撰写论文章节

---

**状态**: ✅ 配置完成，随时可以开始实验！
