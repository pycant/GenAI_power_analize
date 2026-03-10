# 质量评分数据生成报告

**生成时间**: 2026-03-07  
**报告版本**: v1.0  
**数据来源**: `data/analize/results/*/quality_*_scores*.csv`

---

## 执行摘要

本报告详细说明了如何生成七个任务类型（代码生成、创意写作、数学推理、问答、逻辑推理、摘要生成、翻译）的质量评分数据文件。这些文件是多维质效比评估体系的核心组成部分，为后续的帕累托分析和综合评估提供质量维度的数据基础。

**核心输出文件**:
- `code_scores_raw.csv` - 代码生成质量评分
- `creative_scores_raw.csv` - 创意写作质量评分
- `math_scores_raw.csv` - 数学推理质量评分
- `qa_scores_raw.csv` - 问答质量评分
- `reasoning_scores_raw.csv` - 逻辑推理质量评分
- `summary_scores_raw.csv` - 摘要生成质量评分
- `translation_scores_raw.csv` - 翻译质量评分

---

## 一、数据生成流程概览

### 1.1 整体架构

```
原始实验数据 (experiments_1/raw/)
    ↓
质量评估脚本 (data/analize/scripts/)
    ↓
任务专用质量评分 (data/analize/results/*/quality_*_scores*.csv)
    ↓
质量评分表格生成器 (create_quality_score_tables.py)
    ↓
标准化质量评分矩阵 (analysis/qe_research/results/quality_scores/*_scores_raw.csv)
```

### 1.2 关键处理步骤

1. **原始数据采集**: 从实验运行中收集模型输出
2. **任务专用评估**: 针对每个任务类型应用特定评估方法
3. **指标计算**: 计算多维度质量指标
4. **数据聚合**: 按模型聚合多个样本的评分
5. **矩阵转换**: 转换为"指标×模型"的标准化格式

---

## 二、各任务类型评估方法


### 2.1 代码生成 (Code)

**数据源**: `data/analize/results/code_quality/quality_scores_code.csv`

**评估指标**:
- `code_length`: 代码长度（行数）
- `compilation_rate`: 编译通过率（0-1）
- `cyclomatic_complexity`: 圈复杂度（代码复杂度指标）
- `has_code`: 是否包含代码（0-1）

**评估方法**:
- 静态代码分析（AST解析）
- 语法检查和编译验证
- 代码复杂度计算
- 代码结构识别

**特点**: 基于规则的自动化评估，客观性强，可重复性高

---

### 2.2 创意写作 (Creative)

**数据源**: `data/analize/results/creative_quality/creative_quality_scores_with_perplexity.csv`

**评估指标**:
- `avg_sentence_length`: 平均句子长度
- `distinct_1`: 一元词汇多样性（Unigram diversity）
- `distinct_2`: 二元词汇多样性（Bigram diversity）
- `metaphor_count`: 隐喻数量

**评估方法**:
- 统计语言学分析（句长、词汇多样性）
- 修辞手法识别（隐喻检测）
- 困惑度计算（使用预训练语言模型）
- 文本流畅度评估

**特点**: 结合统计指标和语言模型评估，平衡客观性和语义理解

---

### 2.3 数学推理 (Math)

**数据源**: `data/analize/results/math_quality/math_quality_scores.csv`

**评估指标**:
- `exact_match`: 精确匹配率（答案完全正确）
- `extracted_answer`: 提取的数值答案
- `extraction_confidence`: 答案提取置信度（0-1）
- `has_answer`: 是否包含答案（0-1）

**评估方法**:
- 答案提取（正则表达式和模式匹配）
- 数值比较（精确匹配或误差范围内匹配）
- 推理过程分析
- 公式识别和验证

**特点**: 以结果正确性为核心，兼顾推理过程评估

---

### 2.4 问答 (QA)

**数据源**: `data/analize/results/qa_quality/qa_quality_scores.csv`

**评估指标**:
- `answer_length`: 答案长度（字符数）
- `avg_paragraph_length`: 平均段落长度
- `certainty_count`: 确定性表达数量
- `confidence_score`: 置信度得分（0-1）

**评估方法**:
- 文本长度统计
- 结构分析（段落划分）
- 语气分析（确定性表达识别）
- 置信度评估

**特点**: 关注答案的完整性、结构性和表达确定性


---

### 2.5 逻辑推理 (Reasoning)

**数据源**: `data/analize/results/reasoning_quality/reasoning_quality_scores.csv`

**评估指标**:
- `avg_sentence_length`: 平均句子长度
- `coherence_score`: 连贯性得分（基于语义相似度）
- `completeness_score`: 完整性得分（0-1）
- `conclusion_correct`: 结论正确性（0-1）

