# 质量评估结果总索引

**最后更新**: 2026-03-05

本目录包含所有任务类型的质量评估结果，采用统一的目录结构和命名规范。

---

## 📁 目录结构

```
data/analize/results/
├── aggregate/                    # 综合分析结果
│   ├── AGGREGATE_REPORT.md      # 综合分析报告
│   ├── aggregate_all_tasks.csv  # 所有任务原始数据
│   ├── aggregate_normalized.csv # 归一化数据
│   ├── model_ranking.csv        # 模型综合排名
│   ├── task_statistics.csv      # 任务统计信息
│   └── figures/                 # 综合可视化图表
├── code_quality/                # 代码生成任务
├── creative_quality/            # 创意写作任务
├── math_quality/                # 数学推理任务
├── qa_quality/                  # 问答任务
├── reasoning_quality/           # 逻辑推理任务
├── summary_quality/             # 文本摘要任务
└── translation_quality/         # 翻译任务
```

---

## 📊 任务类型概览

### 1. 代码生成 (Code Generation)

**目录**: `code_quality/`

**评估维度**:
- 语法正确性 (Syntax Correctness)
- 功能完整性 (Functionality)
- 代码质量 (Code Quality)
- 可读性 (Readability)

**关键文件**:
- `code_quality_scores.csv` - 详细评分数据
- `code_quality_summary.csv` - 汇总统计
- `code_quality_report.md` - 分析报告
- `figures/` - 可视化图表

**评估方法**: 静态分析 + 编译检查 + 代码质量工具

---

### 2. 创意写作 (Creative Writing)

**目录**: `creative_quality/`

**评估维度**:
- 多样性 (Diversity) - Distinct-1/2/3
- 连贯性 (Coherence)
- 创造性 (Creativity)
- 困惑度 (Perplexity)

**关键文件**:
- `creative_quality_scores.csv` - 详细评分
- `creative_quality_scores_with_perplexity.csv` - 包含困惑度的评分
- `creative_quality_summary.csv` - 汇总统计
- `CREATIVE_EVALUATION_REPORT.md` - 完整报告
- `PERPLEXITY_ANALYSIS_SUMMARY.md` - 困惑度分析
- `figures/` - 13张可视化图表

**评估方法**: N-gram多样性 + 困惑度 + 语义连贯性

---

### 3. 数学推理 (Mathematical Reasoning)

**目录**: `math_quality/`

**评估维度**:
- 答案正确性 (Correctness)
- 推理质量 (Reasoning Quality)
- 步骤完整性 (Step Completeness)

**关键文件**:
- `math_quality_scores.csv` - 详细评分
- `math_quality_summary.csv` - 汇总统计
- `math_quality_report.md` - 分析报告
- `figures/` - 可视化图表

**评估方法**: 答案匹配 + 推理步骤分析

---

### 4. 问答 (Question Answering)

**目录**: `qa_quality/` 和 `qa_quality_academic/`

**评估维度**:
- 精确匹配 (Exact Match)
- F1分数 (F1 Score)
- 语义相似度 (Semantic Similarity - BERTScore)

**关键文件**:
- `qa_quality_scores.csv` - 详细评分
- `qa_quality_summary.csv` - 汇总统计
- `qa_quality_report.md` - 分析报告
- `qa_quality_academic/` - 学术版本评估（包含更多图表）
- `figures/` - 可视化图表

**评估方法**: EM + Token-level F1 + BERTScore

**注意**: `qa_quality_academic/` 是学术版本的评估结果，包含更详细的分析和可视化。

---

### 5. 逻辑推理 (Logical Reasoning)

**目录**: `reasoning_quality/`

**评估维度**:
- 推理步骤数 (Step Count)
- 完整性 (Completeness)
- 结论正确性 (Conclusion Correctness)
- 人工评分 (Manual Scores)

**关键文件**:
- `reasoning_quality_scores.csv` - 自动评分
- `reasoning_quality_summary.csv` - 汇总统计
- `reasoning_quality_report.md` - 分析报告
- `manual_scores.csv` - 人工评分数据
- `manual_scores_report.md` - 人工评分报告
- `REASONING_EVALUATION_COMPLETE.md` - 完整评估文档
- `figures/` - 6张可视化图表

**评估方法**: 自动分析 + 人工评分

---

### 6. 文本摘要 (Text Summarization)

**目录**: `summary_quality/`

**评估维度**:
- ROUGE分数 (ROUGE-1/2/L)
- BERTScore (语义相似度)
- BARTScore (生成质量)
- 压缩比 (Compression Ratio)
- 信息密度 (Information Density)

**关键文件**:
- `summary_quality_scores.csv` - 详细评分
- `summary_quality_scores_with_bartscore.csv` - 包含BARTScore
- `summary_quality_summary.csv` - 汇总统计
- `summary_quality_report.md` - 分析报告
- `summary_bartscore_report.md` - BARTScore专项分析
- `summary_quality_insights.md` - 关键洞察
- `figures/` - 可视化图表（部分在根目录）

**评估方法**: ROUGE + BERTScore + BARTScore + 统计指标

---

### 7. 翻译 (Translation)

**目录**: `translation_quality/`

