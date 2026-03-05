# 质量评估指标快速参考卡

本文档提供所有评估指标的快速查询表，方便快速理解数据文件中的字段含义。

---

## 📋 快速索引

| 任务类型 | 核心指标 | 数据文件 |
|---------|---------|---------|
| [代码生成](#代码生成-code) | 语法正确性、功能完整性 | `code_quality_scores.csv` |
| [创意写作](#创意写作-creative) | 流畅度、创意性、词汇多样性 | `creative_quality_scores.csv` |
| [数学推理](#数学推理-math) | 答案正确性、推理过程 | `math_quality_scores.csv` |
| [问答](#问答-qa) | EM、F1、BERTScore | `qa_quality_scores.csv` |
| [逻辑推理](#逻辑推理-reasoning) | 结论正确性、推理完整性 | `reasoning_quality_scores.csv` |
| [文本摘要](#文本摘要-summary) | ROUGE、BERTScore、压缩比 | `summary_quality_scores.csv` |
| [翻译](#翻译-translation) | BLEU、语义保真度、流畅度 | `translation_quality_scores.csv` |

---

## 代码生成 (Code)

| 指标 | 字段名 | 范围 | 说明 |
|-----|--------|------|------|
| 语法正确性 | `syntax_correctness` | 0-1 | 代码能否通过编译/解析 |
| 功能完整性 | `functionality_completeness` | 0-1 | 是否实现要求的功能 |
| 代码质量 | `code_quality` | 0-1 | 可读性、结构性、注释 |
| 最佳实践 | `best_practices` | 0-1 | 是否遵循编程规范 |
| **综合得分** | `overall_score` | 0-1 | 加权平均 |

---

## 创意写作 (Creative)

| 指标 | 字段名 | 范围 | 说明 |
|-----|--------|------|------|
| 流畅度 | `fluency` | 0-1 | 语言流畅性和可读性 |
| 连贯性 | `coherence` | 0-1 | 逻辑连贯性和结构性 |
| 创意性 | `creativity` | 0-1 | 新颖性和想象力 |
| 相关性 | `relevance` | 0-1 | 与主题的相关程度 |
| 词汇多样性 | `distinct_2` | 0-1 | Bigram多样性 |
| 困惑度 | `perplexity` | >0 | 越低越好 |
| **综合得分** | `overall_score` | 0-1 | 多指标加权 |

---

## 数学推理 (Math)

| 指标 | 字段名 | 范围 | 说明 |
|-----|--------|------|------|
| 答案正确性 | `answer_correctness` | 0-1 | 最终答案是否正确 |
| 推理过程 | `reasoning_process` | 0-1 | 步骤完整性和正确性 |
| 公式使用 | `formula_usage` | 0-1 | 数学公式使用准确性 |
| 步骤清晰度 | `step_clarity` | 0-1 | 解题步骤清晰程度 |
| **综合得分** | `overall_score` | 0-1 | 多维度综合 |

---

## 问答 (QA)

| 指标 | 字段名 | 范围 | 说明 |
|-----|--------|------|------|
| 精确匹配 | `exact_match` (EM) | 0-1 | 与标准答案完全匹配 |
| F1分数 | `f1_score` | 0-1 | 精确率和召回率调和平均 |
| BLEU | `bleu_score` | 0-1 | N-gram重叠度 |
| ROUGE-L | `rouge_l` | 0-1 | 最长公共子序列相似度 |
| BERTScore | `bert_score` | 0-1 | 语义相似度 |
| 答案完整性 | `answer_completeness` | 0-1 | 包含所有必要信息 |
| 答案相关性 | `answer_relevance` | 0-1 | 与问题的相关程度 |
| **综合得分** | `overall_score` | 0-1 | 多指标加权 |

**版本说明：**
- 标准版：基础指标（EM, F1, BLEU, ROUGE）
- 学术版：增加BERTScore、完整性、相关性

---

## 逻辑推理 (Reasoning)

| 指标 | 字段名 | 范围 | 说明 |
|-----|--------|------|------|
| 结论正确性 | `conclusion_correctness` | 0-5 | 推理结论正确程度 |
| 推理完整性 | `reasoning_completeness` | 0-5 | 推理步骤完整程度 |
| 逻辑连贯性 | `logical_coherence` | 0-5 | 推理过程连贯性 |
| 论证深度 | `argumentation_depth` | 0-5 | 论证深度和细致程度 |
| 推理步骤数 | `step_count` | ≥0 | 推理步骤数量 |
| 推理类型 | `reasoning_type` | 分类 | 演绎/归纳/类比/因果 |
| **综合得分** | `overall_score` | 0-1 | 归一化综合评分 |

**评分标准（5分制）：**
- 5分：优秀 - 完全符合标准
- 4分：良好 - 基本符合，有小瑕疵
- 3分：中等 - 部分符合，有明显不足
- 2分：较差 - 大部分不符合
- 1分：很差 - 完全不符合

---

## 文本摘要 (Summary)

| 指标 | 字段名 | 范围 | 说明 |
|-----|--------|------|------|
| ROUGE-1 | `rouge_1` | 0-1 | Unigram召回率 |
| ROUGE-2 | `rouge_2` | 0-1 | Bigram召回率 |
| ROUGE-L | `rouge_l` | 0-1 | 最长公共子序列F1 |
| BERTScore | `bert_score` | 0-1 | 语义相似度 |
| BARTScore | `bart_score` | 实数 | 生成质量评分 |
| 压缩比 | `compression_ratio` | 0-1 | 摘要/原文长度比 |
| 信息密度 | `information_density` | 0-1 | 单位长度信息量 |
| 字数符合度 | `length_compliance` | 0-1 | 长度是否符合要求 |
| **综合得分** | `overall_score` | 0-1 | 多指标加权 |

**指标解读：**
- ROUGE越高 → 与参考摘要越相似
- BERTScore越高 → 语义保留越好
- 压缩比适中为佳（通常0.2-0.3）
- 信息密度越高 → 信息提取越精炼

---

## 翻译 (Translation)

| 指标 | 字段名 | 范围 | 说明 |
|-----|--------|------|------|
| BLEU | `bleu_score` | 0-1 | 机器翻译标准指标 |
| 语义保真度 | `semantic_fidelity` | 0-1 | 译文与原文语义一致性 |
| 流畅度 | `fluency` | 0-1 | 译文语言流畅性 |
| 术语准确性 | `terminology_accuracy` | 0-1 | 专业术语翻译准确性 |
| 文化适应性 | `cultural_adaptation` | 0-1 | 译文文化适应程度 |
| 语言对 | `language_pair` | 分类 | 如en-zh, zh-en |
| 领域类型 | `domain` | 分类 | 技术/文学/日常等 |
| **综合得分** | `overall_score` | 0-1 | 多维度综合 |

---

## 🔍 通用字段

所有数据文件都包含以下字段：

| 字段名 | 说明 | 示例 |
|--------|------|------|
| `model` | 模型名称 | `qwen3_8b`, `deepseek-r1_8b` |
| `question_id` | 问题编号 | `q1`, `q2`, `q3` |
| `task_type` | 任务类型 | `code`, `creative`, `qa` |
| `timestamp` | 评估时间戳 | `2026-03-05 14:30:00` |
| `overall_score` | 综合得分 | 0.85 (0-1范围) |

---

## 📊 评分等级参考

| 分数范围 | 等级 | 说明 |
|---------|------|------|
| 0.9-1.0 | ⭐⭐⭐⭐⭐ 优秀 | 表现卓越 |
| 0.8-0.9 | ⭐⭐⭐⭐ 良好 | 表现良好 |
| 0.7-0.8 | ⭐⭐⭐ 中等 | 表现一般 |
| 0.6-0.7 | ⭐⭐ 及格 | 勉强及格 |
| <0.6 | ⭐ 不及格 | 需要改进 |

---

## 📁 数据文件类型

### 详细评分文件 (`*_scores.csv`)
- 包含每个模型-问题对的详细评分
- 所有评估指标的原始分数
- 用于深入分析和错误诊断

### 汇总统计文件 (`*_summary.csv`)
- 包含每个模型的汇总统计
- 平均值、标准差、最大/最小值
- 用于模型对比和排名

### 报告文件 (`*_report.md`)
- 评估结果的详细分析报告
- 关键发现和模型排名
- 可视化图表说明

---

## 💡 使用技巧

### 1. 快速查看模型表现
```python
import pandas as pd

# 读取汇总文件
summary = pd.read_csv('qa_quality/qa_quality_summary.csv')

# 按综合得分排序
top_models = summary.sort_values('overall_score', ascending=False)
print(top_models[['model', 'overall_score']].head())
```

### 2. 对比特定指标
```python
# 读取详细评分
scores = pd.read_csv('qa_quality/qa_quality_scores.csv')

# 对比EM和F1
comparison = scores[['model', 'exact_match', 'f1_score']]
print(comparison.groupby('model').mean())
```

### 3. 跨任务对比
```python
# 读取多个任务的汇总文件
qa_summary = pd.read_csv('qa_quality/qa_quality_summary.csv')
code_summary = pd.read_csv('code_quality/code_quality_summary.csv')

# 合并对比
combined = pd.merge(
    qa_summary[['model', 'overall_score']], 
    code_summary[['model', 'overall_score']], 
    on='model', 
    suffixes=('_qa', '_code')
)
```

---

## 📚 相关文档

- **[详细指标说明](METRICS_GUIDE.md)** - 完整的指标说明文档
- [目录结构](DIRECTORY_STRUCTURE.md) - 完整目录结构
- [变更日志](CHANGELOG.md) - 目录变更记录
- [README](README.md) - 概述和快速开始

---

## ❓ 常见问题

### Q: 为什么有些指标范围是0-1，有些是0-5？
A: 0-1范围的指标通常是自动化计算的归一化分数；0-5范围的指标（如推理质量）是人工评分，采用5分制更符合人类评判习惯。

### Q: overall_score是如何计算的？
A: overall_score是各项指标的加权平均，权重根据任务类型和指标重要性确定。具体权重见各任务的评估设计文档。

### Q: 标准版和学术版有什么区别？
A: 标准版使用基础评估指标，计算快速；学术版增加更多学术研究常用指标（如BERTScore），评估更全面但计算较慢。

### Q: 如何选择合适的评估版本？
A: 
- 快速对比 → 使用标准版
- 学术研究 → 使用学术版
- 生产环境 → 根据需求选择

---

**文档维护者**：Kiro AI Assistant  
**最后更新**：2026年3月5日
