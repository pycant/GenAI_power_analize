# 质量评估系统使用指南

**更新时间**: 2026-03-05  
**版本**: 2.0

---

## 📋 目录

1. [系统概述](#系统概述)
2. [目录结构](#目录结构)
3. [快速开始](#快速开始)
4. [评估任务详解](#评估任务详解)
5. [输出文件说明](#输出文件说明)
6. [常见问题](#常见问题)
7. [高级用法](#高级用法)

---

## 系统概述

质量评估系统用于评估大语言模型在7种不同任务类型上的输出质量，包括:

| 任务类型 | 评估指标 | 脚本文件 |
|---------|---------|---------|
| 代码生成 (code) | 编译率、代码长度、复杂度 | `evaluate_code_quality.py` |
| 创意写作 (creative) | Distinct-1/2、修辞手法、词汇丰富度 | `evaluate_creative_quality.py` |
| 数学推理 (math) | 精确匹配、数值匹配、推理完整性 | `evaluate_math_quality.py` |
| 问答 (qa) | 置信度、技术术语密度、推理步骤 | `evaluate_qa_quality.py` |
| 逻辑推理 (reasoning) | 结论正确性、推理完整性、连贯性 | `evaluate_reasoning_quality.py` |
| 文本摘要 (summary) | ROUGE-1/2/L、BERTScore、压缩比 | `evaluate_summary_quality.py` |
| 翻译 (translation) | BLEU-4、chrF、BERTScore | `evaluate_translation_quality.py` |

---

## 目录结构

```
data/analize/
├── pre_data/                          # 输入数据
│   ├── responses_raw.csv              # 原始响应数据
│   └── comparison_matrices/           # 按任务分类的响应矩阵
│       ├── code/
│       ├── creative/
│       ├── math/
│       ├── qa/
│       ├── reasoning/
│       ├── summary/
│       └── translation/
├── scripts/                           # 评估脚本
│   ├── run_all_evaluations.py        # 🌟 统一评估入口
│   ├── evaluate_*.py                  # 各任务评估脚本
│   ├── visualize_*.py                 # 可视化脚本
│   ├── aggregate_all_quality_results.py  # 聚合脚本
│   └── quality_evaluation/            # 评估器模块
│       ├── code_evaluator.py
│       ├── creative_evaluator.py
│       ├── math_evaluator.py
│       ├── qa_evaluator.py
│       ├── reasoning_evaluator.py
│       ├── summary_evaluator.py
│       └── translation_evaluator.py
└── results/                           # 输出结果
    ├── code_quality/
    ├── creative_quality/
    ├── math_quality/
    ├── qa_quality/
    ├── reasoning_quality/
    ├── summary_quality/
    ├── translation_quality/
    └── aggregate/                     # 综合分析结果
```

---

## 快速开始

### 方法1: 一键运行所有评估 (推荐)

```bash
# 激活环境
conda activate bartscore

# 运行所有评估
python data/analize/scripts/run_all_evaluations.py
```

### 方法2: 运行特定任务

```bash
# 只评估代码和数学任务
python data/analize/scripts/run_all_evaluations.py --tasks code math

# 详细输出模式
python data/analize/scripts/run_all_evaluations.py --verbose

# 列出所有可用任务
python data/analize/scripts/run_all_evaluations.py --list
```

### 方法3: 单独运行某个任务

```bash
# 代码生成评估
python data/analize/scripts/evaluate_code_quality.py

# 创意写作评估
python data/analize/scripts/evaluate_creative_quality.py

# 数学推理评估
python data/analize/scripts/evaluate_math_quality.py
```

---

## 评估任务详解

### 1. 代码生成 (Code Generation)

**评估指标**:
- `compilation_rate`: 编译成功率
- `code_length`: 代码行数
- `cyclomatic_complexity`: 圈复杂度
- `has_code`: 是否包含代码

**运行命令**:
```bash
python data/analize/scripts/evaluate_code_quality.py \
    --input data/analize/pre_data/responses_raw.csv \
    --output-dir data/analize/results/code_quality
```

**输出文件**:
- `quality_scores_code.csv`: 详细评分
- `quality_summary_code.csv`: 汇总统计

---

### 2. 创意写作 (Creative Writing)

**评估指标**:
- `distinct_1/2`: 词汇多样性
- `unique_token_ratio`: 独特词汇比例
- `total_rhetorical_devices`: 修辞手法总数
- `text_length`: 文本长度

**运行命令**:
```bash
python data/analize/scripts/evaluate_creative_quality.py
```

**输出文件**:
- `creative_quality_scores_detailed.csv`: 详细评分
- `creative_quality_summary.csv`: 汇总统计
- `creative_task_model_matching.csv`: 任务-模型匹配

---

### 3. 数学推理 (Math Reasoning)

**评估指标**:
- `exact_match`: 精确匹配
- `numerical_match`: 数值匹配(容忍1%误差)
- `has_reasoning`: 是否包含推理
- `step_count`: 推理步骤数

**运行命令**:
```bash
python data/analize/scripts/evaluate_math_quality.py \
    --tolerance 0.01
```

**输出文件**:
- `math_quality_scores.csv`: 详细评分
- `math_quality_summary.csv`: 汇总统计
- `math_quality_report.md`: 分析报告

---

### 4. 问答 (Question Answering)

**评估指标**:
- `confidence_score`: 答案置信度
- `technical_term_density`: 技术术语密度
- `has_reasoning`: 是否包含推理
- `reasoning_steps`: 推理步骤数

**运行命令**:
```bash
python data/analize/scripts/evaluate_qa_quality.py
```

**输出文件**:
- `qa_quality_scores.csv`: 详细评分
- `qa_quality_summary.csv`: 汇总统计
- `qa_quality_report.md`: 分析报告

---

### 5. 逻辑推理 (Logical Reasoning)

**评估指标**:
- `conclusion_correct`: 结论正确性
- `completeness_score`: 推理完整性
- `coherence_score`: 逻辑连贯性
- `step_count`: 推理步骤数

**运行命令**:
```bash
python data/analize/scripts/evaluate_reasoning_quality.py
```

**输出文件**:
- `reasoning_quality_scores.csv`: 详细评分
- `reasoning_quality_summary.csv`: 汇总统计
- `reasoning_quality_report.md`: 分析报告

---

### 6. 文本摘要 (Text Summarization)

**评估指标**:
- `rouge_1/2/l_f1`: ROUGE F1分数
- `bertscore_f1`: BERTScore F1分数
- `compression_ratio`: 压缩比
- `information_density`: 信息密度

**运行命令**:
```bash
python data/analize/scripts/evaluate_summary_quality.py \
    --use-bertscore
```

**输出文件**:
- `summary_quality_scores.csv`: 详细评分
- `summary_quality_summary.csv`: 汇总统计
- `summary_quality_report.md`: 分析报告

---

### 7. 翻译 (Translation)

**评估指标**:
- `bleu_4`: BLEU-4分数
- `chrf`: chrF分数
- `bertscore_f1`: BERTScore F1分数
- `length_ratio`: 长度比

**运行命令**:
```bash
python data/analize/scripts/evaluate_translation_quality.py
```

**输出文件**:
- `translation_quality_scores.csv`: 详细评分
- `translation_quality_summary.csv`: 汇总统计
- `TRANSLATION_EVALUATION_REPORT.md`: 分析报告

---

## 输出文件说明

### 标准输出文件

每个任务评估后会生成以下标准文件:

1. **详细评分文件** (`{task}_quality_scores.csv`)
   - 包含每个模型每个问题的详细评分
   - 列: model, question_id, 各项指标

2. **汇总统计文件** (`{task}_quality_summary.csv`)
   - 按模型汇总的统计数据
   - 列: model, 各指标的mean/std/min/max

3. **分析报告** (`{task}_quality_report.md`)
   - Markdown格式的分析报告
   - 包含排名、统计、关键发现

### 可视化图表

运行可视化脚本后会在 `results/{task}_quality/figures/` 生成图表:

```bash
# 创意写作可视化
python data/analize/scripts/visualize_creative_quality.py

# 问答可视化
python data/analize/scripts/visualize_qa_quality.py

# 逻辑推理可视化
python data/analize/scripts/visualize_reasoning_quality.py

# 摘要可视化
python data/analize/scripts/visualize_summary_quality.py

# 翻译可视化
python data/analize/scripts/visualize_translation_quality.py
```

### 综合分析

运行聚合脚本生成跨任务综合分析:

```bash
python data/analize/scripts/aggregate_all_quality_results.py
```

输出文件:
- `aggregate/aggregate_all_tasks.csv`: 所有任务原始数据
- `aggregate/aggregate_normalized.csv`: 归一化数据
- `aggregate/model_ranking.csv`: 模型综合排名
- `aggregate/task_statistics.csv`: 任务统计
- `aggregate/AGGREGATE_REPORT.md`: 综合分析报告
- `aggregate/aggregate_task_comparison.png`: 任务对比图
- `aggregate/aggregate_model_radar.png`: 模型雷达图

---

## 常见问题

### Q1: 如何修改输出路径?

所有评估脚本都支持 `--output-dir` 参数:

```bash
python evaluate_code_quality.py --output-dir /path/to/output
```

### Q2: 如何跳过某些任务?

使用 `run_all_evaluations.py` 的 `--tasks` 参数:

```bash
# 只运行代码、数学、问答
python run_all_evaluations.py --tasks code math qa
```

### Q3: 评估失败怎么办?

1. 检查输入数据是否存在
2. 查看错误信息
3. 使用 `--verbose` 查看详细输出
4. 使用 `--skip-errors` 跳过失败任务继续运行

### Q4: 如何添加新的评估指标?

1. 修改对应的评估器 (`quality_evaluation/{task}_evaluator.py`)
2. 在 `evaluate` 方法中添加新指标计算
3. 更新返回的字典

### Q5: BERTScore计算很慢怎么办?

BERTScore需要GPU加速，如果没有GPU可以:
- 摘要评估: 使用 `--no-bertscore`
- 翻译评估: 使用 `--no-bertscore`

---

## 高级用法

### 自定义评估配置

每个评估脚本都支持配置参数:

```bash
# 代码评估 - 启用代码执行测试
python evaluate_code_quality.py --enable-execution

# 数学评估 - 调整数值匹配容忍度
python evaluate_math_quality.py --tolerance 0.05

# 逻辑推理 - 启用LLM-as-Judge
python evaluate_reasoning_quality.py --use-llm-judge
```

### 批量处理多个实验

```bash
# 创建批处理脚本
for exp in exp1 exp2 exp3; do
    python run_all_evaluations.py \
        --data-dir data/$exp/pre_data \
        --output-dir data/$exp/results
done
```

### 并行运行评估

```bash
# 使用GNU parallel并行运行
parallel python evaluate_{}_quality.py ::: code creative math qa reasoning summary translation
```

---

## 脚本依赖关系

```
run_all_evaluations.py (统一入口)
    ├── evaluate_code_quality.py
    │   └── quality_evaluation/code_evaluator.py
    ├── evaluate_creative_quality.py
    │   └── quality_evaluation/creative_evaluator.py
    ├── evaluate_math_quality.py
    │   └── quality_evaluation/math_evaluator.py
    ├── evaluate_qa_quality.py
    │   └── quality_evaluation/qa_evaluator.py
    ├── evaluate_reasoning_quality.py
    │   └── quality_evaluation/reasoning_evaluator.py
    ├── evaluate_summary_quality.py
    │   └── quality_evaluation/summary_evaluator.py
    └── evaluate_translation_quality.py
        └── quality_evaluation/translation_evaluator.py

visualize_*.py (可视化脚本)
    └── 读取 results/{task}_quality/*.csv

aggregate_all_quality_results.py (聚合脚本)
    └── 读取 results/{task}_quality/*_summary.csv
```

---

## 更新日志

### v2.0 (2026-03-05)
- ✅ 创建统一评估入口 `run_all_evaluations.py`
- ✅ 标准化所有脚本的输出路径
- ✅ 统一命令行参数接口
- ✅ 添加详细的使用文档

### v1.0 (2026-03-04)
- ✅ 实现7种任务类型的评估脚本
- ✅ 创建评估器模块
- ✅ 实现可视化和聚合功能

---

## 联系与支持

如有问题或建议，请参考:
- 设计文档: `data/analize/scripts/quality_evaluation_system.md`
- 各任务设计: `data/analize/scripts/*_EVALUATION_DESIGN.md`
- 快速参考: `data/analize/*_QUICK_REFERENCE.md`

---

**Happy Evaluating! 🎉**
