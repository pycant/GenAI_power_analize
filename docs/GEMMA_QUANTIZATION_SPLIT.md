# Gemma 2B 量化配置分离说明

## 概述

为了比较不同量化级别对模型性能和效率的影响，我们将 Gemma 2B HuggingFace 模型的实验配置分成了两份：
- **4-bit 量化**: 更小的显存占用，更快的推理速度
- **8-bit 量化**: 更高的模型质量，适中的资源消耗

## 配置详情

### 1. Gemma 2B 4-bit 量化

**目录**: `data/gemma_2b_hf_4bit/`

**模型标识**: `hf:models/huggingface/google--gemma-2b-it:4bit`

**特点**:
- 显存占用: ~2-3 GB
- 推理速度: 较快
- 质量: 略有损失但可接受

**运行命令**:
```bash
conda activate bartscore
python experiments/experiment_runner.py \
  --config data/gemma_2b_hf_4bit/test_cases.json \
  --output-dir data/gemma_2b_hf_4bit \
  --skip-bartscore
```

### 2. Gemma 2B 8-bit 量化

**目录**: `data/gemma_2b_hf_8bit/`

**模型标识**: `hf:models/huggingface/google--gemma-2b-it:8bit`

**特点**:
- 显存占用: ~4-5 GB
- 推理速度: 适中
- 质量: 更接近原始模型

**运行命令**:
```bash
conda activate bartscore
python experiments/experiment_runner.py \
  --config data/gemma_2b_hf_8bit/test_cases.json \
  --output-dir data/gemma_2b_hf_8bit \
  --skip-bartscore
```

## 测试用例统计

每个配置包含 **40 个测试用例**，均衡分布在 8 个任务类型：

| 任务类型 | 数量 | 说明 |
|---------|------|------|
| code | 5 | Python 代码生成 |
| creative | 5 | 创意写作（中文） |
| math | 5 | 数学问题求解 |
| multi_turn | 5 | 多轮对话 |
| qa | 5 | 问答任务 |
| reasoning | 5 | 逻辑推理 |
| summary | 5 | 文本摘要 |
| translation | 5 | 跨语言翻译 |

## 批量运行

使用更新后的批处理脚本可以一次性运行所有 9 个模型（包括两个 Gemma 2B 配置）：

```bash
scripts\run_all_experiments_complete.bat
```

**总模型数**: 9 个
- Ollama 模型: 4 个
- HuggingFace 模型: 5 个（包括 Gemma 2B 的两个量化版本）

**预计总时间**: 9-13 小时

## 实验目标

通过对比 4-bit 和 8-bit 量化版本，我们可以分析：

1. **质量-效率权衡**
   - 量化对不同任务类型的影响
   - 质量损失 vs 效率提升的比例

2. **资源消耗对比**
   - GPU 显存占用差异
   - 能耗差异
   - 推理速度差异

3. **任务敏感性**
   - 哪些任务对量化更敏感
   - 哪些任务可以使用更激进的量化

4. **语言公平性**
   - 量化对中英文任务的影响是否一致
   - 跨语言任务的质量保持情况

## 分析建议

在实验完成后，建议进行以下分析：

1. **量化效率曲线**: 绘制质量 vs 量化级别的曲线
2. **任务敏感性热图**: 展示不同任务对量化的敏感程度
3. **能效比对比**: 计算两个版本的质效比差异
4. **最优量化推荐**: 基于任务类型推荐最优量化级别

## 文件结构

```
data/
├── gemma_2b_hf_4bit/
│   ├── test_cases.json                    # 4-bit 配置
│   ├── experiment_results_*_raw.json      # 原始结果（运行后生成）
│   └── experiment_results_*_summary.json  # 汇总结果（运行后生成）
│
└── gemma_2b_hf_8bit/
    ├── test_cases.json                    # 8-bit 配置
    ├── experiment_results_*_raw.json      # 原始结果（运行后生成）
    └── experiment_results_*_summary.json  # 汇总结果（运行后生成）
```

## 相关脚本

- **配置生成**: `scripts/split_gemma_configs.py`
- **批量运行**: `scripts/run_all_experiments_complete.bat`
- **实验执行**: `experiments/experiment_runner.py`

## 注意事项

1. **显存要求**: 
   - 4-bit: 至少 3GB 可用显存
   - 8-bit: 至少 5GB 可用显存

2. **运行顺序**: 建议先运行 4-bit 版本，确认系统稳定后再运行 8-bit

3. **结果对比**: 两个版本使用相同的测试用例和随机种子（42），确保可比性

4. **BARTScore**: 当前配置使用 `--skip-bartscore` 跳过质量评估，仅收集效率指标

## 更新日期

2026-03-03

## 相关文档

- [实验设置完整指南](EXPERIMENTS_COMPLETE_SETUP.md)
- [批量实验指南](EXPERIMENTS_BATCH_GUIDE.md)
- [Ollama 量化指南](OLLAMA_QUANTIZATION_GUIDE.md)
