# 质量评估结果变更日志

本文档记录质量评估结果目录的重要变更。

---

## [2026-03-05] - QA任务目录合并与指标文档创建

### 新增
- ✅ 创建 `METRICS_GUIDE.md` - 详细的质量评估指标说明文档
  - 包含7种任务类型的所有评估指标
  - 提供指标含义、取值范围、评估方法说明
  - 包含数据文件使用指南和评分归一化说明

### 变更
- 🔄 合并QA任务评估结果目录
  - 将 `qa_quality_academic/` 目录内容合并到 `qa_quality/`
  - 保留两个版本的评估文件（标准版和学术版）
  - 统一目录结构，便于管理和使用

### 目录结构变更

**之前：**
```
data/analize/results/
├── qa_quality/
│   ├── qa_quality_scores.csv
│   └── qa_quality_summary.csv
└── qa_quality_academic/
    ├── qa_quality_scores_academic.csv
    └── qa_quality_summary_academic.csv
```

**之后：**
```
data/analize/results/
└── qa_quality/
    ├── figures/
    │   ├── qa_em_vs_f1.png
    │   ├── qa_metric_comparison.png
    │   ├── qa_model_question_heatmap.png
    │   └── qa_question_difficulty.png
    ├── qa_quality_scores.csv
    ├── qa_quality_scores_academic.csv
    ├── qa_quality_summary.csv
    ├── qa_quality_summary_academic.csv
    ├── qa_quality_report.md
    └── qa_quality_report_academic.md
```

### 文件说明

#### QA质量评估文件

| 文件名 | 说明 | 版本 |
|--------|------|------|
| `qa_quality_scores.csv` | 详细评分数据 | 标准版 |
| `qa_quality_scores_academic.csv` | 详细评分数据 | 学术版 |
| `qa_quality_summary.csv` | 汇总统计数据 | 标准版 |
| `qa_quality_summary_academic.csv` | 汇总统计数据 | 学术版 |
| `qa_quality_report.md` | 评估报告 | 标准版 |
| `qa_quality_report_academic.md` | 评估报告 | 学术版 |

#### 版本差异

- **标准版**：使用基础评估指标（EM, F1, BLEU, ROUGE-L）
- **学术版**：增加更多学术研究常用指标（BERTScore, 完整性, 相关性等）

### 影响

- ✅ 简化目录结构，减少冗余
- ✅ 保留两个版本的数据，满足不同需求
- ✅ 统一管理QA任务的所有评估结果
- ✅ 便于后续维护和更新

### 迁移指南

如果你的脚本或代码引用了 `qa_quality_academic/` 目录，请更新路径：

**旧路径：**
```python
# 旧代码
academic_scores = pd.read_csv('data/analize/results/qa_quality_academic/qa_quality_scores_academic.csv')
```

**新路径：**
```python
# 新代码
academic_scores = pd.read_csv('data/analize/results/qa_quality/qa_quality_scores_academic.csv')
```

---

## [2026-03-05] - 可视化图表生成

### 新增
- ✅ 生成所有任务类型的学术标准可视化图表
- ✅ 创建 `VISUALIZATION_GENERATION_SUMMARY.md` 文档
- ✅ 所有图表使用英文标签，符合国际学术标准

### 详情
- 总计生成 33+ 张高质量PNG图表
- 关键图表同时提供PDF版本（用于出版）
- 所有图表采用300 DPI分辨率
- 使用色盲友好的配色方案

---

## 文档索引

### 核心文档
- [指标说明文档](METRICS_GUIDE.md) - 详细的评估指标说明
- [目录结构文档](DIRECTORY_STRUCTURE.md) - 完整的目录结构说明
- [索引文档](INDEX.md) - 快速导航索引
- [README](README.md) - 概述和快速开始

### 可视化相关
- [可视化生成摘要](../visualization/VISUALIZATION_GENERATION_SUMMARY.md)
- [可视化快速指南](../visualization/VISUALIZATION_QUICK_GUIDE.md)
- [学术可视化风格指南](../visualization/ACADEMIC_VISUALIZATION_STYLE_GUIDE.md)

### 评估系统
- [评估系统指南](../scripts/EVALUATION_SYSTEM_GUIDE.md)
- [质量评估系统](../scripts/quality_evaluation_system.md)
- [快速开始指南](../QUICK_START.md)

---

## 维护说明

### 添加新的变更记录

在添加新的变更时，请遵循以下格式：

```markdown
## [YYYY-MM-DD] - 变更标题

### 新增
- ✅ 新增内容描述

### 变更
- 🔄 变更内容描述

### 删除
- ❌ 删除内容描述

### 修复
- 🐛 修复内容描述

### 详情
详细说明...
```

### 版本标记说明

- ✅ 新增功能或文件
- 🔄 修改或更新
- ❌ 删除或移除
- 🐛 错误修复
- 📝 文档更新
- 🎨 样式或格式改进
- ⚡ 性能优化
- 🔒 安全相关

---

**文档维护者**：Kiro AI Assistant  
**最后更新**：2026年3月5日
