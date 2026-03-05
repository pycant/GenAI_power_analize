# 综合分析快速指南

**版本**: 1.0  
**更新时间**: 2026-03-05

---

## 📋 概述

综合分析系统整合质量评估结果和性能实验数据，生成多维度模型评估报告，支持模型选型决策。

## 🎯 核心功能

- ✅ 整合7种任务类型的质量评估数据
- ✅ 整合性能实验数据（能耗、延迟、吞吐量）
- ✅ 计算复合指标（质效比、效率得分、成本指标）
- ✅ 多维度分析（模型、任务、公平性）
- ✅ 生成可视化图表和分析报告

---

## 🚀 快速开始

### 前置条件

1. 已完成质量评估（7种任务类型）
2. 已完成性能实验（experiments_N）
3. 激活conda环境

### 运行步骤

```bash
# 1. 激活环境
conda activate bartscore

# 2. 设置编码
set PYTHONUTF8=1

# 3. 运行综合分析（使用默认配置）
python scripts/comprehensive_analysis.py

# 4. 查看结果
# - 报告: data/analysis/COMPREHENSIVE_ANALYSIS_REPORT.md
# - 数据: data/analysis/*.csv
# - 图表: data/analysis/figures/
```

---

## 📊 输出文件说明

### 数据文件

| 文件名 | 说明 | 关键列 |
|--------|------|--------|
| `comprehensive_results.csv` | 整合的原始数据 | model, task_type, quality_score, latency_s, gpu_energy_j |
| `composite_metrics.csv` | 包含复合指标的完整数据 | qe_ratio, efficiency_score, score_final, cpq |
| `model_analysis.csv` | 按模型汇总的分析结果 | qe_ratio_mean, quality_score_mean, 综合排名 |
| `task_analysis.csv` | 按任务汇总的分析结果 | model, task_type, qe_ratio, quality_score |

### 关键指标说明

| 指标 | 符号 | 计算公式 | 说明 |
|------|------|----------|------|
| 质效比 | QE_ratio | (Q_norm + 0.01) / (1.01 - Eff_score) | 综合评估指标，越大越好 |
| 效率得分 | Eff_score | 0.4×吞吐归一 + 0.3×延迟归一 + 0.3×能耗归一 | 效率综合得分 [0,1] |
| 最终得分 | Score_final | 质量 / 每token能耗 | 能效加权得分 |
| 成本效能比 | CPQ | 质量 / 总成本 | 单位成本质量 |

---

## 🔧 高级用法

### 指定实验批次

```bash
# 分析 experiments_2 的数据
python scripts/comprehensive_analysis.py --experiment experiments_2
```

### 自定义输出目录

```bash
# 输出到自定义目录
python scripts/comprehensive_analysis.py --output-dir data/analysis_v2
```

### 自定义质量数据目录

```bash
# 使用不同的质量数据目录
python scripts/comprehensive_analysis.py --quality-dir data/analize_v2/results
```

### 组合使用

```bash
python scripts/comprehensive_analysis.py \
    --experiment experiments_3 \
    --quality-dir data/analize/results \
    --output-dir data/analysis_exp3
```

---

## 📈 典型工作流

### 场景1: 首次运行综合分析

```bash
# 1. 确认数据完整性
ls data/analize/results/*/  # 检查质量数据
ls data/experiments_1/summary/results.csv  # 检查性能数据

# 2. 运行分析
python scripts/comprehensive_analysis.py

# 3. 查看结果
cat data/analysis/model_analysis.csv  # 查看模型排名
```

### 场景2: 对比多个实验批次

```bash
# 分析实验1
python scripts/comprehensive_analysis.py \
    --experiment experiments_1 \
    --output-dir data/analysis_exp1

# 分析实验2
python scripts/comprehensive_analysis.py \
    --experiment experiments_2 \
    --output-dir data/analysis_exp2

# 对比结果
diff data/analysis_exp1/model_analysis.csv data/analysis_exp2/model_analysis.csv
```

### 场景3: 更新质量评估后重新分析

```bash
# 1. 重新运行质量评估
python data/analize/scripts/run_all_evaluations.py

# 2. 重新运行综合分析
python scripts/comprehensive_analysis.py

# 3. 对比新旧结果
diff data/analysis/model_analysis.csv data/analysis_backup/model_analysis.csv
```

---

## 🔍 结果解读

### 模型排名解读

```csv
model,qe_ratio_mean,quality_score_mean,efficiency_score_mean,综合排名
qwen3_8b,1.8542,0.8234,0.7123,1
deepseek_r1_8b,1.7891,0.8456,0.6891,2
gemma3_4b,1.6234,0.7123,0.7456,3
```

**解读**:
- `qwen3_8b` 综合排名第1，质效比最高
- `deepseek_r1_8b` 质量最高(0.8456)，但效率略低
- `gemma3_4b` 效率最高(0.7456)，但质量相对较低

### 任务分析解读

查看每个模型在不同任务上的表现，识别：
- 各模型的优势任务
- 各任务的最佳模型
- 任务难度差异

---

## ⚠️ 常见问题

### Q1: 数据整合失败

**问题**: `ValueError: 未找到任何质量评估数据`

**解决**:
```bash
# 检查质量数据是否存在
ls data/analize/results/*/

# 如果缺失，运行质量评估
python data/analize/scripts/run_all_evaluations.py
```

### Q2: 模型名称不匹配

**问题**: 整合后数据很少，模型名称不匹配

**解决**: 脚本会自动标准化模型名称（qwen3:8b → qwen3_8b），但如果仍有问题：
- 检查质量数据中的模型名称
- 检查性能数据中的模型名称
- 确保两者一致

### Q3: 缺少某些指标

**问题**: `⚠ 警告: 缺少计算质效比所需的列`

**解决**: 检查性能数据是否包含必要字段：
- `latency_s`: 延迟
- `toks_per_s`: 吞吐量
- `gpu_energy_j`: GPU能耗
- `quality_score`: 质量得分（来自质量评估）

### Q4: 中文乱码

**解决**:
```bash
# Windows
set PYTHONUTF8=1
python scripts/comprehensive_analysis.py

# Linux/Mac
export PYTHONUTF8=1
python scripts/comprehensive_analysis.py
```

---

## 📚 相关文档

- 设计文档: `docs/analysis/comprehensive_analysis_design.md`
- 实验设计: `docs/experiment/experiment_design.md`
- 质量评估指南: `data/analize/scripts/EVALUATION_SYSTEM_GUIDE.md`
- 项目指南: `AGENTS.md`

---

## 🔄 更新日志

### v1.0 (2026-03-05)
- ✅ 初始版本
- ✅ 支持7种任务类型整合
- ✅ 实现复合指标计算
- ✅ 生成模型和任务分析

---

**需要帮助?** 查看详细设计文档或提交Issue