**评估维度**:
- BLEU分数 (BLEU-1/2/4)
- chrF++ (字符级F分数)
- BERTScore (语义相似度)
- COMET (可选，基于预训练模型)

**关键文件**:
- `translation_quality_scores.csv` - 详细评分
- `translation_quality_summary.csv` - 汇总统计
- `TRANSLATION_EVALUATION_REPORT.md` - 分析报告
- `figures/` - 5张可视化图表

**评估方法**: BLEU + chrF++ + BERTScore + COMET

**设计文档**: `data/analize/scripts/TRANSLATION_EVALUATION_DESIGN.md`

---

## 🔧 使用指南

### 查看单个任务结果

1. 进入对应任务目录，如 `cd data/analize/results/creative_quality/`
2. 查看汇总报告: `*_quality_report.md`
3. 查看详细数据: `*_quality_scores.csv`
4. 查看统计信息: `*_quality_summary.csv`
5. 查看可视化: `figures/` 目录

### 生成综合分析

运行聚合脚本:
```bash
python data/analize/scripts/aggregate_all_quality_results.py
```

输出:
- `aggregate/AGGREGATE_REPORT.md` - 综合分析报告
- `aggregate/aggregate_all_tasks.csv` - 所有任务数据
- `aggregate/model_ranking.csv` - 模型排名
- `aggregate/task_statistics.csv` - 任务统计
- `aggregate/figures/` - 综合可视化图表

### 检查目录结构

运行组织脚本:
```bash
python data/analize/scripts/organize_results.py
```

输出:
- `DIRECTORY_STRUCTURE.md` - 详细目录结构报告

---

## 📈 标准文件命名规范

每个任务目录应包含以下标准文件:

1. **评分数据**: `{task}_quality_scores.csv`
   - 包含每个模型、每个问题的详细评分

2. **汇总统计**: `{task}_quality_summary.csv`
   - 包含每个模型的平均分、标准差等统计信息

3. **分析报告**: `{task}_quality_report.md`
   - Markdown格式的分析报告，包含关键发现和洞察

4. **可视化图表**: `figures/` 子目录
   - PNG格式，300 DPI
   - 命名格式: `{task}_{chart_type}.png`

5. **补充文档** (可选):
   - 评估设计文档
   - 专项分析报告
   - 人工评分数据

---

## 📝 数据格式说明

### CSV文件编码
- 统一使用 **UTF-8** 编码
- 包含中文列名和内容

### 评分数据格式
```csv
model,question_id,metric1,metric2,...,overall_score
model_name,q01,0.85,0.90,...,0.875
```

### 汇总统计格式
```csv
model,avg_score,std_score,min_score,max_score,count
model_name,0.875,0.05,0.80,0.95,10
```

---

## 🔍 快速查找

### 按模型查找
所有任务的评分数据都包含 `model` 或 `model_name` 列，可以通过模型名称筛选。

### 按任务查找
每个任务有独立的目录，目录名格式为 `{task}_quality/`。

### 按指标查找
不同任务有不同的评估指标，详见各任务的 `*_quality_report.md`。

---

## 📚 相关文档

- **评估系统设计**: `data/analize/scripts/quality_evaluation_system.md`
- **分析设计文档**: `data/analize/scripts/analysis_design.md`
- **各任务评估设计**:
  - 代码: `data/analize/scripts/CODE_EVALUATION_DESIGN.md`
  - 创意: `data/analize/scripts/CREATIVE_EVALUATION_DESIGN.md`
  - 数学: `data/analize/scripts/MATH_EVALUATION_DESIGN.md`
  - 问答: `data/analize/scripts/QA_EVALUATION_DESIGN.md`
  - 推理: `data/analize/scripts/REASONING_EVALUATION_DESIGN.md`
  - 摘要: `data/analize/scripts/SUMMARY_EVALUATION_DESIGN.md`
  - 翻译: `data/analize/scripts/TRANSLATION_EVALUATION_DESIGN.md`

---

## 🛠️ 维护指南

### 添加新任务评估结果

1. 创建任务目录: `{task}_quality/`
2. 创建 `figures/` 子目录
3. 生成标准文件:
   - `{task}_quality_scores.csv`
   - `{task}_quality_summary.csv`
   - `{task}_quality_report.md`
4. 更新本索引文件
5. 运行聚合脚本更新综合分析

### 更新现有结果

1. 替换对应的CSV和报告文件
2. 重新生成可视化图表
3. 运行聚合脚本更新综合分析
4. 更新 `DIRECTORY_STRUCTURE.md`

---

## ⚠️ 注意事项

1. **不要修改目录结构**: 保持统一的命名规范和目录结构
2. **保持编码一致**: 所有文件使用UTF-8编码
3. **图表格式**: PNG格式，300 DPI，存放在 `figures/` 子目录
4. **备份数据**: 在修改前备份原始数据
5. **版本控制**: 重要更新应提交到Git

---

## 📞 联系方式

如有问题或建议，请参考项目根目录的 `AGENTS.md` 文件。

---

**文档版本**: 1.0  
**创建日期**: 2026-03-05  
**维护者**: GenAI Power Analysis Team
