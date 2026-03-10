# 质量评估指标说明文档

本文档详细说明了各个任务类型下质量评估所包含的指标及其含义，方便快速理解数据文件的内容。

---

## 目录

1. [代码生成质量 (Code Quality)](#1-代码生成质量-code-quality)
2. [创意写作质量 (Creative Quality)](#2-创意写作质量-creative-quality)
3. [数学推理质量 (Math Quality)](#3-数学推理质量-math-quality)
4. [问答质量 (QA Quality)](#4-问答质量-qa-quality)
5. [逻辑推理质量 (Reasoning Quality)](#5-逻辑推理质量-reasoning-quality)
6. [摘要生成质量 (Summary Quality)](#6-摘要生成质量-summary-quality)
7. [翻译质量 (Translation Quality)](#7-翻译质量-translation-quality)

---

## 1. 代码生成质量 (Code Quality)

**目录位置：** `data/analize/results/code_quality/`

### 核心指标

| 指标名称 | 英文名称 | 取值范围 | 说明 |
|---------|---------|---------|------|
| 语法正确性 | syntax_correctness | 0-1 | 代码是否符合语法规范，能否通过编译/解析 |
| 功能完整性 | functionality_completeness | 0-1 | 代码是否实现了要求的功能 |
| 代码质量 | code_quality | 0-1 | 代码的可读性、结构性、注释完整性 |
| 最佳实践 | best_practices | 0-1 | 是否遵循编程最佳实践和规范 |
| 综合得分 | overall_score | 0-1 | 上述指标的加权平均 |

### 数据文件

- `quality_scores_code.csv` - 详细评分数据（每个模型-问题对）
- `quality_summary_code.csv` - 汇总统计数据（每个模型的平均分）

### 评估方法

- 基于规则的静态分析
- 语法检查（AST解析）
- 代码风格检查
- 功能测试（如适用）

---

## 2. 创意写作质量 (Creative Quality)

**目录位置：** `data/analize/results/creative_quality/`

### 核心指标

| 指标名称　 | 英文名称　　　| 取值范围 | 说明　　　　　　　　　　　 |
| ------------| ---------------| ----------| ----------------------------|
| 流畅度　　 | fluency　　　 | 0-1　　　| 文本的语言流畅性和可读性　 |
| 连贯性　　 | coherence　　 | 0-1　　　| 文本的逻辑连贯性和结构性　 |
| 创意性　　 | creativity　　| 0-1　　　| 内容的新颖性和想象力　　　 |
| 相关性　　 | relevance　　 | 0-1　　　| 内容与主题的相关程度　　　 |
| 词汇多样性 | distinct_2　　| 0-1　　　| 基于bigram的词汇多样性指标 |
| 困惑度　　 | perplexity　　| >0　　　 | 语言模型困惑度（越低越好） |
| 综合得分　 | overall_score | 0-1　　　| 多指标加权平均　　　　　　 |

### 数据文件

- `creative_quality_scores.csv` - 基础评分数据
- `creative_quality_scores_detailed.csv` - 详细评分（包含各维度）
- `creative_quality_scores_with_perplexity.csv` - 包含困惑度的评分
- `creative_quality_summary.csv` - 汇总统计
- `creative_task_model_matching.csv` - 任务-模型匹配分析

### 评估方法

- GPT-4辅助评分（流畅度、连贯性、创意性、相关性）
- 统计指标计算（distinct-2）
- 语言模型困惑度计算

---

## 3. 数学推理质量 (Math Quality)

**目录位置：** `data/analize/results/math_quality/`

### 核心指标

| 指标名称 | 英文名称 | 取值范围 | 说明 |
|---------|---------|---------|------|
| 答案正确性 | answer_correctness | 0-1 | 最终答案是否正确 |
| 推理过程 | reasoning_process | 0-1 | 推理步骤的完整性和正确性 |
| 公式使用 | formula_usage | 0-1 | 数学公式使用的准确性 |
| 步骤清晰度 | step_clarity | 0-1 | 解题步骤的清晰程度 |
| 综合得分 | overall_score | 0-1 | 多维度综合评分 |

### 数据文件

- `math_quality_scores.csv` - 详细评分数据
- `math_quality_summary.csv` - 汇总统计数据

### 评估方法

- 答案匹配（精确匹配或数值比较）
- GPT-4辅助评估推理过程
- 步骤完整性分析

---

## 4. 问答质量 (QA Quality)

**目录位置：** `data/analize/results/qa_quality/`

### 核心指标

| 指标名称 | 英文名称 | 取值范围 | 说明 |
|---------|---------|---------|------|
| 精确匹配 | exact_match (EM) | 0-1 | 答案是否与标准答案完全匹配 |
| F1分数 | f1_score | 0-1 | 基于词级别的精确率和召回率的调和平均 |
| BLEU分数 | bleu_score | 0-1 | 机器翻译质量评估指标，衡量n-gram重叠 |
| ROUGE-L | rouge_l | 0-1 | 基于最长公共子序列的相似度 |
| BERTScore | bert_score | 0-1 | 基于BERT嵌入的语义相似度 |
| 答案完整性 | answer_completeness | 0-1 | 答案是否包含所有必要信息 |
| 答案相关性 | answer_relevance | 0-1 | 答案与问题的相关程度 |
| 综合得分 | overall_score | 0-1 | 多指标加权平均 |

### 数据文件

- `qa_quality_scores.csv` - 详细评分数据（标准版）
- `qa_quality_scores_academic.csv` - 学术版评分数据
- `qa_quality_summary.csv` - 汇总统计（标准版）
- `qa_quality_summary_academic.csv` - 汇总统计（学术版）

### 评估方法

- 自动化指标计算（EM, F1, BLEU, ROUGE, BERTScore）
- GPT-4辅助评估（完整性、相关性）
- 多参考答案支持

### 版本说明

- **标准版**：使用基础评估指标
- **学术版**：增加更多学术研究常用指标，评估更全面

---

## 5. 逻辑推理质量 (Reasoning Quality)

**目录位置：** `data/analize/results/reasoning_quality/`

### 核心指标

| 指标名称 | 英文名称 | 取值范围 | 说明 |
|---------|---------|---------|------|
| 结论正确性 | conclusion_correctness | 0-5 | 推理结论的正确程度（5分制） |
| 推理完整性 | reasoning_completeness | 0-5 | 推理步骤的完整程度（5分制） |
| 逻辑连贯性 | logical_coherence | 0-5 | 推理过程的逻辑连贯性（5分制） |
| 论证深度 | argumentation_depth | 0-5 | 论证的深度和细致程度（5分制） |
| 推理步骤数 | step_count | ≥0 | 推理过程包含的步骤数量 |
| 推理类型 | reasoning_type | 分类 | 演绎/归纳/类比/因果等推理类型 |
| 综合得分 | overall_score | 0-1 | 归一化后的综合评分 |

### 数据文件

- `reasoning_quality_scores.csv` - 详细评分数据
- `reasoning_quality_summary.csv` - 汇总统计
- `manual_scores.csv` - 人工评分原始数据
- `manual_scores_filled.csv` - 填充后的人工评分
- `manual_scores_by_question.csv` - 按问题汇总的评分
- `manual_scores_summary.csv` - 人工评分汇总统计

### 评估方法

- **人工评分**：专家按照评分标准进行5分制评分
- **自动化辅助**：GPT-4辅助识别推理类型和步骤
- **多维度评估**：从正确性、完整性、连贯性、深度等多个维度评估

### 评分标准

每个维度采用5分制：
- **5分**：优秀 - 完全符合标准
- **4分**：良好 - 基本符合，有小瑕疵
- **3分**：中等 - 部分符合，有明显不足
- **2分**：较差 - 大部分不符合
- **1分**：很差 - 完全不符合

---

## 6. 摘要生成质量 (Summary Quality)

**目录位置：** `data/analize/results/summary_quality/`

### 核心指标

| 指标名称 | 英文名称 | 取值范围 | 说明 |
|---------|---------|---------|------|
| ROUGE-1 | rouge_1 | 0-1 | 基于unigram的召回率 |
| ROUGE-2 | rouge_2 | 0-1 | 基于bigram的召回率 |
| ROUGE-L | rouge_l | 0-1 | 基于最长公共子序列的F1分数 |
| BERTScore | bert_score | 0-1 | 基于BERT嵌入的语义相似度 |
| BARTScore | bart_score | 实数 | 基于BART的生成质量评分 |
| 压缩比 | compression_ratio | 0-1 | 摘要长度与原文长度的比值 |
| 信息密度 | information_density | 0-1 | 单位长度内包含的信息量 |
| 字数符合度 | length_compliance | 0-1 | 摘要长度是否符合要求 |
| 综合得分 | overall_score | 0-1 | 多指标加权平均 |

### 数据文件

- `summary_quality_scores.csv` - 基础评分数据
- `summary_quality_scores_with_bartscore.csv` - 包含BARTScore的评分
- `summary_quality_summary.csv` - 汇总统计
- `summary_bartscore_summary.csv` - BARTScore专项汇总

### 评估方法

- **ROUGE指标**：与参考摘要的n-gram重叠度
- **BERTScore**：语义相似度评估
- **BARTScore**：生成质量评估（需要大模型）
- **统计指标**：压缩比、信息密度、长度符合度

### 指标解读

- **ROUGE-1/2/L**：越高表示与参考摘要越相似
- **BERTScore**：越高表示语义保留越好
- **BARTScore**：越高表示生成质量越好
- **压缩比**：适中为佳（通常0.2-0.3）
- **信息密度**：越高表示信息提取越精炼

---

## 7. 翻译质量 (Translation Quality)

**目录位置：** `data/analize/results/translation_quality/`

### 核心指标

| 指标名称 | 英文名称 | 取值范围 | 说明 |
|---------|---------|---------|------|
| BLEU分数 | bleu_score | 0-1 | 机器翻译标准评估指标 |
| 语义保真度 | semantic_fidelity | 0-1 | 译文与原文的语义一致性 |
| 流畅度 | fluency | 0-1 | 译文的语言流畅性 |
| 术语准确性 | terminology_accuracy | 0-1 | 专业术语翻译的准确性 |
| 文化适应性 | cultural_adaptation | 0-1 | 译文的文化适应程度 |
| 语言对 | language_pair | 分类 | 源语言-目标语言对（如en-zh） |
| 领域类型 | domain | 分类 | 翻译内容的领域（技术/文学/日常等） |
| 综合得分 | overall_score | 0-1 | 多维度综合评分 |

### 数据文件

- `translation_quality_scores.csv` - 详细评分数据
- `translation_quality_summary.csv` - 汇总统计数据

### 评估方法

- **BLEU计算**：与参考译文的n-gram匹配度
- **GPT-4辅助评估**：语义保真度、流畅度、术语准确性、文化适应性
- **多参考译文支持**：可使用多个参考译文提高评估准确性

### 语言对说明

常见语言对：
- `en-zh`：英文→中文
- `zh-en`：中文→英文
- `en-ja`：英文→日文
- `ja-zh`：日文→中文

---

## 通用字段说明

所有任务类型的数据文件都包含以下通用字段：

| 字段名称 | 说明 |
|---------|------|
| model | 模型名称（如qwen3_8b, deepseek-r1_8b等） |
| question_id | 问题编号 |
| task_type | 任务类型 |
| timestamp | 评估时间戳 |
| overall_score | 综合得分（0-1范围，归一化后） |

---

## 数据文件类型说明

### 1. 详细评分文件 (`*_scores.csv`)

包含每个模型-问题对的详细评分，字段包括：
- 所有评估指标的原始分数
- 中间计算结果
- 元数据信息

**用途**：深入分析、问题级别对比、错误分析

### 2. 汇总统计文件 (`*_summary.csv`)

包含每个模型的汇总统计，字段包括：
- 各指标的平均值
- 标准差
- 最大/最小值
- 样本数量

**用途**：模型对比、整体性能评估、排名分析

### 3. 报告文件 (`*_report.md`)

包含评估结果的详细分析报告，内容包括：
- 评估概述
- 关键发现
- 模型排名
- 详细分析
- 可视化图表说明

**用途**：快速了解评估结果、生成报告、分享发现

---

## 评分归一化说明

为了便于跨任务对比，所有综合得分（overall_score）都归一化到0-1范围：

- **0.9-1.0**：优秀
- **0.8-0.9**：良好
- **0.7-0.8**：中等
- **0.6-0.7**：及格
- **<0.6**：不及格

---

## 使用建议

### 1. 快速查看

查看 `*_summary.csv` 文件获取模型整体表现。

### 2. 深入分析

查看 `*_scores.csv` 文件进行问题级别的详细分析。

### 3. 理解评估

阅读 `*_report.md` 文件了解评估方法和关键发现。

### 4. 可视化分析

查看 `figures/` 目录下的图表进行可视化分析。

### 5. 跨任务对比

使用归一化的 `overall_score` 进行跨任务模型性能对比。

---

## 更新日志

- **2026-03-05**：创建初始版本，包含7种任务类型的指标说明
- **2026-03-05**：合并QA任务的两个版本到统一目录

---

## 相关文档

- [评估系统指南](../scripts/EVALUATION_SYSTEM_GUIDE.md)
- [可视化快速指南](../visualization/VISUALIZATION_QUICK_GUIDE.md)
- [数据目录结构](DIRECTORY_STRUCTURE.md)
- [快速开始指南](../QUICK_START.md)

---

**文档维护者**：Kiro AI Assistant  
**最后更新**：2026年3月5日
