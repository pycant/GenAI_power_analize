# 质量评分表格生成指南

## 概述

本指南说明如何生成以模型为列、评分指标为行的质量评分表格。这些表格直接使用原始评分指标，不进行赋权处理，便于后续分析和对比。

## 快速开始

### 运行脚本

**方式1：使用批处理文件（推荐）**
```bash
# 双击运行或在命令行执行
analysis\qe_research\scripts\run_quality_score_tables.bat
```

**方式2：直接运行Python脚本**
```bash
# 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 运行脚本
python analysis/qe_research/scripts/create_quality_score_tables.py
```

## 输出文件

### 输出目录
```
analysis/qe_research/results/quality_scores/
```

### 生成的文件

#### 1. 各任务类型的评分表格

每个任务类型生成两个版本：

- **格式化版本** (`{task}_scores.csv`)
  - 数值已格式化，便于阅读
  - 评分指标保留4位小数
  - 计数类指标保留整数
  
- **原始版本** (`{task}_scores_raw.csv`)
  - 保留完整精度
  - 便于后续计算和分析

**任务类型列表：**
1. `code_scores.csv` - 代码生成质量评分
2. `creative_scores.csv` - 创意写作质量评分
3. `math_scores.csv` - 数学推理质量评分
4. `qa_scores.csv` - 问答质量评分
5. `reasoning_scores.csv` - 逻辑推理质量评分
6. `summary_scores.csv` - 摘要生成质量评分
7. `translation_scores.csv` - 翻译质量评分

#### 2. 跨任务聚合表格

- `overall_scores_by_task.csv` - 各任务的综合评分汇总
  - 行：任务类型
  - 列：模型名称
  - 值：overall_score平均值

#### 3. 说明文档

- `README.md` - 详细的使用说明和数据来源

## 表格结构

### 示例：代码生成质量评分表格

```
评分指标 \ 模型,deepseek_8b,gemma3_4b,qwen3_8b,...
syntax_correctness,0.9500,0.8800,0.9200,...
functionality_completeness,0.8700,0.7900,0.8500,...
code_quality,0.8200,0.7500,0.8000,...
best_practices,0.7800,0.7200,0.7600,...
overall_score,0.8550,0.7850,0.8325,...
```

- **行**：各项评分指标
- **列**：不同模型
- **值**：该模型在该指标上的平均得分

## 数据来源

### 质量评分数据源

脚本从以下目录读取质量评分数据：

```
data/analize/results/
├── code_quality/quality_scores_code.csv
├── creative_quality/creative_quality_scores_with_perplexity.csv
├── math_quality/math_quality_scores.csv
├── qa_quality/qa_quality_scores.csv
├── reasoning_quality/reasoning_quality_scores.csv
├── summary_quality/summary_quality_scores_with_bartscore.csv
└── translation_quality/translation_quality_scores.csv
```

### 各任务包含的指标

#### Code (代码生成)
- syntax_correctness - 语法正确性
- functionality_completeness - 功能完整性
- code_quality - 代码质量
- best_practices - 最佳实践
- overall_score - 综合得分

#### Creative (创意写作)
- fluency - 流畅度
- coherence - 连贯性
- creativity - 创意性
- relevance - 相关性
- distinct_2 - 词汇多样性
- perplexity - 困惑度
- overall_score - 综合得分

#### Math (数学推理)
- answer_correctness - 答案正确性
- reasoning_process - 推理过程
- formula_usage - 公式使用
- step_clarity - 步骤清晰度
- overall_score - 综合得分

#### QA (问答)
- exact_match - 精确匹配
- f1_score - F1分数
- bleu_score - BLEU分数
- rouge_l - ROUGE-L分数
- bert_score - BERTScore
- answer_completeness - 答案完整性
- answer_relevance - 答案相关性
- overall_score - 综合得分

#### Reasoning (逻辑推理)
- conclusion_correct - 结论正确性
- completeness_score - 推理完整性
- coherence_score - 逻辑连贯性
- depth_score - 论证深度
- step_count - 推理步骤数
- overall_score - 综合得分

#### Summary (摘要生成)
- rouge_1 - ROUGE-1分数
- rouge_2 - ROUGE-2分数
- rouge_l - ROUGE-L分数
- bert_score - BERTScore
- bart_score - BARTScore
- compression_ratio - 压缩比
- information_density - 信息密度
- overall_score - 综合得分

#### Translation (翻译)
- bleu_score - BLEU分数
- semantic_fidelity - 语义保真度
- fluency - 流畅度
- terminology_accuracy - 术语准确性
- cultural_adaptation - 文化适应性
- overall_score - 综合得分

## 使用示例

### Python读取和分析

