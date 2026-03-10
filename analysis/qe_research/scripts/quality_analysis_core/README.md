# 质量数据描述性分析模块

## 概述

本模块实现对 `analysis/qe_research/results/quality_scores/` 中质量评分数据的全面描述性分析，生成标准化的统计报告和可视化图表。

## 功能特性

- **多任务分析**: 支持7个任务类型（code, creative, math, qa, reasoning, summary, translation）
- **描述性统计**: 计算均值、中位数、标准差、变异系数等统计量
- **分布分析**: 生成直方图+KDE分布图
- **模型排名**: 按主要指标对模型进行排名可视化
- **相关性分析**: 计算并可视化指标间的相关系数矩阵
- **跨任务综合评估**: 模型×任务热力图和综合排名
- **自动化报告**: 生成Markdown格式的综合分析报告

## 文件结构

```
quality_analysis_core/
├── quality_data_analyzer.py    # 主分析器类
├── shared_functions.py          # 共享工具函数
├── reference.md                 # 参考报告格式
└── README.md                    # 本文档
```

## 快速开始

### 方法1: 使用批处理脚本（Windows推荐）

```bash
# 双击运行或在命令行执行
analysis/qe_research/scripts/run_quality_analysis.bat
```

### 方法2: 使用Python脚本

```bash
# 激活conda环境
conda activate bartscore

# 设置UTF-8编码
set PYTHONUTF8=1

# 运行分析
python analysis/qe_research/scripts/run_quality_analysis.py
```

### 方法3: 直接调用分析器

```python
from analysis.qe_research.scripts.quality_analysis_core.quality_data_analyzer import QualityDataAnalyzer

# 创建分析器
analyzer = QualityDataAnalyzer(use_raw=True)

# 运行所有分析
analyzer.run_all_analyses()
```

## 输出结果

分析完成后，结果保存在 `analysis/qe_research/results/quality_analysis/` 目录：

### 1. 报告 (`reports/`)
- `QUALITY_ANALYSIS_REPORT.md`: 综合分析报告

### 2. 图表 (`figures/`)
- `{task}_{metric}_distribution.png`: 各任务指标分布图
- `{task}_model_ranking.png`: 各任务模型排名
- `{task}_correlation.png`: 各任务指标相关性热力图
- `cross_task_heatmap.png`: 模型×任务质量热力图
- `cross_task_ranking.png`: 跨任务综合排名

### 3. 数据表格 (`tables/`)
- `{task}_descriptive_stats.csv`: 各任务描述性统计
- `cross_task_summary.csv`: 跨任务综合摘要

## 数据来源

分析使用的数据来自 `analysis/qe_research/results/quality_scores/`：

- `code_scores_raw.csv`: 代码生成质量评分
- `creative_scores_raw.csv`: 创意写作质量评分
- `math_scores_raw.csv`: 数学推理质量评分
- `qa_scores_raw.csv`: 问答质量评分
- `reasoning_scores_raw.csv`: 逻辑推理质量评分
- `summary_scores_raw.csv`: 摘要生成质量评分
- `translation_scores_raw.csv`: 翻译质量评分

数据格式：转置格式（指标为行，模型为列），脚本会自动转换为标准格式。

## 指标说明

各任务的主要评估指标参考 `QUALITY_SCORES_GENERATION_REPORT_V2.md`：

- **代码生成**: compilation_rate, functional_correctness, code_length
- **创意写作**: distinct_2, distinct_1, metaphor_count
- **数学推理**: exact_match, extraction_confidence, has_answer
- **问答**: confidence_score, answer_length, certainty_count
- **逻辑推理**: conclusion_correct, completeness_score, coherence_score
- **摘要生成**: bartscore_avg, bertscore_f1, bartscore_faith
- **翻译**: bertscore_f1, bleu_1, bertscore_precision

## 共享函数库

`shared_functions.py` 提供可复用的工具函数：

### 数据加载
- `load_quality_scores()`: 加载质量评分数据
- `get_task_info()`: 获取任务信息

### 统计分析
- `calculate_descriptive_stats()`: 计算描述性统计量
- `normalize_scores()`: 数据归一化
- `identify_outliers()`: 异常值检测
- `calculate_correlation_matrix()`: 相关系数矩阵

### 可视化
- `plot_distribution()`: 分布图（直方图+KDE）
- `plot_boxplot()`: 箱线图
- `plot_heatmap()`: 热力图
- `plot_radar_chart()`: 雷达图

### 工具函数
- `setup_chinese_font()`: 设置中文字体
- `get_academic_colors()`: 获取学术配色
- `save_table()`: 保存数据表格
- `format_number()`: 格式化数值

## 自定义分析

### 分析单个任务

```python
analyzer = QualityDataAnalyzer(use_raw=True)
analyzer.load_all_data()
analyzer.analyze_task('code')  # 只分析代码任务
```

### 使用共享函数

```python
from analysis.qe_research.scripts.quality_analysis_core.shared_functions import (
    load_quality_scores, calculate_descriptive_stats, plot_distribution
)

# 加载数据
df = load_quality_scores('code', use_raw=True)

# 计算统计量
stats = calculate_descriptive_stats(df['compilation_rate'])

# 绘制分布图
plot_distribution(df['compilation_rate'], 
                 title='编译率分布', 
                 output_path='compilation_rate_dist.png')
```

## 依赖环境

- Python 3.8+
- pandas >= 1.5.0
- numpy >= 1.23.0
- matplotlib >= 3.5.0
- seaborn >= 0.12.0

## 注意事项

1. **中文字体**: 脚本会自动检测并使用Microsoft YaHei字体，如系统无此字体会回退到英文
2. **数据完整性**: 确保所有任务的质量评分数据文件存在
3. **输出目录**: 脚本会自动创建输出目录，无需手动创建
4. **日志记录**: 分析日志保存在 `analysis/qe_research/logs/quality_analysis.log`

## 参考文档

- 指标详细说明: `analysis/qe_research/results/quality_scores/QUALITY_SCORES_GENERATION_REPORT_V2.md`
- 报告格式参考: `analysis/qe_research/scripts/quality_analysis_core/reference.md`
- 数据结构说明: `analysis/DATA_STRUCTURE_REFACTORING.md`

## 更新日志

- **2026-03-07**: 初始版本，实现基础描述性分析功能
  - 支持7个任务类型的质量数据分析
  - 生成标准化报告和可视化图表
  - 提供共享函数库便于复用

## 维护者

GenAI质效比评估项目组
