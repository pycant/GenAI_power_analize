# 质量评估体系说明

## 核心理念

**从主观加权 → 客观多维度 + 任务-模型适配性分析**

我们不再强制将多个指标合并为单一"质量分数"，而是：

1. ✅ **保留所有原始指标**：让数据说话，避免主观权重
2. ✅ **多维度呈现**：不同指标反映不同质量维度
3. ✅ **任务-模型适配性**：为不同应用场景推荐最适合的模型
4. ✅ **可选客观聚合**：如需综合分数，使用数据驱动的方法（熵权法、PCA、TOPSIS）

## 为什么不用主观权重？

**问题**：
```python
# ❌ 主观权重缺乏科学依据
Q_qa = 0.4 × Exact_Match + 0.3 × F1 + 0.3 × BERTScore
# 为什么是 0.4/0.3/0.3 而不是 0.5/0.25/0.25？
```

**解决方案**：
```python
# ✅ 保留所有指标，让用户根据需求选择
quality_metrics = {
    'exact_match': 0.85,
    'f1_score': 0.92,
    'bertscore_f1': 0.88
}

# 用户根据应用场景自行判断：
# - 如果需要精确匹配 → 看 exact_match
# - 如果允许部分匹配 → 看 f1_score
# - 如果关注语义理解 → 看 bertscore_f1
```

## 应用场景导向的模型选择

### 场景一：代码生成助手

**需求**：代码必须能运行，正确性最重要

**关键指标**：
- `pass_at_1`：测试用例通过率（最重要）
- `compilation_rate`：编译成功率（基础要求）

**推荐模型**：在 `pass_at_1` 上得分最高的模型

**示例输出**：
```
代码生成任务 Top 3 模型（按 pass_at_1 排序）：
1. deepseek_8b_ol_q4km: 0.85
2. qwen25_7b_hf_4bit: 0.82
3. phi3_4b_hf_4bit: 0.78
```

### 场景二：创意写作辅助

**需求**：生成内容要多样化，避免重复

**关键指标**：
- `distinct_2`：短语多样性（越高越好）
- `self_bleu`：生成多样性（越低越好）

**推荐模型**：`distinct_2` 高且 `self_bleu` 低的模型

**示例输出**：
```
创意写作任务 Top 3 模型（按多样性排序）：
1. gemma_4b_ol_q4km: distinct_2=0.92, self_bleu=0.15
2. qwen_8b_ol_q4km: distinct_2=0.89, self_bleu=0.18
3. qwen25_3b_hf_4bit: distinct_2=0.87, self_bleu=0.20
```

### 场景三：综合应用（多任务）

**需求**：模型需要在多个任务上都表现良好

**方法**：帕累托前沿分析

**推荐模型**：在多个任务的核心指标上都不差的模型

**示例输出**：
```
综合表现 Top 3 模型（帕累托前沿）：
1. qwen25_7b_hf_4bit: 代码(0.82), 问答(0.88), 摘要(0.85)
2. qwen_8b_ol_q4km: 代码(0.78), 问答(0.90), 摘要(0.87)
3. deepseek_8b_ol_q4km: 代码(0.85), 问答(0.85), 摘要(0.80)
```

## 客观综合评分方法（可选）

如果确实需要单一综合分数，我们提供三种**数据驱动**的方法：

### 方法一：熵权法（推荐）

**原理**：根据指标的信息熵自动确定权重

**优势**：
- ✅ 完全客观，无主观权重
- ✅ 信息量大的指标自动获得更高权重
- ✅ 适用于所有任务类型

**使用**：
```bash
python evaluate_all_models.py --aggregation entropy
```

### 方法二：主成分分析（PCA）

**原理**：自动发现指标间的主要变化方向

**优势**：
- ✅ 数据驱动
- ✅ 可解释性强（通过主成分载荷）
- ✅ 自动处理指标相关性

**使用**：
```bash
python evaluate_all_models.py --aggregation pca
```

### 方法三：TOPSIS

**原理**：基于理想解的距离排序

**优势**：
- ✅ 考虑理想解和负理想解
- ✅ 可处理不同方向的指标（越大越好/越小越好）
- ✅ 结果直观

**使用**：
```bash
python evaluate_all_models.py --aggregation topsis
```

### 默认：不聚合（推荐）

**使用**：
```bash
python evaluate_all_models.py  # 或 --aggregation none
```

**输出**：
- 所有原始指标
- 任务-模型适配性分析
- 每个指标的 Top 3 模型

## 输出文件

### 1. quality_scores_detailed.csv

包含所有原始指标，不做主观加权：

```csv
experiment_id,model,task_type,exact_match,f1_score,bertscore_f1,rouge_l,distinct_2,...
exp_001,qwen_8b,qa,0.85,0.92,0.88,0.75,0.82,...
exp_002,qwen_8b,code,,,,,0.78,0.95,...
```

### 2. task_model_matching.csv

任务-模型适配性分析，每个指标的 Top 3 模型：

```csv
task_type,metric,rank,model,score
qa,exact_match,1,qwen_8b_ol_q4km,0.85
qa,exact_match,2,deepseek_8b_ol_q4km,0.82
qa,exact_match,3,qwen25_7b_hf_4bit,0.80
qa,f1_score,1,qwen_8b_ol_q4km,0.92
...
```

## 使用流程

### 步骤1：运行质量评估

```bash
conda activate bartscore
set PYTHONUTF8=1
cd data/analize/scripts

# 默认：保留所有原始指标
python evaluate_all_models.py

# 或使用客观聚合方法
python evaluate_all_models.py --aggregation entropy
```

### 步骤2：查看任务-模型适配性

```python
import pandas as pd

# 加载适配性分析结果
matching = pd.read_csv('data/analize/pre_data/task_model_matching.csv')

# 查看代码生成任务的最优模型
code_best = matching[
    (matching['task_type'] == 'code') & 
    (matching['metric'] == 'pass_at_1') &
    (matching['rank'] == 1)
]
print(code_best)
```

### 步骤3：根据应用场景选择模型

```python
# 场景：需要代码生成 + 问答能力
code_models = matching[
    (matching['task_type'] == 'code') & 
    (matching['metric'] == 'pass_at_1') &
    (matching['rank'] <= 3)
]['model'].tolist()

qa_models = matching[
    (matching['task_type'] == 'qa') & 
    (matching['metric'] == 'exact_match') &
    (matching['rank'] <= 3)
]['model'].tolist()

# 找出两个任务都表现好的模型
best_models = set(code_models) & set(qa_models)
print(f"推荐模型: {best_models}")
```

## 优势总结

✅ **客观性**：避免主观权重，数据驱动

✅ **灵活性**：用户根据需求选择关注的指标

✅ **可解释性**：每个指标都有明确含义

✅ **实用性**：直接支持应用场景导向的模型选择

✅ **可扩展性**：易于添加新指标和新任务类型

## 参考文档

- 详细设计：`quality_evaluation_system.md`
- 分析设计：`analysis_design.md`
- 项目指南：`AGENTS.md`

---

**版本**: v2.0（任务-模型适配性导向）  
**更新日期**: 2026-03-04  
**作者**: Kiro AI Assistant
