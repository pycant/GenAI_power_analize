# 问答任务质量评估总结 (学术标准版)

**评估日期**: 2026-03-04  
**评估模型数**: 11  
**评估样本数**: 55 (11 models × 5 questions)  
**评估指标**: Exact Match, F1 Score, ROUGE-L, BLEU

## 📊 评估完成情况

### ✅ 已实现的指标

1. **Exact Match (EM)** ✅
   - 预测答案与标准答案完全匹配
   - 归一化处理(小写、去标点、去冠词)
   - 无需外部模型

2. **F1 Score** ✅
   - 词级别的精确率和召回率
   - 衡量部分匹配程度
   - 无需外部模型

3. **ROUGE-L** ✅
   - 基于最长公共子序列
   - 衡量序列完整性
   - 使用rouge库

4. **BLEU** ✅
   - 基于N-gram精确率
   - 适用于生成式QA
   - 使用nltk库

5. **BERTScore** ⏳ (可选,未启用)
   - 基于BERT的语义相似度
   - 需要GPU加速
   - 可通过--use-bertscore启用

## 🔍 评估结果分析

### 核心发现

1. **Exact Match = 0%**
   - 所有模型的EM都为0
   - 原因: 模型给出详细推理过程,而非简短答案
   - 示例: 标准答案"Quicksort",模型输出"I need to find an algorithm that has a worst-case running time of Θ(n²)..."

2. **F1 Score很低** (平均5.06%)
   - 最高: gemma_2b_hf_4bit (6.60%)
   - 最低: deepseek_8b_ol_q4km (3.40%)
   - 原因: 模型输出包含大量推理文本,与简短标准答案重叠度低

3. **BLEU接近0** (平均0.05%)
   - N-gram匹配度极低
   - 说明模型输出与标准答案表述差异大

4. **ROUGE-L显示nan**
   - rouge库在某些情况下返回nan
   - 需要进一步调试

### 问题难度分析

| 问题 | 平均F1 | 难度评估 |
|------|--------|----------|
| q03 (What is Nmap?) | 14.09% | 最简单 |
| q02 (Hash tables EXCEPT) | 7.29% | 中等 |
| q04 (Boolean NOT complete) | 3.32% | 困难 |
| q01 (Algorithm Θ(n²)) | 0.62% | 非常困难 |
| q05 (AH Protocol not) | 0.00% | 非常困难 |

## 💡 关键问题与改进方向

### 问题1: 答案提取缺失

**现状**: 直接用整个模型输出与标准答案比较

**问题**: 模型输出包含详细推理,不是简短答案

**解决方案**:
1. 实现答案提取器,从输出中提取最终答案
2. 使用正则表达式匹配"answer is", "the correct answer"等模式
3. 提取最后一句话或最后提到的关键词

### 问题2: 标准答案格式不一致

**现状**: 标准答案有长有短
- q01: "Quicksort" (1词)
- q02: "Range search: Given values..." (完整句子)
- q05: "Privacy" (1词)

**问题**: 长答案和短答案的评估标准不同

**解决方案**:
1. 为不同长度的答案使用不同的评估策略
2. 短答案(1-3词): 优先EM
3. 长答案(>10词): 优先F1和ROUGE-L

### 问题3: ROUGE-L返回nan

**现状**: rouge库在某些情况下返回nan

**解决方案**:
1. 添加异常处理
2. 检查输入文本是否为空
3. 考虑使用其他ROUGE实现

## 📁 输出文件

```
data/analize/results/qa_quality_academic/
├── qa_quality_scores_academic.csv          # 详细评分(55行×10列)
├── qa_quality_summary_academic.csv         # 汇总统计(11行)
└── qa_quality_report_academic.md           # 分析报告
```

### 关键指标列
- `exact_match`: 精确匹配 (0/1)
- `f1_score`: F1分数 [0, 1]
- `bertscore_f1`: BERTScore F1 (可选)
- `rouge_l`: ROUGE-L F1分数
- `bleu`: BLEU分数
- `reference_answer`: 标准答案

## 🔧 技术实现

### 核心代码
```
data/analize/scripts/
├── quality_evaluation/
│   └── qa_evaluator.py                     # 评估器实现(~150行)
└── evaluate_qa_quality_academic.py         # 批量评估脚本(~200行)
```

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

## 🎯 下一步行动

### 优先级1: 实现答案提取器 (高)

```python
def extract_answer(text: str) -> str:
    """从模型输出中提取最终答案"""
    # 策略1: 查找"answer is", "the correct answer"
    # 策略2: 提取最后一句话
    # 策略3: 使用NER识别关键实体
    pass
```

### 优先级2: 启用BERTScore (中)

```bash
# 安装依赖
pip install bert-score

# 运行评估
python evaluate_qa_quality_academic.py --use-bertscore
```

### 优先级3: 修复ROUGE-L (中)

- 调试rouge库返回nan的问题
- 考虑使用rouge-score库替代

### 优先级4: 可视化分析 (低)

- 生成EM vs F1散点图
- 生成模型-问题热力图
- 生成指标对比柱状图

## 📊 与之前版本对比

| 维度 | 规则版 (之前) | 学术版 (当前) |
|------|--------------|--------------|
| 核心指标 | 置信度、技术密度 | EM, F1, BERTScore |
| 是否需要标准答案 | 否 | 是 |
| 学术认可度 | 低 | 高 |
| 计算成本 | 低 | 中(BERTScore需GPU) |
| 适用场景 | 无标准答案 | 有标准答案 |
| 论文可用性 | 否 | 是 |

## 🔗 相关文档

- [评估方法设计](scripts/QA_EVALUATION_DESIGN.md)
- [评估器代码](scripts/quality_evaluation/qa_evaluator.py)
- [评估报告](results/qa_quality_academic/qa_quality_report_academic.md)

---

**文档版本**: v1.0  
**最后更新**: 2026-03-04  
**状态**: 评估完成,需要改进答案提取 ⚠️
