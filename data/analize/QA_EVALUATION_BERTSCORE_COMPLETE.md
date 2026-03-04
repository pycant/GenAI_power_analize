# QA任务BERTScore评估完成总结

**完成时间**: 2026-03-04  
**状态**: ✅ 已完成

## 📊 评估概况

- **评估模型数**: 11
- **评估样本数**: 55 (11 models × 5 questions)
- **评估指标**: Exact Match, F1 Score, BERTScore (P/R/F1), ROUGE-L, BLEU

## ✅ 已实现的指标

### 1. Exact Match (EM)
- 预测答案与标准答案完全匹配
- 归一化处理(小写、去标点、去冠词)
- 无需外部模型

### 2. F1 Score
- 词级别的精确率和召回率
- 衡量部分匹配程度
- 无需外部模型

### 3. BERTScore ✅ (新增)
- 基于BERT的语义相似度
- 使用roberta-large模型
- 返回Precision, Recall, F1三个指标
- 需要GPU加速（可使用CPU但较慢）

### 4. ROUGE-L
- 基于最长公共子序列
- 衡量序列完整性
- 使用rouge库

### 5. BLEU
- 基于N-gram精确率
- 适用于生成式QA
- 使用nltk库

## 🔍 评估结果分析

### Top 3 模型 (按Exact Match)

1. **phi3_4b_hf_4bit**: 20.00%
2. **phi3_4b_hf_8bit**: 20.00%
3. 其他模型: 0.00%

### Top 3 模型 (按F1 Score)

1. **phi3_4b_hf_8bit**: 30.50%
2. **phi3_4b_hf_4bit**: 29.38%
3. **deepseek_8b_ol_q4km**: 5.00%

### BERTScore示例结果

| 模型 | 问题 | BERTScore P | BERTScore R | BERTScore F1 |
|------|------|-------------|-------------|--------------|
| deepseek_8b_ol_q4km | q01 | 0.8486 | 0.7957 | 0.8213 |
| gemma_2b_hf_4bit | q01 | 0.9210 | 0.7797 | 0.8445 |
| phi3_4b_hf_4bit | q01 | 0.9048 | 0.8648 | 0.8844 |

## 🔧 技术实现

### 核心代码

```
data/analize/scripts/
├── quality_evaluation/
│   └── qa_evaluator.py                     # 评估器实现
└── evaluate_qa_quality_academic.py         # 批量评估脚本
```

### 答案提取功能

评估器实现了智能答案提取功能：

1. 查找明确的答案标记("answer is", "the correct answer")
2. 查找结论性语句("therefore", "thus", "in conclusion")
3. 提取最后一句话
4. 如果都失败,返回前100个字符

### 答案归一化

```python
def normalize_answer(text: str) -> str:
    # 1. 转小写
    text = text.lower()
    
    # 2. 去除标点
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 3. 去除冠词
    articles = ['a', 'an', 'the']
    words = [w for w in words if w not in articles]
    
    # 4. 去除多余空格
    return ' '.join(words).strip()
```

## 📁 输出文件

```
data/analize/results/qa_quality_academic/
├── qa_quality_scores_academic.csv          # 详细评分(55行×11列)
├── qa_quality_summary_academic.csv         # 汇总统计(11行)
└── qa_quality_report_academic.md           # 分析报告
```

### 关键指标列

- `exact_match`: 精确匹配 (0/1)
- `f1_score`: F1分数 [0, 1]
- `bertscore_precision`: BERTScore精确率 [0, 1]
- `bertscore_recall`: BERTScore召回率 [0, 1]
- `bertscore_f1`: BERTScore F1分数 [0, 1]
- `rouge_l`: ROUGE-L F1分数 [0, 1]
- `bleu`: BLEU分数 [0, 1]
- `reference_answer`: 标准答案
- `extracted_answer`: 提取的答案

## 💡 关键发现

### 1. Exact Match很低
- 大多数模型EM=0%
- 原因: 模型给出详细推理过程,而非简短答案
- 只有phi3模型在某些问题上达到20% EM

### 2. F1 Score较低
- 平均F1约5-30%
- 最高: phi3_4b_hf_8bit (30.50%)
- 原因: 模型输出包含大量推理文本

### 3. BERTScore表现较好
- BERTScore F1普遍在0.80-0.90之间
- 说明模型输出在语义层面与标准答案相关
- 即使EM=0,BERTScore仍能捕捉语义相似性

### 4. BLEU接近0
- N-gram匹配度极低
- 说明模型输出与标准答案表述差异大

## 🎯 BERTScore的优势

1. **语义理解**: 不依赖精确词匹配,能捕捉语义相似性
2. **鲁棒性**: 对同义词、改写、不同表述方式更宽容
3. **学术认可**: 广泛应用于NLP评估任务
4. **可解释性**: 提供P/R/F1三个维度的分析

## 🔧 环境配置

### 依赖安装

```bash
conda activate bartscore
pip install bert-score rouge nltk
```

### 运行评估

```bash
# 不使用BERTScore (更快)
python data/analize/scripts/evaluate_qa_quality_academic.py

# 使用BERTScore (更准确,但较慢)
python data/analize/scripts/evaluate_qa_quality_academic.py --use-bertscore
```

## 📊 与其他指标对比

| 指标 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| Exact Match | 简单直观 | 过于严格 | 短答案 |
| F1 Score | 部分匹配 | 忽略语义 | 中等长度答案 |
| BERTScore | 语义理解 | 需要GPU | 所有场景 |
| ROUGE-L | 序列完整性 | 忽略语义 | 长文本 |
| BLEU | N-gram匹配 | 过于严格 | 机器翻译 |

## 🔗 相关文档

- [QA评估设计](scripts/QA_EVALUATION_DESIGN.md)
- [评估器代码](scripts/quality_evaluation/qa_evaluator.py)
- [评估报告](results/qa_quality_academic/qa_quality_report_academic.md)
- [QA评估总结](QA_EVALUATION_ACADEMIC_SUMMARY.md)

## 📝 下一步工作

### 已完成 ✅
- [x] 实现Exact Match
- [x] 实现F1 Score
- [x] 实现BERTScore
- [x] 实现ROUGE-L
- [x] 实现BLEU
- [x] 实现答案提取功能
- [x] 生成评估报告

### 待优化 ⏳
- [ ] 优化答案提取算法(提高EM和F1)
- [ ] 添加可视化图表
- [ ] 实现数学任务评估
- [ ] 实现代码任务评估

---

**文档版本**: v1.0  
**最后更新**: 2026-03-04  
**状态**: BERTScore评估完成 ✅