**评估方法**:
- 逻辑链完整性检查
- 推理步骤连贯性分析
- 结论正确性验证
- 论证质量评估

**特点**: 结合自动化指标和人工标注，关注推理过程的逻辑性

---

### 2.6 摘要生成 (Summary)

**数据源**: `data/analize/results/summary_quality/summary_quality_scores_with_bartscore.csv`

**评估指标**:
- `bartscore_avg`: BARTScore平均分（综合质量）
- `bartscore_faith`: BARTScore忠实度（事实一致性）
- `bartscore_info`: BARTScore信息性（信息覆盖度）
- `bertscore_f1`: BERTScore F1分数（语义相似度）

**评估方法**:
- BARTScore评估（基于BART模型的生成质量评分）
  - 忠实度：摘要与原文的事实一致性
  - 信息性：关键信息的覆盖程度
- BERTScore评估（基于BERT嵌入的语义相似度）
- ROUGE指标（n-gram重叠度）

**特点**: 使用先进的神经网络评估方法，关注语义层面的质量

---

### 2.7 翻译 (Translation)

**数据源**: `data/analize/results/translation_quality/translation_quality_scores.csv`

**评估指标**:
- `bertscore_f1`: BERTScore F1分数
- `bertscore_precision`: BERTScore精确率
- `bertscore_recall`: BERTScore召回率
- `bleu_1`: BLEU-1分数（一元语法匹配）

**评估方法**:
- BERTScore评估（多语言语义相似度）
  - Precision: 译文的准确性
  - Recall: 原文信息的保留度
  - F1: 精确率和召回率的调和平均
- BLEU评估（n-gram匹配度）
- 流畅度和准确性综合评估

**特点**: 结合传统机器翻译指标和现代语义评估方法

---

## 三、质量评分表格生成过程

### 3.1 核心脚本

**脚本路径**: `analysis/qe_research/scripts/create_quality_score_tables.py`

**主要功能**:
1. 从各任务的质量评估结果中加载数据
2. 自动检测所有数值型指标列
3. 按模型聚合多个样本的评分（计算平均值）
4. 转换数据格式：从"样本×指标"转为"指标×模型"矩阵
5. 生成两个版本：格式化版本（便于阅读）和原始版本（便于计算）

### 3.2 数据转换流程

```python
# 输入格式（每行一个样本）
model, question_id, metric_1, metric_2, ...
qwen_8b, q1, 0.85, 0.92, ...
qwen_8b, q2, 0.78, 0.88, ...
deepseek_8b, q1, 0.90, 0.85, ...

# 输出格式（指标×模型矩阵）
评分指标 \ 模型, qwen_8b, deepseek_8b, ...
metric_1, 0.815, 0.90, ...
metric_2, 0.90, 0.85, ...
```

### 3.3 指标自动检测

脚本自动识别数值型指标，排除以下元数据列：
- `model`, `question_id`, `experiment_id`, `task_type`
- `prompt`, `response`, `text`, `timestamp`
- `language_pair`, `domain`, `reasoning_type`
- `answer`, `reference`, `source`, `target`

### 3.4 数据聚合策略

- **聚合方法**: 计算每个模型在每个指标上的平均值
- **缺失值处理**: 忽略NaN值，仅对有效数据计算平均
- **精度保留**: 
  - 计数类指标：保留整数
  - 困惑度：保留2位小数
  - 其他评分：保留4位小数（原始版本保留完整精度）

---

## 四、数据质量保证

### 4.1 数据验证

1. **完整性检查**: 确保所有任务类型都有对应的质量评分文件
2. **格式验证**: 检查CSV文件格式和必需列的存在性
3. **数值范围检查**: 验证评分是否在合理范围内
4. **模型覆盖度**: 确保所有实验模型都有评分数据

### 4.2 质量控制措施

- **自动化日志**: 记录所有处理步骤和潜在问题
- **异常检测**: 识别异常值和缺失数据
- **一致性验证**: 确保不同任务间的模型命名一致
- **版本控制**: 保留原始数据和处理后数据的两个版本


---

## 五、评估指标体系总览

### 5.1 指标分类

