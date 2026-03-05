# 质量评估系统

**版本**: 2.0  
**更新时间**: 2026-03-05  
**状态**: ✅ 生产就绪

---

## 🎯 系统简介

质量评估系统用于评估大语言模型在7种不同任务类型上的输出质量，提供全面、客观、可量化的评估指标。

### 支持的任务类型

| 任务 | 评估指标 | 状态 |
|------|---------|------|
| 代码生成 | 编译率、代码长度、圈复杂度 | ✅ |
| 创意写作 | Distinct-1/2、修辞手法、词汇丰富度 | ✅ |
| 数学推理 | 精确匹配、数值匹配、推理完整性 | ✅ |
| 问答 | 置信度、技术术语密度、推理步骤 | ✅ |
| 逻辑推理 | 结论正确性、推理完整性、连贯性 | ✅ |
| 文本摘要 | ROUGE-1/2/L、BERTScore、压缩比 | ✅ |
| 翻译 | BLEU-4、chrF、BERTScore | ✅ |

---

## ⚡ 快速开始

```bash
# 1. 激活环境
conda activate bartscore

# 2. 运行所有评估
python data/analize/scripts/run_all_evaluations.py

# 3. 查看结果
ls data/analize/results/
```

详细说明请查看: [QUICK_START.md](QUICK_START.md)

---

## 📁 目录结构

```
data/analize/
├── README.md                          # 本文件
├── QUICK_START.md                     # 快速开始指南
├── DOCUMENTATION_INDEX.md             # 文档索引
├── REORGANIZATION_SUMMARY.md          # 系统重组总结
│
├── pre_data/                          # 输入数据
│   ├── responses_raw.csv              # 原始响应数据
│   ├── responses_summary.csv          # 响应汇总
│   └── comparison_matrices/           # 按任务分类的响应矩阵
│       ├── code/
│       ├── creative/
│       ├── math/
│       ├── qa/
│       ├── reasoning/
│       ├── summary/
│       └── translation/
│
├── scripts/                           # 评估脚本
│   ├── run_all_evaluations.py        # 🌟 统一评估入口
│   ├── EVALUATION_SYSTEM_GUIDE.md    # 完整使用指南
│   ├── fix_output_paths.py           # 路径修复工具
│   │
│   ├── evaluate_*.py                  # 各任务评估脚本
│   ├── visualize_*.py                 # 可视化脚本
│   ├── aggregate_all_quality_results.py  # 聚合脚本
│   │
│   ├── quality_evaluation/            # 评估器模块
│   │   ├── code_evaluator.py
│   │   ├── creative_evaluator.py
│   │   ├── math_evaluator.py
│   │   ├── qa_evaluator.py
│   │   ├── reasoning_evaluator.py
│   │   ├── summary_evaluator.py
│   │   └── translation_evaluator.py
│   │
│   └── *_EVALUATION_DESIGN.md         # 各任务设计文档
│
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

## 📚 文档导航

### 核心文档

| 文档 | 说明 | 链接 |
|------|------|------|
| 快速开始 | 一分钟上手指南 | [QUICK_START.md](QUICK_START.md) |
| 使用指南 | 完整的使用说明 | [EVALUATION_SYSTEM_GUIDE.md](scripts/EVALUATION_SYSTEM_GUIDE.md) |
| 文档索引 | 所有文档的索引 | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |
| 重组总结 | 系统重组说明 | [REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md) |

### 任务文档

每个任务都有对应的设计文档和快速参考:

| 任务 | 设计文档 | 快速参考 |
|------|---------|---------|
| 代码生成 | - | - |
| 创意写作 | [CREATIVE_EVALUATION_DESIGN.md](scripts/CREATIVE_EVALUATION_DESIGN.md) | [CREATIVE_QUICK_REFERENCE.md](CREATIVE_QUICK_REFERENCE.md) |
| 数学推理 | [MATH_EVALUATION_DESIGN.md](scripts/MATH_EVALUATION_DESIGN.md) | [MATH_QUICK_REFERENCE.md](MATH_QUICK_REFERENCE.md) |
| 问答 | [QA_EVALUATION_DESIGN.md](scripts/QA_EVALUATION_DESIGN.md) | [QA_QUICK_REFERENCE.md](QA_QUICK_REFERENCE.md) |
| 逻辑推理 | [REASONING_EVALUATION_DESIGN.md](scripts/REASONING_EVALUATION_DESIGN.md) | [REASONING_EVALUATION_QUICK_REFERENCE.md](REASONING_EVALUATION_QUICK_REFERENCE.md) |
| 文本摘要 | [SUMMARY_EVALUATION_DESIGN.md](scripts/SUMMARY_EVALUATION_DESIGN.md) | [SUMMARY_QUICK_REFERENCE.md](SUMMARY_QUICK_REFERENCE.md) |
| 翻译 | [TRANSLATION_EVALUATION_DESIGN.md](scripts/TRANSLATION_EVALUATION_DESIGN.md) | [TRANSLATION_QUICK_REFERENCE.md](TRANSLATION_QUICK_REFERENCE.md) |

---

## 🚀 使用方法

### 方法1: 一键运行所有评估 (推荐)

```bash
python data/analize/scripts/run_all_evaluations.py
```

### 方法2: 运行特定任务

```bash
python data/analize/scripts/run_all_evaluations.py --tasks code math qa
```

### 方法3: 单独运行某个任务

```bash
python data/analize/scripts/evaluate_code_quality.py
python data/analize/scripts/evaluate_creative_quality.py
python data/analize/scripts/evaluate_math_quality.py
# ... 其他任务
```

### 方法4: 生成可视化和综合报告

```bash
# 可视化
python data/analize/scripts/visualize_creative_quality.py
python data/analize/scripts/visualize_qa_quality.py
# ... 其他可视化

