# 量化对比实验完整配置

**更新时间**: 2026-03-03 19:10

## 概述

为了系统性地研究量化对模型性能和效率的影响，我们为所有 4 个 HuggingFace 模型创建了 4-bit 和 8-bit 两个量化版本，总计 **12 个模型配置**。

## 实验设计

### 量化级别对比

| 量化级别 | 精度 | 显存占用 | 推理速度 | 质量损失 |
|---------|------|---------|---------|---------|
| 4-bit | INT4 | 最低 (~25%) | 最快 | 中等 (5-10%) |
| 8-bit | INT8 | 中等 (~50%) | 较快 | 较小 (2-5%) |
| FP16 | Float16 | 高 (100%) | 基准 | 无 (基准) |

### 模型配置矩阵

#### Ollama 模型 (4个) - 固定 Q4_K_M 量化

| 模型 | 参数量 | 量化 | 显存 | 配置目录 |
|------|--------|------|------|---------|
| Gemma3 | 4B | Q4_K_M | ~3.3GB | `gemma_4b_ol_q4km/` |
| Qwen3 | 4B | Q4_K_M | ~2.5GB | `qwen_4b_ol_q4km/` |
| Qwen3 | 8B | Q4_K_M | ~5.2GB | `qwen_8b_ol_q4km/` |
| DeepSeek-R1 | 8B | Q4_K_M | ~5.2GB | `deepseek_8b_ol_q4km/` |

#### HuggingFace 模型 (11个) - 4-bit vs 8-bit 对比

| 模型 | 参数量 | 4-bit 配置 | 8-bit 配置 |
|------|--------|-----------|-----------|
| **Gemma 2B** | 2B | `gemma_2b_hf_4bit/` | `gemma_2b_hf_8bit/` |
| **Phi-3 Mini** | 3.8B | `phi3_4b_hf_4bit/` | `phi3_4b_hf_8bit/` |
| **Qwen 2.5 3B** | 3B | `qwen25_3b_hf_4bit/` | `qwen25_3b_hf_8bit/` |
| **Qwen 2.5 7B** | 7B | `qwen25_7b_hf_4bit/` | `qwen25_7b_hf_8bit/` |

**总计**: 12 个模型配置 (4 Ollama + 8 HF 量化对比)

## 实验规模

### 任务分布

每个模型配置 40 个测试用例：

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

### 总体规模

- **模型配置数**: 12 个
- **每配置任务数**: 40 个
- **总任务数**: 480 个
- **预计总时间**: 15-18 小时
- **数据量**: 约 2-3 GB（JSON 结果）

## 量化对比分析目标

### 1. 质量-效率权衡曲线

**研究问题**:
- 4-bit 量化相比 8-bit 损失多少质量？
- 效率提升是否值得质量损失？
- 不同模型大小的量化敏感度如何？

**分析方法**:
```
质效比 = 质量得分 / (延迟 × 能耗)
量化效率增益 = (效率_4bit - 效率_8bit) / 效率_8bit
量化质量损失 = (质量_8bit - 质量_4bit) / 质量_8bit
```

### 2. 任务类型敏感性

**研究问题**:
- 哪些任务对量化更敏感？
- 代码生成 vs 创意写作的量化影响差异？
- 推理任务是否需要更高精度？

**分析维度**:
- 按任务类型分组对比
- 质量损失热图
- 任务-量化交互效应

### 3. 模型规模效应

**研究问题**:
- 大模型（7B）vs 小模型（2B）的量化表现？
- 参数量与量化鲁棒性的关系？
- 最优量化策略是否与模型大小相关？

**对比组**:
- Gemma 2B (4-bit vs 8-bit)
- Qwen 2.5 3B (4-bit vs 8-bit)
- Qwen 2.5 7B (4-bit vs 8-bit)
- Phi-3 Mini 3.8B (4-bit vs 8-bit)

### 4. 语言公平性