| 任务类型 | 指标数量　　　　　　 | 主要评估维度　　　　　 | 评估方法类型　|
| ----------| ----------------------| ------------------------| ---------------|
| 代码生成 | 4　　　　　　　　　　| 语法、编译、复杂度　　 | 静态分析　　　|
| 创意写作 | 4　　　　　　　　　　| 流畅度、多样性、修辞　 | 统计+语言模型 |
| 数学推理 | 4　　　　　　　　　　| 答案正确性、提取置信度 | 规则匹配+验证 |
| 问答　　 | 4 长度、结构、置信度 | 文本分析　　　　　　　 | 　　　　　　　|
| 逻辑推理 | 4　　　　　　　　　　| 连贯性、完整性、正确性 | 语义分析+验证 |
| 摘要生成 | 4　　　　　　　　　　| 忠实度、信息性、语义　 | 神经网络评估　|
| 翻译　　 | 4　　　　　　　　　　| 语义相似度、n-gram匹配 | 多语言评估　　|

### 5.2 评估方法分布

- **规则基础方法** (30%): 代码编译、答案匹配、文本统计
- **统计语言学方法** (25%): 词汇多样性、句长、结构分析
- **神经网络方法** (35%): BARTScore, BERTScore, 语义相似度
- **混合方法** (10%): 结合多种评估技术

### 5.3 指标特性

**客观性指标** (高可重复性):
- 代码编译率、精确匹配、BLEU、词汇多样性

**语义指标** (需要语言理解):
- BARTScore、BERTScore、连贯性、忠实度

**结构指标** (关注形式):
- 代码复杂度、句子长度、段落结构

**正确性指标** (需要标准答案):
- 数学答案正确性、推理结论正确性

---

## 六、模型评估覆盖

### 6.1 评估模型列表

本次评估涵盖12个模型配置：

| 模型名称　　　　　　| 参数规模 | 量化方式 | 来源　　　　|     |
| ---------------------| ----------| ----------| -------------| -----|
| deepseek_8b_ol_q4km | 8B　　　 | Q4_K_M　 | Ollama　　　|     |
| gemma_2b_hf_4bit　　| 2B　　　 | 4-bit　　| HuggingFace |     |
| gemma_2b_hf_8bit　　| 2B　　　 | 8-bit　　| HuggingFace |     |
| gemma_4b_ol_q4km　　| 4B　　　 | Q4_K_M　 | Ollama　　　|     |
| phi3_4b_hf_4bit　　 | 4B　　　 | 4-bit　　| HuggingFace |     |
| phi3_4b_hf_8bit　　 | 4B　　　 | 8-bit　　| HuggingFace |     |
| qwen25_3b_hf_4bit　 | 3B　　　 | 4-bit　　| HuggingFace |     |
| qwen25_3b_hf_8bit　 | 3B　　　 | 8-bit　　| HuggingFace |     |
| qwen25_7b_hf_4bit　 | 7B　　　 | 4-bit　　| HuggingFace |     |
| qwen25_7b_hf_8bit　 | 7B　　　 | 8-bit　　| HuggingFace |     |
| qwen_4b_ol_q4km　　 | 4B　　　 | Q　　　　| Ollama　　　|     |
| qwen_8b_ol_q4km　　 | 8B　　　 | Q4_K_M　 | Ollama　　　|     |

### 6.2 量化方式对比

- **Q4_K_M** (Ollama): 4-bit量化，混合精度
- **4-bit** (HuggingFace): 4-bit量化，使用bitsandbytes
- **8-bit** (HuggingFace): 8-bit量化，更高精度

### 6.3 任务覆盖度

- 所有7个任务类型均有完整评估
- 每个任务包含多个测试样本（通常5-10个）
- 每个模型在每个任务上都有评分数据

---

## 七、数据文件说明

### 7.1 输出文件结构

```
analysis/qe_research/results/quality_scores/
├── code_scores.csv                    # 代码生成（格式化）
├── code_scores_raw.csv                # 代码生成（原始）
├── creative_scores.csv                # 创意写作（格式化）
├── creative_scores_raw.csv            # 创意写作（原始）
├── math_scores.csv                    # 数学推理（格式化）
├── math_scores_raw.csv                # 数学推理（原始）
├── qa_scores.csv                      # 问答（格式化）
├── qa_scores_raw.csv                  # 问答（原始）
├── reasoning_scores.csv               # 逻辑推理（格式化）
├── reasoning_scores_raw.csv           # 逻辑推理（原始）
├── summary_scores.csv                 # 摘要生成（格式化）
├── summary_scores_raw.csv             # 摘要生成（原始）
├── translation_scores.csv             # 翻译（格式化）
├── translation_scores_raw.csv         # 翻译（原始）
├── aggregated_scores_by_task.csv      # 跨任务聚合
└── README.md                          # 使用说明
```

### 7.2 文件版本说明

**格式化版本** (`*_scores.csv`):
- 数值已格式化，便于人工阅读
- 计数类指标显示为整数
- 评分类指标保留2-4位小数

