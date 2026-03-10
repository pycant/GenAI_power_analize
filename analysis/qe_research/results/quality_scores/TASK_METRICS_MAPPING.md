# 任务-质量指标对应表

本文档整理了各任务类型使用的质量评估指标及其说明。

**自动生成**: 本文档由脚本 `generate_task_metrics_mapping.py` 自动生成

---

## 任务指标汇总

| 任务类型 | 中文名称 | 指标数量 | 核心指标 | 数据文件 |
|---------|---------|---------|---------|---------|
| Code Generation | 代码生成 | 7 | 编译通过率 | `code_scores_raw.csv` |
| Creative Writing | 创意写作 | 13 | 词汇多样性-2 | `creative_scores_raw.csv` |
| Math Reasoning | 数学推理 | 10 | 精确匹配率 | `math_scores_raw.csv` |
| Question Answering | 问答 | 14 | 置信度得分 | `qa_scores_raw.csv` |
| Summarization | 摘要生成 | 22 | BARTScore平均分 | `summary_scores_raw.csv` |
| Translation | 翻译 | 11 | BLEU | `translation_scores_raw.csv` |
| Reasoning | 推理 | 16 | 准确率 | `reasoning_scores_raw.csv` |

---
## 代码生成任务 (Code Generation)

**数据文件**: `code_scores_raw.csv`

| 指标名称 | 英文名称 | 指标说明 | 优化方向 |
|---------|---------|---------|---------|
| 代码长度 | code_length | 生成代码的平均行数 | 适中为佳 |
| 编译通过率 | compilation_rate | 代码能够成功编译的比例 | 越高越好 ↑ |
| 圈复杂度 | cyclomatic_complexity | 代码的逻辑复杂度（分支数量） | 适中为佳 |
| 包含代码 | has_code | 输出中是否包含代码块 | 1为合格 |
| test_pass_rate | test_pass_rate | 通过测试用例的比例 | 越高越好 ↑ |
| tests_passed | tests_passed | 通过的测试用例数量 | 适中为佳 |
| tests_total | tests_total | 总测试用例数量 | 适中为佳 |

**核心指标**: 编译通过率 (compilation_rate)
**指标数量**: 7

---
## 创意写作任务 (Creative Writing)

**数据文件**: `creative_scores_raw.csv`

| 指标名称 | 英文名称 | 指标说明 | 优化方向 |
|---------|---------|---------|---------|
| 平均句长 | avg_sentence_length | 每句话的平均词数 | 适中为佳 |
| 词汇多样性-1 | distinct_1 | 不重复单词（unigram）占比 | 越高越好 ↑ |
| 词汇多样性-2 | distinct_2 | 不重复二元组（bigram）占比 | 越高越好 ↑ |
| 隐喻数量 | metaphor_count | 检测到的隐喻修辞数量 | 越高越好 ↑ |
| parallelism_count | parallelism_count | 检测到的排比修辞数量 | 越高越好 ↑ |
| perplexity | perplexity | 语言模型困惑度（越低表示文本越流畅） | 越低越好 ↓ |
| personification_count | personification_count | 检测到的拟人修辞数量 | 越高越好 ↑ |
| repetition_count | repetition_count | 检测到的重复修辞数量 | 适中为佳 |
| sentence_count | sentence_count | 输出中的句子数量 | 适中为佳 |
| text_length | text_length | 输出文本的总长度 | 适中为佳 |
| token_count | token_count | 文本的总词元数 | 适中为佳 |
| total_rhetorical_devices | total_rhetorical_devices | 检测到的修辞手法总数 | 越高越好 ↑ |
| unique_token_ratio | unique_token_ratio | 独特词元占总词元的比例 | 越高越好 ↑ |

**核心指标**: 词汇多样性-2 (distinct_2)
**指标数量**: 13

---
## 数学推理任务 (Math Reasoning)

**数据文件**: `math_scores_raw.csv`

| 指标名称 | 英文名称 | 指标说明 | 优化方向 |
|---------|---------|---------|---------|
| 精确匹配 | exact_match | 答案与标准答案完全一致的比例 | 越高越好 ↑ |
| 提取答案 | extracted_answer | 从输出中提取的数值答案 | 适中为佳 |
| 提取置信度 | extraction_confidence | 答案提取的置信度 | 越高越好 ↑ |
| 包含答案 | has_answer | 输出中是否包含答案 | 1为合格 |
| has_calculation | has_calculation | 输出中是否包含计算过程 | 1为合格 |
| has_reasoning | has_reasoning | 输出中是否包含推理过程 | 1为合格 |
| numerical_match | numerical_match | 数值答案的匹配程度 | 越高越好 ↑ |
| reference_answer | reference_answer | 参考答案的数值 | 适中为佳 |
| step_count | step_count | 推理步骤数量 | 适中为佳 |
| text_length | text_length | 输出文本的总长度 | 适中为佳 |