```python
import pandas as pd

# 1. 读取某个任务的评分表格
code_scores = pd.read_csv('analysis/qe_research/results/quality_scores/code_scores.csv', 
                          index_col=0)

# 2. 查看特定指标的所有模型得分
print("Overall Score across models:")
print(code_scores.loc['overall_score'])

# 3. 查看特定模型的所有指标得分
print("\nQwen3:8b scores:")
print(code_scores['qwen3:8b'])

# 4. 找出某指标得分最高的模型
best_model = code_scores.loc['overall_score'].idxmax()
best_score = code_scores.loc['overall_score'].max()
print(f"\nBest model: {best_model} (score: {best_score:.4f})")

# 5. 读取跨任务聚合表格
overall_scores = pd.read_csv('analysis/qe_research/results/quality_scores/overall_scores_by_task.csv',
                             index_col=0)
print("\nOverall scores by task:")
print(overall_scores)

# 6. 计算每个模型的平均质量得分（跨所有任务）
avg_quality = overall_scores.mean(axis=0)
print("\nAverage quality across all tasks:")
print(avg_quality.sort_values(ascending=False))
```

### 与效率指标结合分析

```python
import pandas as pd

# 读取质量得分
quality = pd.read_csv('analysis/qe_research/results/quality_scores/overall_scores_by_task.csv',
                      index_col=0)

# 读取能耗数据
energy = pd.read_csv('analysis/qe_research/results/metric_tables/01_avg_gpu_energy.csv',
                     index_col=0)

# 计算质效比（以code任务为例）
code_quality = quality.loc['code']
code_energy = energy.loc['code']

# 质效比 = 质量 / 能耗（越高越好）
qe_ratio = code_quality / code_energy

print("Quality-Efficiency Ratio (Code task):")
print(qe_ratio.sort_values(ascending=False))
```

## 注意事项

### 1. 数据完整性
- 如果某个模型在某个任务上没有数据，表格中会显示NaN
- 脚本会自动跳过缺失的质量评分文件

### 2. 指标含义
- 所有评分均为原始值，未进行归一化或赋权
- 不同任务的指标含义和取值范围可能不同
- 详细指标说明请参考 `analysis/METRICS_GUIDE.md`

### 3. 模型名称
- 模型名称会自动从质量评分数据中提取
- 确保质量评分数据中的model列命名一致

### 4. 计算方法
- 所有数值均为该模型在该任务下多个问题的平均值
- 使用pandas的mean()函数，自动忽略NaN值

## 与其他分析的集成

### 1. 与效率指标表格对比

效率指标表格位于：
```
analysis/qe_research/results/metric_tables/
├── 01_avg_gpu_energy.csv
├── 02_avg_output_tokens.csv
├── 03_ttft.csv
├── 04_avg_response_time.csv
├── 05_avg_gpu_memory.csv
└── 06_avg_gpu_utilization.csv
```

这些表格的结构是：任务为行、模型为列

### 2. 数据对齐

质量评分表格和效率指标表格可以通过以下方式对齐：

```python
# 质量表格：指标为行，模型为列
quality_df = pd.read_csv('quality_scores/code_scores.csv', index_col=0)

# 效率表格：任务为行，模型为列
energy_df = pd.read_csv('metric_tables/01_avg_gpu_energy.csv', index_col=0)

# 提取code任务的能耗数据（转置为列）
code_energy = energy_df.loc['code']

# 现在可以直接对比
print("Quality overall_score:", quality_df.loc['overall_score'])
print("Energy consumption:", code_energy)
```

## 故障排除

### 问题1：找不到质量评分文件

**错误信息：**
```
质量评分文件不存在: data/analize/results/xxx/xxx.csv
```

**解决方法：**
- 确认质量评估脚本已运行
- 检查文件路径是否正确
- 查看 `data/analize/results/` 目录结构

### 问题2：数据中缺少model列

**错误信息：**
```
数据中缺少 'model' 列
```

**解决方法：**
- 检查质量评分CSV文件格式
- 确保第一列为model列
- 重新运行质量评估脚本

### 问题3：中文显示乱码

**解决方法：**
```bash
# 设置UTF-8编码
set PYTHONUTF8=1

# 或在Python中
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

## 相关文档

- [METRICS_GUIDE.md](../../METRICS_GUIDE.md) - 完整指标说明
- [数据管道系统.md](../../数据管道系统.md) - 数据处理流程
- [create_metric_tables.py](scripts/create_metric_tables.py) - 效率指标表格生成脚本
- [质量评估结果说明](../../../data/analize/results/README.md)

## 更新日志

- **2026-03-07**: 创建初始版本
  - 支持7种任务类型的质量评分表格生成
  - 生成跨任务聚合表格
  - 保留原始评分，不进行赋权

---

**脚本位置**: `analysis/qe_research/scripts/create_quality_score_tables.py`  
**输出目录**: `analysis/qe_research/results/quality_scores/`  
**维护者**: Kiro AI Assistant