**原始版本** (`*_scores_raw.csv`):
- 保留完整数值精度
- 用于后续计算和分析
- 避免精度损失

### 7.3 数据使用示例

```python
import pandas as pd

# 读取代码生成质量评分
code_scores = pd.read_csv('code_scores_raw.csv', index_col=0)

# 查看特定指标的所有模型得分
print(code_scores.loc['compilation_rate'])

# 查看特定模型的所有指标
print(code_scores['qwen25_7b_hf_4bit'])

# 找出编译率最高的模型
best_model = code_scores.loc['compilation_rate'].idxmax()
print(f"编译率最高: {best_model}")
```

---

## 八、后续应用

### 8.1 帕累托分析

这些质量评分数据是帕累托分析的核心输入：
- 质量维度：从质量评分表中提取
- 效率维度：从实验运行数据中提取（延迟、吞吐量）
- 能耗维度：从功耗监控数据中提取

### 8.2 综合评估

质量评分与效率、能耗指标结合，计算：
- **质效比** (Q/E Ratio): 质量与效率的权衡
- **能效比** (Performance per Watt): 性能与能耗的比值
- **综合得分**: 多维度加权评分

### 8.3 模型排名

基于质量评分进行：
- 任务专用排名：每个任务的最佳模型
- 综合排名：跨任务的整体表现
- 量化方式对比：不同量化方法的影响分析

---

## 九、技术细节

### 9.1 依赖环境

```bash
# Python环境
Python 3.10+
pandas >= 1.5.0
numpy >= 1.23.0

# 评估工具
transformers >= 4.36.0  # BERTScore, BARTScore
torch >= 2.1.0          # 神经网络评估
```

### 9.2 运行命令

```bash
# 激活环境
conda activate bartscore

# 生成质量评分表格
python analysis/qe_research/scripts/create_quality_score_tables.py

# 输出位置
# analysis/qe_research/results/quality_scores/
```

### 9.3 处理时间

- 单个任务处理：< 1秒
- 全部7个任务：< 5秒
- 主要时间消耗：CSV读取和数据聚合

---

## 十、总结

### 10.1 核心成果

1. **标准化评分矩阵**: 7个任务 × 12个模型 × 28个指标
2. **多维度评估**: 涵盖语法、语义、结构、正确性等多个维度
3. **自动化流程**: 从原始数据到标准化评分的完整管道
4. **双版本输出**: 兼顾可读性和计算精度

### 10.2 数据特点

- **全面性**: 覆盖7种典型NLP任务
- **客观性**: 基于自动化评估方法，可重复验证
- **标准化**: 统一的数据格式和命名规范
- **可扩展**: 易于添加新任务、新模型、新指标

### 10.3 应用价值

这些质量评分数据为多维质效比评估体系提供了坚实的质量维度基础，支持：
- 模型性能横向对比
- 量化方式影响分析
- 任务适配性评估
- 质效权衡决策

---

## 附录

### A. 相关文档

- [METRICS_GUIDE.md](../../../data/analize/results/METRICS_GUIDE.md) - 完整指标说明
- [README.md](./README.md) - 质量评分表格使用指南
- [PARETO_ANALYSIS_GUIDE.md](../PARETO_ANALYSIS_GUIDE.md) - 帕累托分析指南

### B. 数据来源追溯

| 任务类型　　| 原始数据路径　　　　　　　　　　　　　　　　| 评估脚本　　　　　　　　　　　　　|
| -------------| ---------------------------------------------| -----------------------------------|
| Code　　　　| `data/analize/results/code_quality/`　　　　| `evaluate_code_quality.py`　　　　|
| Creative　　| `data/analize/results/creative_quality/`　　| `evaluate_creative_quality.py`　　|
| Math　　　　| `data/analize/results/math_quality/`　　　　| `evaluate_math_quality.py`　　　　|
| QA　　　　　| `data/analize/results/qa_quality/`　　　　　| `evaluate_qa_quality_academic.py` |
| Reasoning　 | `data/analize/results/reasoning_quality/`　 | `evaluate_reasoning_quality.py`　 |
| Summary　　 | `data/analize/results/summary_quality/`　　 | `evaluate_summary_quality.py`　　 |
| Translation | `data/analize/results/translation_quality/` | `evaluate_translation_quality.py` |

### C. 更新日志

- **2026-03-07**: 初始版本，包含7个任务类型的质量评分数据
- 后续更新将记录在此

---

**报告生成**: `analysis/qe_research/scripts/create_quality_score_tables.py`  
**最后更新**: 2026-03-07  
**维护者**: GenAI质效比评估项目组
4_K_M　 | ------　　　| -------------- |