**研究问题**:
- 量化对中英文任务的影响是否一致？
- 跨语言任务的量化敏感度？
- 是否存在语言偏见放大效应？

**分析指标**:
- 中文任务质量损失率
- 英文任务质量损失率
- 跨语言任务质量损失率
- 公平性差距（Fairness Gap）

## 预期发现

### 假设 1: 小模型更敏感
**预测**: 2B-3B 模型的量化质量损失 > 7B-8B 模型

**原因**: 小模型参数冗余度低，量化影响更显著

### 假设 2: 推理任务更敏感
**预测**: reasoning 和 math 任务的量化损失 > creative 和 summary

**原因**: 逻辑推理需要更高的数值精度

### 假设 3: 4-bit 性价比更高
**预测**: 4-bit 的质效比 > 8-bit（对大多数任务）

**原因**: 效率提升（2x）超过质量损失（<10%）

### 假设 4: 语言公平性下降
**预测**: 量化会放大中英文性能差距

**原因**: 量化可能对低资源语言影响更大

## 运行指南

### 批量运行所有实验

```bash
conda activate bartscore
scripts\run_all_experiments_complete.bat
```

### 按模型类型运行

```bash
# 只运行 Ollama 模型（4个）
python experiments/experiment_runner.py --config data/gemma_4b_ol_q4km/test_cases.json --output-dir data/gemma_4b_ol_q4km --skip-bartscore
python experiments/experiment_runner.py --config data/qwen_4b_ol_q4km/test_cases.json --output-dir data/qwen_4b_ol_q4km --skip-bartscore
python experiments/experiment_runner.py --config data/qwen_8b_ol_q4km/test_cases.json --output-dir data/qwen_8b_ol_q4km --skip-bartscore
python experiments/experiment_runner.py --config data/deepseek_8b_ol_q4km/test_cases.json --output-dir data/deepseek_8b_ol_q4km --skip-bartscore

# 只运行 HF 4-bit 模型（4个）
python experiments/experiment_runner.py --config data/gemma_2b_hf_4bit/test_cases.json --output-dir data/gemma_2b_hf_4bit --skip-bartscore
python experiments/experiment_runner.py --config data/phi3_4b_hf_4bit/test_cases.json --output-dir data/phi3_4b_hf_4bit --skip-bartscore
python experiments/experiment_runner.py --config data/qwen25_3b_hf_4bit/test_cases.json --output-dir data/qwen25_3b_hf_4bit --skip-bartscore
python experiments/experiment_runner.py --config data/qwen25_7b_hf_4bit/test_cases.json --output-dir data/qwen25_7b_hf_4bit --skip-bartscore

# 只运行 HF 8-bit 模型（4个）
python experiments/experiment_runner.py --config data/gemma_2b_hf_8bit/test_cases.json --output-dir data/gemma_2b_hf_8bit --skip-bartscore
python experiments/experiment_runner.py --config data/phi3_4b_hf_8bit/test_cases.json --output-dir data/phi3_4b_hf_8bit --skip-bartscore
python experiments/experiment_runner.py --config data/qwen25_3b_hf_8bit/test_cases.json --output-dir data/qwen25_3b_hf_8bit --skip-bartscore
python experiments/experiment_runner.py --config data/qwen25_7b_hf_8bit/test_cases.json --output-dir data/qwen25_7b_hf_8bit --skip-bartscore
```

### 按量化对比组运行

