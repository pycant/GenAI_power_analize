# 质量评估系统快速开始

**版本**: 2.0 | **更新**: 2026-03-05

---

## ⚡ 一分钟快速开始

```bash
# 1. 激活环境
conda activate bartscore

# 2. 运行所有评估
python data/analize/scripts/run_all_evaluations.py

# 3. 查看结果
ls data/analize/results/
```

就这么简单! 🎉

---

## 📋 常用命令

### 运行评估

```bash
# 运行所有评估
python data/analize/scripts/run_all_evaluations.py

# 运行特定任务
python data/analize/scripts/run_all_evaluations.py --tasks code math qa

# 详细输出
python data/analize/scripts/run_all_evaluations.py --verbose

# 列出所有任务
python data/analize/scripts/run_all_evaluations.py --list
```

### 单独运行某个任务

```bash
# 代码生成
python data/analize/scripts/evaluate_code_quality.py

# 创意写作
python data/analize/scripts/evaluate_creative_quality.py

# 数学推理
python data/analize/scripts/evaluate_math_quality.py

# 问答
python data/analize/scripts/evaluate_qa_quality.py

# 逻辑推理
python data/analize/scripts/evaluate_reasoning_quality.py

# 文本摘要
python data/analize/scripts/evaluate_summary_quality.py

# 翻译
python data/analize/scripts/evaluate_translation_quality.py
```

### 生成可视化

```bash
# 创意写作
python data/analize/scripts/visualize_creative_quality.py

# 问答
python data/analize/scripts/visualize_qa_quality.py

# 逻辑推理
python data/analize/scripts/visualize_reasoning_quality.py

# 摘要
python data/analize/scripts/visualize_summary_quality.py

# 翻译
python data/analize/scripts/visualize_translation_quality.py
```

### 综合分析

```bash
# 聚合所有任务结果
python data/analize/scripts/aggregate_all_quality_results.py
```

---

## 📁 重要路径

| 路径 | 说明 |
|------|------|
| `data/analize/pre_data/` | 输入数据 |
| `data/analize/scripts/` | 评估脚本 |
| `data/analize/results/` | 输出结果 |
| `data/analize/results/aggregate/` | 综合分析 |

---

## 📊 输出文件

每个任务评估后会生成:

| 文件 | 说明 |
|------|------|
| `{task}_quality_scores.csv` | 详细评分 |
| `{task}_quality_summary.csv` | 汇总统计 |
| `{task}_quality_report.md` | 分析报告 |
| `figures/*.png` | 可视化图表 |

---

## 🎯 7种评估任务

| 任务 | 代码 | 主要指标 |
|------|------|---------|
| 代码生成 | `code` | 编译率、代码长度、复杂度 |
| 创意写作 | `creative` | Distinct-1/2、修辞手法 |
| 数学推理 | `math` | 精确匹配、推理完整性 |
| 问答 | `qa` | 置信度、技术术语密度 |
| 逻辑推理 | `reasoning` | 结论正确性、推理完整性 |
| 文本摘要 | `summary` | ROUGE、BERTScore |
| 翻译 | `translation` | BLEU、chrF、BERTScore |

---

## 🔧 常见问题

### Q: 如何只运行部分任务?

```bash
python run_all_evaluations.py --tasks code math qa
```

### Q: 评估失败怎么办?

```bash
# 跳过错误继续运行
python run_all_evaluations.py --skip-errors

# 查看详细错误
python run_all_evaluations.py --verbose
```

### Q: 如何修改输出路径?

```bash
python evaluate_code_quality.py --output-dir /path/to/output
```

### Q: BERTScore太慢怎么办?

```bash
# 摘要评估 - 禁用BERTScore
python evaluate_summary_quality.py --no-bertscore

# 翻译评估 - 禁用BERTScore
python evaluate_translation_quality.py --no-bertscore
```

---

## 📚 详细文档

| 文档 | 说明 |
|------|------|
| [EVALUATION_SYSTEM_GUIDE.md](scripts/EVALUATION_SYSTEM_GUIDE.md) | 完整使用指南 |
| [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) | 文档索引 |
| [REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md) | 系统重组总结 |

---

## 🚀 完整工作流

```bash
# 1. 准备数据
ls data/analize/pre_data/responses_raw.csv

# 2. 运行评估
python data/analize/scripts/run_all_evaluations.py

# 3. 生成可视化
python data/analize/scripts/visualize_creative_quality.py
python data/analize/scripts/visualize_qa_quality.py
python data/analize/scripts/visualize_reasoning_quality.py
python data/analize/scripts/visualize_summary_quality.py
python data/analize/scripts/visualize_translation_quality.py

# 4. 综合分析
python data/analize/scripts/aggregate_all_quality_results.py

# 5. 查看结果
cat data/analize/results/aggregate/AGGREGATE_REPORT.md
```

---

## 💡 提示

- 使用 `--list` 查看所有可用任务
- 使用 `--verbose` 查看详细输出
- 使用 `--skip-errors` 跳过失败任务
- 使用 `--tasks` 选择特定任务

---

## 📞 需要帮助?

查看完整文档: [EVALUATION_SYSTEM_GUIDE.md](scripts/EVALUATION_SYSTEM_GUIDE.md)

---

**快速开始指南** | v2.0 | 2026-03-05