**核心指标**: 精确匹配率 (exact_match)
**指标数量**: 10

---
## 问答任务 (Question Answering)

**数据文件**: `qa_scores_raw.csv`

| 指标名称 | 英文名称 | 指标说明 | 优化方向 |
|---------|---------|---------|---------|
| 答案长度 | answer_length | 生成答案的字符数 | 适中为佳 |
| 平均段落长度 | avg_paragraph_length | 每段的平均字符数 | 适中为佳 |
| 确定性词汇数 | certainty_count | 表达确定性的词汇数量 | 适中为佳 |
| 置信度得分 | confidence_score | 答案的整体置信度 | 越高越好 ↑ |
| 包含答案 | has_answer | 输出中是否包含答案 | 1为合格 |
| has_conclusion | has_conclusion | 输出中是否包含结论 | 1为合格 |
| has_enumeration | has_enumeration | 输出中是否包含列举内容 | 1为合格 |
| has_examples | has_examples | 输出中是否包含示例 | 1为合格 |
| has_reasoning | has_reasoning | 输出中是否包含推理过程 | 1为合格 |
| paragraph_count | paragraph_count | 输出中的段落数量 | 适中为佳 |
| 推理步骤数 | reasoning_steps | 推理步骤的数量 | 适中为佳 |
| technical_term_count | technical_term_count | 专业术语的数量 | 适中为佳 |
| technical_term_density | technical_term_density | 专业术语密度（术语数/总词数） | 适中为佳 |
| uncertainty_count | uncertainty_count | 表达不确定性的词汇数量 | 适中为佳 |

**核心指标**: 置信度得分 (confidence_score)
**指标数量**: 14

---
## 摘要生成任务 (Summarization)

**数据文件**: `summary_scores_raw.csv`

| 指标名称 | 英文名称 | 指标说明 | 优化方向 |
|---------|---------|---------|---------|
| BARTScore平均 | bartscore_avg | 基于BART的语义相似度平均分 | 越接近0越好 ↑ |
| BARTScore忠实度 | bartscore_faith | 摘要对原文的忠实度 | 越接近0越好 ↑ |
| BARTScore信息量 | bartscore_info | 摘要包含的信息量 | 越接近0越好 ↑ |
| BERTScore F1 | bertscore_f1 | 基于BERT的语义相似度F1值 | 越高越好 ↑ |
| BERTScore精确率 | bertscore_precision | 基于BERT的精确率 | 越高越好 ↑ |
| BERTScore召回率 | bertscore_recall | 基于BERT的召回率 | 越高越好 ↑ |
| compliance_score | compliance_score | 摘要长度符合要求的程度 | 越高越好 ↑ |
| compression_ratio | compression_ratio | 摘要长度与原文长度的比值 | 适中为佳 |
| deviation | deviation | 摘要长度与目标长度的偏差 | 越低越好 ↓ |
| in_range | in_range | 摘要长度是否在目标范围内 | 1为合格 |
| information_density | information_density | 单位长度内包含的信息量 | 越高越好 ↑ |
| length | length | 摘要的字符长度 | 适中为佳 |
| rouge_1_f1 | rouge_1_f1 | ROUGE-1的F1分数（unigram重叠） | 越高越好 ↑ |
| rouge_1_precision | rouge_1_precision | ROUGE-1的精确率 | 越高越好 ↑ |
| rouge_1_recall | rouge_1_recall | ROUGE-1的召回率 | 越高越好 ↑ |
| rouge_2_f1 | rouge_2_f1 | ROUGE-2的F1分数（bigram重叠） | 越高越好 ↑ |
| rouge_2_precision | rouge_2_precision | ROUGE-2的精确率 | 越高越好 ↑ |
| rouge_2_recall | rouge_2_recall | ROUGE-2的召回率 | 越高越好 ↑ |
| rouge_l_f1 | rouge_l_f1 | ROUGE-L的F1分数（最长公共子序列） | 越高越好 ↑ |
| rouge_l_precision | rouge_l_precision | ROUGE-L的精确率 | 越高越好 ↑ |
| rouge_l_recall | rouge_l_recall | ROUGE-L的召回率 | 越高越好 ↑ |
| source_length | source_length | 原文的字符长度 | 适中为佳 |