```bash
# Gemma 2B 量化对比
python experiments/experiment_runner.py --config data/gemma_2b_hf_4bit/test_cases.json --output-dir data/gemma_2b_hf_4bit --skip-bartscore
python experiments/experiment_runner.py --config data/gemma_2b_hf_8bit/test_cases.json --output-dir data/gemma_2b_hf_8bit --skip-bartscore

# Phi-3 Mini 量化对比
python experiments/experiment_runner.py --config data/phi3_4b_hf_4bit/test_cases.json --output-dir data/phi3_4b_hf_4bit --skip-bartscore
python experiments/experiment_runner.py --config data/phi3_4b_hf_8bit/test_cases.json --output-dir data/phi3_4b_hf_8bit --skip-bartscore

# Qwen 2.5 3B 量化对比
python experiments/experiment_runner.py --config data/qwen25_3b_hf_4bit/test_cases.json --output-dir data/qwen25_3b_hf_4bit --skip-bartscore
python experiments/experiment_runner.py --config data/qwen25_3b_hf_8bit/test_cases.json --output-dir data/qwen25_3b_hf_8bit --skip-bartscore

# Qwen 2.5 7B 量化对比
python experiments/experiment_runner.py --config data/qwen25_7b_hf_4bit/test_cases.json --output-dir data/qwen25_7b_hf_4bit --skip-bartscore
python experiments/experiment_runner.py --config data/qwen25_7b_hf_8bit/test_cases.json --output-dir data/qwen25_7b_hf_8bit --skip-bartscore
```

## 数据分析计划

### 阶段 1: 基础统计

1. **描述性统计**
   - 每个模型配置的平均吞吐量、延迟、能耗
   - 质量指标分布（按任务类型）
   - 显存占用峰值

2. **量化效应**
   - 4-bit vs 8-bit 的质量损失率
   - 4-bit vs 8-bit 的效率提升率
   - 质效比对比

### 阶段 2: 深度分析

1. **任务敏感性分析**
   - ANOVA: 量化级别 × 任务类型交互效应
   - 热图: 任务-量化质量损失矩阵
   - 推荐: 每种任务的最优量化级别

2. **模型规模分析**
   - 回归: 参数量 vs 量化鲁棒性
   - 对比: 2B vs 3B vs 4B vs 7B vs 8B
   - 拐点: 量化友好的模型规模阈值

3. **语言公平性分析**
   - 中英文质量损失对比
   - 跨语言任务的量化影响
   - 公平性指标（Fairness Gap, Gini）

### 阶段 3: 可视化

1. **质效比散点图**
   - X轴: 效率得分
   - Y轴: 质量得分
   - 颜色: 量化级别
   - 大小: 模型参数量

2. **量化效应热图**
   - 行: 模型
   - 列: 任务类型
   - 值: 质量损失率（4-bit vs 8-bit）

3. **帕累托前沿**
   - 质量-效率的帕累托最优解
   - 标注每个模型配置的位置
   - 识别最优量化策略

4. **雷达图对比**
   - 维度: 8个任务类型
   - 对比: 同一模型的 4-bit vs 8-bit

## 预期输出

### 学术贡献

1. **量化效应模型**
   - 量化损失预测公式
   - 基于任务类型和模型规模

2. **最优量化策略**
   - 任务-量化映射表
   - 决策树: 如何选择量化级别

3. **公平性分析**
   - 量化对语言公平性的影响
   - 缓解策略建议

### 实践指导

1. **量化选择指南**
   - 何时使用 4-bit？
   - 何时使用 8-bit？
   - 何时不应量化？

2. **性能预测工具**
   - 输入: 模型大小、任务类型、量化级别
   - 输出: 预期质量损失、效率提升

3. **部署建议**
   - 资源受限场景的最优配置
   - 质量优先场景的最优配置
   - 平衡场景的最优配置

## 相关文档

- [实验状态总览](../EXPERIMENT_STATUS.md)
- [Gemma 量化配置](GEMMA_QUANTIZATION_SPLIT.md)
- [批量实验指南](EXPERIMENTS_BATCH_GUIDE.md)
- [实验执行器指南](EXPERIMENT_RUNNER_GUIDE.md)

## 生成脚本

- **配置生成**: `scripts/split_all_hf_quantization.py`
- **批量运行**: `scripts/run_all_experiments_complete.bat`
- **单模型分离**: `scripts/split_gemma_configs.py`

---

**准备就绪！** 所有 15 个模型配置已完成，可以开始量化对比实验。