# 综合分析
python data/analize/scripts/aggregate_all_quality_results.py
```

---

## 📊 输出说明

### 标准输出文件

每个任务评估后会在 `results/{task}_quality/` 生成:

| 文件 | 说明 |
|------|------|
| `{task}_quality_scores.csv` | 每个模型每个问题的详细评分 |
| `{task}_quality_summary.csv` | 按模型汇总的统计数据 |
| `{task}_quality_report.md` | Markdown格式的分析报告 |
| `figures/*.png` | 可视化图表 |

### 综合分析输出

运行聚合脚本后会在 `results/aggregate/` 生成:

| 文件 | 说明 |
|------|------|
| `aggregate_all_tasks.csv` | 所有任务的原始数据 |
| `aggregate_normalized.csv` | 归一化后的数据 |
| `model_ranking.csv` | 模型综合排名 |
| `task_statistics.csv` | 任务统计信息 |
| `AGGREGATE_REPORT.md` | 综合分析报告 |
| `aggregate_task_comparison.png` | 任务对比图 |
| `aggregate_model_radar.png` | 模型雷达图 |

---

## 🔧 系统特性

### ✅ 已实现

- 7种任务类型的质量评估
- 统一的评估入口和接口
- 标准化的输出路径
- 详细的评估报告
- 可视化图表生成
- 综合分析和排名
- 完整的文档体系

### 🚧 计划中

- 评估结果的自动化测试
- 评估结果的版本管理
- Web可视化界面
- 实时评估监控
- 分布式评估支持

---

## 🛠️ 依赖环境

### Python环境

```bash
conda create -n bartscore python=3.10
conda activate bartscore
```

### 必需依赖

```bash
pip install pandas numpy matplotlib seaborn
pip install rouge-score bert-score sacrebleu
pip install transformers torch
```

### 可选依赖

```bash
# 困惑度计算
pip install transformers torch

# 代码执行测试
pip install ast radon
```

---

## 📈 评估指标说明

### 代码生成
- `compilation_rate`: 编译成功率
- `code_length`: 代码行数
- `cyclomatic_complexity`: 圈复杂度

### 创意写作
- `distinct_1/2`: 词汇多样性
- `unique_token_ratio`: 独特词汇比例
- `total_rhetorical_devices`: 修辞手法总数

### 数学推理
- `exact_match`: 精确匹配
- `numerical_match`: 数值匹配
- `has_reasoning`: 是否包含推理

### 问答
- `confidence_score`: 答案置信度
- `technical_term_density`: 技术术语密度
- `reasoning_steps`: 推理步骤数

### 逻辑推理
- `conclusion_correct`: 结论正确性
- `completeness_score`: 推理完整性
- `coherence_score`: 逻辑连贯性

### 文本摘要
- `rouge_1/2/l_f1`: ROUGE F1分数
- `bertscore_f1`: BERTScore F1分数
- `compression_ratio`: 压缩比

### 翻译
- `bleu_4`: BLEU-4分数
- `chrf`: chrF分数
- `bertscore_f1`: BERTScore F1分数

---

## 🤝 贡献指南

### 添加新的评估任务

1. 在 `quality_evaluation/` 创建新的评估器
2. 在 `scripts/` 创建评估脚本
3. 更新 `run_all_evaluations.py` 的任务配置
4. 编写设计文档和快速参考
5. 更新文档索引

### 添加新的评估指标

1. 修改对应的评估器
2. 更新评估脚本
3. 更新文档说明

---

## 📞 支持与反馈

### 文档

- 使用指南: [EVALUATION_SYSTEM_GUIDE.md](scripts/EVALUATION_SYSTEM_GUIDE.md)
- 文档索引: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- 快速开始: [QUICK_START.md](QUICK_START.md)

### 常见问题

查看 [EVALUATION_SYSTEM_GUIDE.md - 常见问题](scripts/EVALUATION_SYSTEM_GUIDE.md#常见问题)

---

## 📝 更新日志

### v2.0 (2026-03-05)

**新增**:
- ✅ 统一评估入口 `run_all_evaluations.py`
- ✅ 完整使用指南和文档体系
- ✅ 路径修复工具
- ✅ 快速开始指南

**改进**:
- ✅ 标准化所有脚本的输出路径
- ✅ 统一命令行参数接口
- ✅ 改进错误处理和进度跟踪
- ✅ 整理和组织所有文档

**修复**:
- ✅ 修复输出路径不一致问题
- ✅ 修复文档交叉引用错误

### v1.0 (2026-03-04)

- ✅ 实现7种任务类型的评估脚本
- ✅ 创建评估器模块
- ✅ 实现可视化和聚合功能

---

## 📄 许可证

本项目用于学术研究和评估目的。

---

## 🎉 致谢

感谢所有贡献者和使用者的支持!

---

**质量评估系统** | v2.0 | 2026-03-05 | ✅ 生产就绪
