# 质量评分表格

**生成时间**: 2026-03-07 14:23:30

---

## 表格说明

本目录包含各任务类型的质量评分表格，以模型为列、评分指标为行的矩阵格式展示。

所有评分均为原始指标值，未进行赋权处理。

### 表格列表

1. **code_scores.csv** - CODE任务质量评分
   - 数据源: `code_quality/quality_scores_code.csv`
   - 指标: 自动检测所有数值型指标
2. **creative_scores.csv** - CREATIVE任务质量评分
   - 数据源: `creative_quality/creative_quality_scores_with_perplexity.csv`
   - 指标: 自动检测所有数值型指标
3. **math_scores.csv** - MATH任务质量评分
   - 数据源: `math_quality/math_quality_scores.csv`
   - 指标: 自动检测所有数值型指标
4. **qa_scores.csv** - QA任务质量评分
   - 数据源: `qa_quality/qa_quality_scores.csv`
   - 指标: 自动检测所有数值型指标
5. **reasoning_scores.csv** - REASONING任务质量评分
   - 数据源: `reasoning_quality/reasoning_quality_scores.csv`
   - 指标: 自动检测所有数值型指标
6. **summary_scores.csv** - SUMMARY任务质量评分
   - 数据源: `summary_quality/summary_quality_scores_with_bartscore.csv`
   - 指标: 自动检测所有数值型指标
7. **translation_scores.csv** - TRANSLATION任务质量评分
   - 数据源: `translation_quality/translation_quality_scores.csv`
   - 指标: 自动检测所有数值型指标

8. **aggregated_scores_by_task.csv** - 跨任务聚合评分汇总
   - 每个任务的所有指标平均值

### 数据来源

- 数据源: `data/analize/results/*/quality_*_scores*.csv`
- 各任务类型的详细质量评估结果

### 文件版本

每个任务有两个版本的文件：
- **格式化版本** (如 `code_scores.csv`): 数值已格式化，便于阅读
- **原始版本** (如 `code_scores_raw.csv`): 保留完整精度，便于后续计算

### 使用方法

```python
import pandas as pd

# 读取某个任务的评分表格
df = pd.read_csv('code_scores.csv', index_col=0)

# 查看特定指标的所有模型得分
print(df.loc['compilation_rate'])  # 示例指标

# 查看特定模型的所有指标得分
print(df['qwen3:8b'])

# 读取跨任务聚合表格
agg_df = pd.read_csv('aggregated_scores_by_task.csv', index_col=0)
print(agg_df)
```

### 指标说明

详细的指标说明请参考：
- [METRICS_GUIDE.md](../../METRICS_GUIDE.md) - 完整指标说明文档
- [data/analize/results/README.md](../../../data/analize/results/README.md) - 质量评估结果说明

### 注意事项

- 表格中的NaN值表示该模型在该指标上没有数据
- 所有数值均为该模型在该任务下多个问题的平均值
- 指标自动从原始数据中检测，包含所有数值型列
- 不同任务的指标含义和取值范围可能不同，详见指标说明文档
- 评分未进行归一化或赋权，保留原始评估结果

---

**生成脚本**: `analysis/qe_research/scripts/create_quality_score_tables.py`
