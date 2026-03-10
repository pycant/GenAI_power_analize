# 混合任务分析

## 概述

混合任务分析通过加权聚合多个任务的质量得分，评估模型在综合场景下的质效比表现。支持三种预定义权重配置，适用于不同应用场景。

## 核心特性

- ✅ **多任务聚合**: 综合评估7个任务（code, creative, math, qa, reasoning, summary, translation）
- ✅ **灵活权重**: 支持客观任务为主、主观任务为主、均衡配置三种方案
- ✅ **帕累托分析**: 识别质量-能耗、质量-速度、三维帕累托前沿
- ✅ **稳健性验证**: 扰动分析和交叉验证
- ✅ **完整输出**: 数据文件、可视化图表、分析报告

## 快速开始

### 1. 检查前置条件
```bash
# 确保质量数据存在
ls analysis/qe_research/results/quality_scores/*_scores_raw.csv

# 确保能耗和速度数据存在
ls analysis/qe_research/results/metric_tables/energy_per_token_transposed.csv
ls analysis/qe_research/results/metric_tables/tokens_per_second_transposed.csv
```

### 2. 运行分析
```bash
conda activate bartscore
set PYTHONUTF8=1
cd analysis/qe_research/scripts/pareto_core
python pareto_mixed_task.py
```

### 3. 查看结果
```bash
# 查看报告
code analysis/qe_research/results/mixed_task_analysis/task_01/objective/MIXED_TASK_ANALYSIS_REPORT.md

# 查看图表
explorer analysis/qe_research/results/mixed_task_analysis/task_01/objective
```

## 权重配置

### Objective（客观任务为主）
适用于技术应用、工程实践、需要精确结果的场景

| 任务 | 权重 | 类型 |
|------|------|------|
| code | 30% | 客观 |
| math | 25% | 客观 |
| qa | 20% | 客观 |
| reasoning | 15% | 客观 |
| creative | 5% | 主观 |
| summary | 3% | 主观 |
| translation | 2% | 主观 |

**客观任务合计**: 90% | **主观任务合计**: 10%

### Subjective（主观任务为主）
适用于内容创作、文学创作、需要创造性的场景

| 任务 | 权重 | 类型 |
|------|------|------|
| creative | 35% | 主观 |
| summary | 25% | 主观 |
| translation | 20% | 主观 |
| code | 10% | 客观 |
| math | 5% | 客观 |
| qa | 3% | 客观 |
| reasoning | 2% | 客观 |

**主观任务合计**: 80% | **客观任务合计**: 20%

### Balanced（均衡配置）
适用于通用评估、综合应用

| 任务 | 权重 |
|------|------|
| code | 15% |
| math | 15% |
| qa | 15% |
| creative | 15% |
| summary | 15% |
| translation | 13% |
| reasoning | 12% |

**分布**: 相对均衡，客观任务57%，主观任务43%

## 输出结构

```
mixed_task_analysis/task_01/
├── objective/                           # 客观任务为主
│   ├── merged_data.csv                  # 合并数据（模型×质量/能耗/速度）
│   ├── task_quality_scores.csv          # 质量矩阵（模型×任务）
│   ├── task_weights.png                 # 权重分布柱状图
│   ├── quality_heatmap.png              # 质量热力图
│   ├── pareto_quality_energy.png        # 质量-能耗前沿
│   ├── pareto_quality_speed.png         # 质量-速度前沿
│   ├── MIXED_TASK_ANALYSIS_REPORT.md    # 完整报告
│   └── {task}/entropy_weights.png       # 各任务熵权法权重
│
├── subjective/                          # 主观任务为主
│   └── ...（同上）
│
└── balanced/                            # 均衡配置
    └── ...（同上）
```

## 关键指标

### 综合质量得分
- **定义**: 各任务质量得分的加权平均
- **范围**: [0, 1]
- **计算**: Σ(任务权重 × 归一化质量得分)
- **解释**: 越高表示模型在多任务场景下综合表现越好

### 平均能耗
- **定义**: 各任务能耗的算术平均
- **单位**: J/token
- **解释**: 越低表示模型越节能

### 平均速度
- **定义**: 各任务速度的算术平均
- **单位**: tokens/s
- **解释**: 越高表示模型推理越快

### 帕累托前沿
- **质量-能耗前沿**: 在质量和能耗之间不被支配的模型集合
- **质量-速度前沿**: 在质量和速度之间不被支配的模型集合
- **三维前沿**: 在质量、能耗、速度三个维度都不被支配的模型

### 拐点模型
- **定义**: 帕累托前沿上曲率最大的点
- **意义**: 综合性价比最高，推荐优先选择
- **特点**: 在质量提升和效率损失之间达到最佳平衡

## 分析流程

```
1. 加载质量数据
   ├─ 使用熵权法处理各任务指标
   ├─ Z-Score归一化
   └─ 生成任务质量得分

2. 聚合质量得分
   ├─ Min-Max归一化到[0,1]
   ├─ 按权重加权平均
   └─ 生成综合质量得分

3. 合并能耗和速度
   ├─ 计算各任务平均能耗
   ├─ 计算各任务平均速度
   └─ 合并为完整数据集

4. 帕累托前沿分析
   ├─ 识别2D前沿（质量-能耗、质量-速度）
   ├─ 识别3D前沿
   ├─ 计算超体积、间距指标
   └─ 寻找拐点模型

5. 稳健性分析
   ├─ 扰动分析（±5%噪声，100次）
   └─ 交叉验证（5折）

6. 生成输出
   ├─ 数据文件（CSV）
   ├─ 可视化图表（PNG）
   └─ 分析报告（Markdown）
```

## 使用场景

### 场景1: 技术应用选型
**推荐配置**: objective（客观任务为主）

适用于：
- 代码助手、IDE插件
- 数学求解器、计算工具
- 问答系统、知识库
- 逻辑推理引擎

**关注指标**: 综合质量得分、代码/数学任务表现

### 场景2: 内容创作应用
**推荐配置**: subjective（主观任务为主）

适用于：
- 文章生成、博客写作
- 创意写作、故事创作
- 文本摘要、内容提炼
- 机器翻译服务

**关注指标**: 综合质量得分、创意/摘要/翻译任务表现

### 场景3: 通用评估对比
**推荐配置**: balanced（均衡配置）

适用于：
- 模型选型决策
- 学术研究对比
- 综合能力评估
- 跨场景应用

**关注指标**: 综合质量得分、各任务均衡性

## 文档索引

- 📖 **[method.md](method.md)**: 详细方法说明
- 🚀 **[QUICK_START.md](QUICK_START.md)**: 快速开始指南
- 📊 **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)**: 实现总结

## 相关分析

- **单任务分析**: `analysis/qe_research/results/pareto_analysis_v3/`
- **质量分析**: `analysis/qe_research/results/quality_analysis/`
- **原始数据分析**: `analysis/qe_research/results/raw_analysis/`

## 技术支持

### 依赖项
- Python 3.8+
- pandas, numpy, matplotlib, seaborn
- scikit-learn

### 常见问题
参见 [QUICK_START.md](QUICK_START.md) 的"常见问题"部分

### 联系方式
- 项目仓库: GenAI_power_analize
- 文档: `analysis/qe_research/`

---

**版本**: 1.0  
**更新日期**: 2026-03-08  
**状态**: ✅ 已完成，可运行