**核心指标**: BARTScore平均分 (bartscore_avg)
**指标数量**: 22

---
## 翻译任务 (Translation)

**数据文件**: `translation_scores_raw.csv`

| 指标名称 | 英文名称 | 指标说明 | 优化方向 |
|---------|---------|---------|---------|
| BERTScore F1 | bertscore_f1 | 基于BERT的语义相似度F1值 | 越高越好 ↑ |
| BERTScore精确率 | bertscore_precision | 基于BERT的精确率 | 越高越好 ↑ |
| BERTScore召回率 | bertscore_recall | 基于BERT的召回率 | 越高越好 ↑ |
| BLEU-1 | bleu_1 | BLEU-1分数（单词级n-gram匹配） | 越高越好 ↑ |
| BLEU-2 | bleu_2 | BLEU-2分数（二元组级n-gram匹配） | 越高越好 ↑ |
| BLEU-4 | bleu_4 | BLEU-4分数（四元组级n-gram匹配） | 越高越好 ↑ |
| chrf | chrf | 字符级F分数（character n-gram F-score） | 越高越好 ↑ |
| edit_distance | edit_distance | 编辑距离（需要的最少编辑操作数） | 越低越好 ↓ |
| edit_similarity | edit_similarity | 编辑相似度（1 - 归一化编辑距离） | 越高越好 ↑ |
| length_ratio | length_ratio | 译文长度与原文长度的比值 | 适中为佳 |
| normalized_edit_distance | normalized_edit_distance | 归一化编辑距离（编辑距离/最大长度） | 越低越好 ↓ |

**核心指标**: BLEU (bleu_1)
**指标数量**: 11

---
## 推理任务 (Reasoning)

**数据文件**: `reasoning_scores_raw.csv`

| 指标名称 | 英文名称 | 指标说明 | 优化方向 |
|---------|---------|---------|---------|
| 平均句长 | avg_sentence_length | 每句话的平均词数 | 适中为佳 |
| coherence_score | coherence_score | 推理过程的逻辑连贯性得分 | 越高越好 ↑ |
| completeness_score | completeness_score | 推理过程的完整性得分 | 越高越好 ↑ |
| conclusion_correct | conclusion_correct | 推理结论的正确性 | 越高越好 ↑ |
| conclusion_f1 | conclusion_f1 | 结论与参考答案的F1分数 | 越高越好 ↑ |
| connector_density | connector_density | 逻辑连接词密度 | 越高越好 ↑ |
| depth_score | depth_score | 推理深度得分 | 越高越好 ↑ |
| 提取置信度 | extraction_confidence | 答案提取的置信度 | 越高越好 ↑ |
| has_conclusion | has_conclusion | 输出中是否包含结论 | 1为合格 |
| has_logical_connectors | has_logical_connectors | 输出中是否包含逻辑连接词 | 1为合格 |
| has_premise | has_premise | 输出中是否包含前提 | 1为合格 |
| has_reasoning_steps | has_reasoning_steps | 输出中是否包含推理步骤 | 1为合格 |
| keyword_coverage | keyword_coverage | 关键词覆盖率 | 越高越好 ↑ |
| reasoning_keyword_count | reasoning_keyword_count | 推理关键词数量 | 适中为佳 |
| sentence_count | sentence_count | 输出中的句子数量 | 适中为佳 |
| step_count | step_count | 推理步骤数量 | 适中为佳 |

**核心指标**: 准确率 (accuracy)
**指标数量**: 16

---
## 指标分类

### 按评估维度分类

#### 1. 准确性指标
- **精确匹配类**: exact_match, compilation_rate, accuracy
- **相似度类**: BLEU, ROUGE, BERTScore
- **语义评分类**: BARTScore

#### 2. 多样性指标
- **词汇多样性**: distinct_1, distinct_2
- **修辞丰富度**: metaphor_count

#### 3. 结构指标
- **长度类**: code_length, answer_length, avg_sentence_length
- **复杂度类**: cyclomatic_complexity

#### 4. 置信度指标
- **确定性**: confidence_score, certainty_count, extraction_confidence

---

**生成时间**: 2026-03-09
**数据版本**: v3.0
**评估模型数量**: 12个主流开源语言模型
