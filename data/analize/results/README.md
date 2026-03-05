# 质量评估结果目录

本目录包含所有任务类型的质量评估结果，按任务类型组织。

## 目录结构

```
data/analize/results/
├── README.md                          # 本文件
├── code_quality/                      # 代码生成任务评估结果
│   ├── figures/                       # 可视化图表
│   ├── code_quality_scores.csv        # 详细评分
│   ├── code_quality_summary.csv       # 汇总统计
│   └── code_quality_report.md         # 评估报告
├── creative_quality/                  # 创意写作任务评估结果
│   ├── figures/                       # 可视化图表
│   ├── creative_quality_scores.csv    # 详细评分
│   ├── creative_quality_summary.csv   # 汇总统计
│   └── creative_quality_report.md     # 评估报告
├── math_quality/                      # 数学推理任务评估结果
│   ├── figures/                       # 可视化图表
│   ├── math_quality_scores.csv        # 详细评分
│   ├── math_quality_summary.csv       # 汇总统计
│   └── math_quality_report.md         # 评估报告
├── qa_quality/                        # 问答任务评估结果
│   ├── figures/                       # 可视化图表
│   ├── qa_quality_scores.csv          # 详细评分
│   ├── qa_quality_summary.csv         # 汇总统计
│   └── qa_quality_report.md           # 评估报告
├── reasoning_quality/                 # 逻辑推理任务评估结果
│   ├── figures/                       # 可视化图表
│   ├── reasoning_quality_scores.csv   # 详细评分
│   ├── reasoning_quality_summary.csv  # 汇总统计
│   └── reasoning_quality_report.md    # 评估报告
├── summary_quality/                   # 文本摘要任务评估结果
│   ├── figures/                       # 可视化图表
│   ├── summary_quality_scores.csv     # 详细评分
│   ├── summary_quality_summary.csv    # 汇总统计
│   └── summary_quality_report.md      # 评估报告
└── translation_quality/               # 翻译任务评估结果
    ├── figures/                       # 可视化图表
    ├── translation_quality_scores.csv # 详细评分
    ├── translation_quality_summary.csv# 汇总统计
    └── translation_quality_report.md  # 评估报告
```

## 任务类型说明

### 1. 代码生成 (code_quality)
- **评估指标**: 编译成功率、语法正确性、代码质量
- **核心文件**: code_quality_scores.csv
- **报告**: code_quality_report.md

### 2. 创意写作 (creative_quality)
- **评估指标**: Distinct-N、困惑度、文本长度
- **核心文件**: creative_quality_scores.csv
- **报告**: creative_quality_report.md

### 3. 数学推理 (math_quality)
- **评估指标**: Exact Match、数值精度、推理完整性
- **核心文件**: math_quality_scores.csv
- **报告**: math_quality_report.md

### 4. 问答 (qa_quality)

- **评估指标**: Exact Match、F1 Score、BERTScore、ROUGE-L
- **核心文件**: qa_quality_scores.csv, qa_quality_scores_academic.csv
- **报告**: qa_quality_report.md, qa_quality_report_academic.md
- **说明**: 包含标准版和学术版两个版本的评估结果

### 5. 逻辑推理 (reasoning_quality)
- **评估指标**: 结论正确性、推理完整性、逻辑连贯性
- **核心文件**: reasoning_quality_scores.csv
- **报告**: reasoning_quality_report.md

### 6. 文本摘要 (summary_quality)
- **评估指标**: ROUGE-L、BERTScore、BARTScore、压缩比
- **核心文件**: summary_quality_scores.csv
- **报告**: summary_quality_report.md

### 7. 翻译 (translation_quality)
- **评估指标**: BLEU、chrF、BERTScore、长度比
- **核心文件**: translation_quality_scores.csv
- **报告**: translation_quality_report.md

## 文件说明

### 详细评分文件 (*_quality_scores.csv)
包含每个模型在每个问题上的详细评分，字段包括：
- `model`: 模型名称
- `question_id`: 问题ID
- 各项评估指标的具体分数

### 汇总统计文件 (*_quality_summary.csv)
包含按模型汇总的统计数据，字段包括：
- `model`: 模型名称
- 各指标的 `mean`、`std`、`min`、`max` 统计值

### 评估报告 (*_quality_report.md)
包含：
- 评估概览
- 核心指标排名
- 按任务/问题类型分析
- 指标说明
- 详细数据引用

### 可视化图表 (figures/)
包含各类对比图表：
- 准确率对比柱状图
- 多维度散点图
- 雷达图
- 热力图等

## 使用指南

### 查看评估结果

1. **快速查看排名**：打开对应任务的 `*_quality_report.md`
2. **详细分析**：查看 `*_quality_scores.csv` 和 `*_quality_summary.csv`
3. **可视化分析**：查看 `figures/` 目录下的图表

### 对比不同任务

可以使用以下脚本汇总所有任务的评估结果：

```bash
python data/analize/scripts/aggregate_all_quality_results.py
```

### 生成综合报告

```bash
python data/analize/scripts/generate_comprehensive_report.py
```

## 数据更新

- **最后更新**: 2026-03-05
- **评估模型数**: 12个模型
- **评估任务数**: 7种任务类型
- **总评估次数**: 约420次（12模型 × 7任务 × 5问题）

## 注意事项

1. 所有CSV文件使用UTF-8编码
2. 图表文件为PNG格式，分辨率300 DPI
3. 报告文件为Markdown格式，支持中文显示
4. 评分范围通常为 [0, 1]，部分指标可能有不同范围

## 相关文档

### 核心文档
- **[质量评估指标说明](METRICS_GUIDE.md)** - 详细的评估指标说明和数据文件使用指南 ⭐
- [目录结构文档](DIRECTORY_STRUCTURE.md) - 完整的目录结构说明
- [变更日志](CHANGELOG.md) - 目录变更记录
- [索引文档](INDEX.md) - 快速导航索引

### 评估系统设计
- [质量评估体系设计](../scripts/quality_evaluation_system.md)
- [代码评估设计](../scripts/CODE_EVALUATION_DESIGN.md)
- [创意写作评估设计](../scripts/CREATIVE_EVALUATION_DESIGN.md)
- [数学推理评估设计](../scripts/MATH_EVALUATION_DESIGN.md)
- [问答评估设计](../scripts/QA_EVALUATION_DESIGN.md)
- [逻辑推理评估设计](../scripts/REASONING_EVALUATION_DESIGN.md)
- [文本摘要评估设计](../scripts/SUMMARY_EVALUATION_DESIGN.md)
- [翻译评估设计](../scripts/TRANSLATION_EVALUATION_DESIGN.md)

### 可视化相关
- [可视化生成摘要](../visualization/VISUALIZATION_GENERATION_SUMMARY.md)
- [可视化快速指南](../visualization/VISUALIZATION_QUICK_GUIDE.md)
- [学术可视化风格指南](../visualization/ACADEMIC_VISUALIZATION_STYLE_GUIDE.md)

## 联系方式

如有问题或建议，请参考项目文档或提交Issue。
