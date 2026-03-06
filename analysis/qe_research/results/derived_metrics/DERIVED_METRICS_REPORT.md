# 派生指标分析报告

**生成时间**: 2026-03-06 14:20:14

---

## 概述

本报告基于6个基础指标表格，计算了8个派生指标，提供更深入的模型性能分析。

## 派生指标列表

### 1. 平均token速度 (tokens/s)

**公式**: 输出tokens / 回答时间

**意义**: 衡量模型的生成速度，越高越好。

**文件**: `07_avg_token_speed.csv`

### 2. 每token能耗 (J/token)

**公式**: GPU能耗 / 输出tokens

**意义**: 衡量生成每个token的能耗成本，越低越好。

**文件**: `08_energy_per_token.csv`

### 3. 平均功率 (W)

**公式**: GPU能耗 / 回答时间

**意义**: 衡量模型运行时的平均功率消耗，越低越好。

**文件**: `09_avg_power.csv`

### 4. 显存效率 (tokens/MB)

**公式**: 输出tokens / 显存占用

**意义**: 衡量显存利用效率，越高越好。

**文件**: `10_memory_efficiency.csv`

### 5. 能效比 (tokens/J)

**公式**: 输出tokens / GPU能耗

**意义**: 衡量能量利用效率，越高越好。这是评估模型可持续性的关键指标。

**文件**: `11_throughput_per_joule.csv`

### 6. 首token延迟占比 (%)

**公式**: (TTFT / 1000) / 回答时间 × 100

**意义**: 衡量首token延迟在总时间中的占比，越低表示生成过程越流畅。

**文件**: `12_ttft_ratio.csv`

**注意**: 仅部分Ollama模型有数据。

### 7. GPU利用效率 (tokens/s/%)

**公式**: token速度 / GPU占用率

**意义**: 衡量GPU利用的有效性，越高表示GPU资源利用越充分。

**文件**: `13_gpu_utilization_efficiency.csv`

### 8. 综合效率得分 (0-1)

**公式**: 0.4×归一化速度 + 0.4×归一化能效 + 0.2×归一化显存效率

**意义**: 综合评估模型的整体效率，越高越好。

**文件**: `14_composite_efficiency_score.csv`

## 关键发现

### Token生成速度

- **code任务**: 最快 qwen3:4b (59.3 tokens/s), 最慢 qwen--qwen2.5-7b-instruct:8bit (3.3 tokens/s)
- **creative任务**: 最快 qwen3:4b (65.8 tokens/s), 最慢 qwen--qwen2.5-7b-instruct:8bit (3.4 tokens/s)
- **math任务**: 最快 qwen3:4b (64.7 tokens/s), 最慢 qwen--qwen2.5-3b-instruct:8bit (7.4 tokens/s)
- **multi_turn任务**: 最快 qwen3:4b (211.5 tokens/s), 最慢 qwen--qwen2.5-3b-instruct:8bit (23.6 tokens/s)
- **qa任务**: 最快 qwen3:4b (57.6 tokens/s), 最慢 qwen--qwen2.5-3b-instruct:8bit (7.6 tokens/s)
- **reasoning任务**: 最快 qwen3:4b (64.6 tokens/s), 最慢 qwen--qwen2.5-3b-instruct:8bit (7.5 tokens/s)
- **summary任务**: 最快 qwen3:4b (55.4 tokens/s), 最慢 google--gemma-2b-it:8bit (7.3 tokens/s)
- **translation任务**: 最快 qwen3:4b (60.5 tokens/s), 最慢 qwen--qwen2.5-3b-instruct:8bit (7.6 tokens/s)

### 能效比排名

- **code任务**: qwen3:4b (0.837 tokens/J)
- **creative任务**: qwen3:4b (0.924 tokens/J)
- **math任务**: qwen3:4b (0.953 tokens/J)
- **multi_turn任务**: qwen3:4b (0.866 tokens/J)
- **qa任务**: qwen3:4b (0.971 tokens/J)
- **reasoning任务**: qwen3:4b (0.952 tokens/J)
- **summary任务**: qwen3:4b (0.984 tokens/J)
- **translation任务**: qwen3:4b (0.968 tokens/J)

### 综合效率得分 Top 3

**跨任务平均得分**:

1. qwen3:4b: 1.000
2. gemma3:4b: 0.639
3. qwen3:8b: 0.487

## 使用建议

### 场景推荐

1. **追求速度**: 选择token速度最高的模型
2. **追求节能**: 选择能效比最高的模型
3. **显存受限**: 选择显存效率最高的模型
4. **综合考虑**: 选择综合效率得分最高的模型

## 数据文件

所有派生指标CSV文件位于: `analysis/qe_research/results/derived_metrics/`

---

**生成脚本**: `analysis/qe_research/scripts/compute_derived_metrics.py`
