# 2.4 问答任务 (QA) 评估方法设计

## 1. 评估目标

评估模型在问答任务中的**答案准确性、完整性、相关性与语义正确性**。

## 2. 数据特征分析

### 2.1 任务类型

基于提供的QA问题,任务类型为:
- **事实型问答**: 计算机科学、算法、网络安全等专业领域问题
- **简短答案**: 大多数答案为单词、短语或简短句子
- **抽取式/生成式混合**: 部分答案可直接从知识中抽取,部分需要生成解释

### 2.2 标准答案

| 问题ID | 问题 | 标准答案 |
|--------|------|----------|
| q01 | Which algorithm has Θ(n²) worst case but Θ(n log n) average? | Quicksort |
| q02 | Hash tables EXCEPT for which problem? | Range search: Given values a and b, find all records whose key value is in range a, b. |
| q03 | What is Nmap? | It is a scanner which works by injecting packets to a range of addresses, and inferring what hosts and services might be at those addresses, based on the responses |
| q04 | Which Boolean operator set is NOT complete? | {AND, OR} |
| q05 | AH Protocol provides authentication and integrity, but not | Privacy |

### 2.3 答案特征

- **简短答案**: q01, q04, q05 (1-2个词)
- **中等长度**: q02 (一句话)
- **详细解释**: q03 (完整描述)



## 3. 核心指标

### 3.1 Exact Match (EM)

**定义**: 预测答案与标准答案在归一化后**完全一致**。

**计算方法**:
1. 对预测答案与标准答案进行归一化处理:
   - 转换为小写
   - 去除前后空格
   - 去除标点符号
   - 去除冠词(a, an, the)
2. 进行字符串严格匹配

**数学表达**:
$$
EM = \begin{cases} 
1, & \text{normalize}(\text{预测答案}) = \text{normalize}(\text{标准答案}) \\
0, & \text{其他}
\end{cases}
$$

**范围**: $\{0, 1\}$

**特点**:
- ✅ 严格、直观
- ✅ 适用于抽取式QA、简短事实型答案
- ⚠️ 对表述差异敏感(如"Quicksort" vs "Quick sort")

**实现方案**:
```python
def normalize_answer(text: str) -> str:
    """答案归一化"""
    import re
    import string
    
    # 转小写
    text = text.lower()
    
    # 去除标点
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 去除冠词
    articles = ['a', 'an', 'the']
    words = text.split()
    words = [w for w in words if w not in articles]
    
    # 去除多余空格
    text = ' '.join(words).strip()
    
    return text

def calculate_exact_match(generated: str, reference: str) -> float:
    """计算Exact Match"""
    gen_norm = normalize_answer(generated)
    ref_norm = normalize_answer(reference)
    
    return 1.0 if gen_norm == ref_norm else 0.0
```



### 3.2 F1 Score (词级别)

**定义**: 衡量预测答案与标准答案在**词汇层面的重合程度**,综合精确率与召回率。

**计算方法**:

1. **Precision (精确率)**:
$$
Precision = \frac{|\text{预测词} \cap \text{标准词}|}{|\text{预测词}|}
$$

2. **Recall (召回率)**:
$$
Recall = \frac{|\text{预测词} \cap \text{标准词}|}{|\text{标准词}|}
$$

3. **F1 Score**:
$$
F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}
$$

**范围**: $[0, 1]$

**特点**:
- ✅ 对**部分正确、答案较长、多片段答案**更友好
- ✅ 比EM更宽松合理
- ✅ 适用于生成式QA
- ⚠️ 不考虑词序

**实现方案**:
```python
def calculate_f1_score(generated: str, reference: str) -> float:
    """计算F1 Score"""
    # 归一化并分词
    gen_tokens = normalize_answer(generated).split()
    ref_tokens = normalize_answer(reference).split()
    
    if len(gen_tokens) == 0 or len(ref_tokens) == 0:
        return 0.0
    
    # 计算交集
    common = set(gen_tokens) & set(ref_tokens)
    
    # 计算precision和recall
    precision = len(common) / len(gen_tokens)
    recall = len(common) / len(ref_tokens)
    
    # 计算F1
    if precision + recall == 0:
        return 0.0
    
    f1 = 2 * precision * recall / (precision + recall)
    
    return f1
```

**示例**:
- 标准答案: "Quicksort"
- 预测答案: "The answer is Quicksort algorithm"
- Precision: 1/5 = 0.2 (1个共同词/5个预测词)
- Recall: 1/1 = 1.0 (1个共同词/1个标准词)
- F1: 2 × 0.2 × 1.0 / (0.2 + 1.0) = 0.33



### 3.3 BERTScore

**定义**: 基于预训练语言模型(BERT)的**上下文语义相似度**,不依赖表面词重叠。

**计算方法**:
1. 使用预训练BERT模型获取token向量表示
2. 计算预测答案与标准答案token间的余弦相似度
3. 通过最大匹配得到语义级别的Precision/Recall/F1

**数学表达**:
$$
\text{BERTScore}_P = \frac{1}{|x|} \sum_{x_i \in x} \max_{y_j \in y} \cos(e_{x_i}, e_{y_j})
$$

$$
\text{BERTScore}_R = \frac{1}{|y|} \sum_{y_j \in y} \max_{x_i \in x} \cos(e_{x_i}, e_{y_j})
$$

$$
\text{BERTScore}_{F1} = 2 \times \frac{P \times R}{P + R}
$$

其中:
- $x$: 预测答案的token序列
- $y$: 标准答案的token序列
- $e_{x_i}$, $e_{y_j}$: BERT生成的token向量
- $\cos(\cdot, \cdot)$: 余弦相似度

**范围**: $[0, 1]$

**特点**:
- ✅ 能识别**同义不同表述**的答案
- ✅ 更贴近人类理解
- ✅ 适合**抽象、转述型、长答案**
- ⚠️ 需要GPU加速
- ⚠️ 首次运行需下载模型(~400MB)

**实现方案**:
```python
def calculate_bertscore(generated: str, reference: str, 
                       lang: str = 'en', device: str = 'cuda') -> Dict[str, float]:
    """
    计算BERTScore
    
    Args:
        generated: 生成的答案
        reference: 标准答案
        lang: 语言('en' for English, 'zh' for Chinese)
        device: 'cuda' or 'cpu'
    
    Returns:
        Dict with precision, recall, f1
    """
    try:
        from bert_score import score
        
        # 计算BERTScore
        P, R, F1 = score(
            [generated], 
            [reference], 
            lang=lang, 
            device=device,
            verbose=False
        )
        
        return {
            'bertscore_precision': P.item(),
            'bertscore_recall': R.item(),
            'bertscore_f1': F1.item()
        }
    except ImportError:
        print("⚠️  bert-score not installed. Run: pip install bert-score")
        return {
            'bertscore_precision': None,
            'bertscore_recall': None,
            'bertscore_f1': None
        }
```

**示例**:
- 标准答案: "Quicksort"
- 预测答案: "Quick sort algorithm"
- BERTScore F1: ~0.85 (能识别语义相似性)



## 4. 辅助指标

### 4.1 ROUGE-L

**定义**: 基于**最长公共子序列**(LCS)的重叠度量。

**计算方法**:
$$
R_{lcs} = \frac{LCS(X, Y)}{|Y|}
$$

$$
P_{lcs} = \frac{LCS(X, Y)}{|X|}
$$

$$
F_{lcs} = \frac{(1 + \beta^2) R_{lcs} P_{lcs}}{R_{lcs} + \beta^2 P_{lcs}}
$$

其中:
- $X$: 预测答案
- $Y$: 标准答案
- $LCS(X, Y)$: 最长公共子序列长度
- $\beta$: 通常设为1

**特点**:
- 关注答案的**整体顺序与完整性**
- 适用于**长文本答案、生成式QA**
- 考虑词序信息

**实现方案**:
```python
def calculate_rouge_l(generated: str, reference: str) -> float:
    """计算ROUGE-L F1分数"""
    try:
        from rouge import Rouge
        
        rouge = Rouge()
        scores = rouge.get_scores(generated, reference)[0]
        
        return scores['rouge-l']['f']
    except ImportError:
        print("⚠️  rouge not installed. Run: pip install rouge")
        return None
```

### 4.2 BLEU

**定义**: 基于N-gram精确率的重叠指标。

**计算方法**:
$$
BLEU = BP \times \exp\left(\sum_{n=1}^{N} w_n \log p_n\right)
$$

其中:
- $p_n$: n-gram精确率
- $w_n$: 权重(通常均匀分配)
- $BP$: 简短惩罚因子

**特点**:
- 常用于**多参考答案**的生成式问答
- 衡量生成文本与标准答案的相似度
- 对短答案可能不够敏感

**实现方案**:
```python
def calculate_bleu(generated: str, reference: str) -> float:
    """计算BLEU分数"""
    from nltk.translate.bleu_score import sentence_bleu
    
    gen_tokens = generated.split()
    ref_tokens = [reference.split()]  # BLEU需要列表格式
    
    return sentence_bleu(ref_tokens, gen_tokens)
```



## 5. 推荐评估方案

### 5.1 核心指标组合

| 维度 | 指标 | 优先级 | 计算成本 | 适用场景 |
|------|------|--------|----------|----------|
| 精确匹配 | Exact Match | ⭐⭐⭐ | 低 | 简短答案、事实型QA |
| 部分匹配 | F1 Score | ⭐⭐⭐ | 低 | 长答案、多片段答案 |
| 语义相似 | BERTScore | ⭐⭐⭐ | 高(需GPU) | 转述型答案、语义评估 |
| 序列匹配 | ROUGE-L | ⭐⭐ | 低 | 长文本答案 |
| N-gram匹配 | BLEU | ⭐ | 低 | 多参考答案 |

### 5.2 评估流程

```
1. 答案提取与归一化
   ├── 从模型输出中提取答案
   ├── 归一化处理(小写、去标点、去冠词)
   └── 准备标准答案

2. 基础指标计算
   ├── Exact Match (严格匹配)
   └── F1 Score (词级别重叠)

3. 语义指标计算(可选)
   ├── BERTScore (语义相似度)
   ├── ROUGE-L (序列匹配)
   └── BLEU (N-gram匹配)

4. 结果汇总
   ├── 按模型汇总平均分数
   ├── 按问题分析难度
   └── 生成评估报告
```

### 5.3 评分权重建议

#### 方案1: 简短答案优先(推荐用于本数据集)
```python
qa_quality_score = {
    'exact_match': 0.5,      # 50% - 精确匹配最重要
    'f1_score': 0.3,         # 30% - 部分匹配
    'bertscore_f1': 0.2      # 20% - 语义相似度
}
```

**理由**: 本数据集中q01, q04, q05为简短答案,EM最能反映准确性

#### 方案2: 语义理解优先
```python
qa_quality_score = {
    'bertscore_f1': 0.4,     # 40% - 语义最重要
    'f1_score': 0.3,         # 30% - 词汇重叠
    'exact_match': 0.3       # 30% - 精确匹配
}
```

**理由**: 强调语义理解,适合转述型答案

#### 方案3: 多维度呈现(推荐)
不计算单一综合分数,保留所有原始指标:
```python
qa_quality_metrics = {
    'exact_match': float,
    'f1_score': float,
    'bertscore_precision': float,
    'bertscore_recall': float,
    'bertscore_f1': float,
    'rouge_l': float,
    'bleu': float
}
```

**理由**: 保留完整信息,支持多角度分析



## 6. 实现方案

### 6.1 评估器设计

```python
# data/analize/scripts/quality_evaluation/qa_evaluator.py

import re
import string
from typing import Dict, Optional


class QAEvaluator:
    """问答任务评估器 - 基于学术标准指标"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.use_bertscore = self.config.get('use_bertscore', True)
        self.device = self.config.get('device', 'cuda')
        self.lang = self.config.get('lang', 'en')
    
    def evaluate(self, generated: str, reference: str, 
                 context: Dict = None) -> Dict[str, float]:
        """
        评估问答质量
        
        Args:
            generated: 生成的答案
            reference: 标准答案
            context: 额外上下文
        
        Returns:
            Dict[str, float]: 多维度指标
        """
        scores = {}
        
        # 基础检查
        if not generated or not reference:
            return self._get_zero_scores()
        
        # 1. Exact Match
        scores['exact_match'] = self._calculate_exact_match(generated, reference)
        
        # 2. F1 Score
        scores['f1_score'] = self._calculate_f1_score(generated, reference)
        
        # 3. BERTScore (可选)
        if self.use_bertscore:
            bertscore_results = self._calculate_bertscore(generated, reference)
            scores.update(bertscore_results)
        
        # 4. ROUGE-L
        scores['rouge_l'] = self._calculate_rouge_l(generated, reference)
        
        # 5. BLEU
        scores['bleu'] = self._calculate_bleu(generated, reference)
        
        return scores
    
    def _normalize_answer(self, text: str) -> str:
        """答案归一化"""
        # 转小写
        text = text.lower()
        
        # 去除标点
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # 去除冠词
        articles = ['a', 'an', 'the']
        words = text.split()
        words = [w for w in words if w not in articles]
        
        # 去除多余空格
        text = ' '.join(words).strip()
        
        return text
    
    def _calculate_exact_match(self, generated: str, reference: str) -> float:
        """计算Exact Match"""
        gen_norm = self._normalize_answer(generated)
        ref_norm = self._normalize_answer(reference)
        
        return 1.0 if gen_norm == ref_norm else 0.0
    
    def _calculate_f1_score(self, generated: str, reference: str) -> float:
        """计算F1 Score"""
        gen_tokens = self._normalize_answer(generated).split()
        ref_tokens = self._normalize_answer(reference).split()
        
        if len(gen_tokens) == 0 or len(ref_tokens) == 0:
            return 0.0
        
        common = set(gen_tokens) & set(ref_tokens)
        
        precision = len(common) / len(gen_tokens)
        recall = len(common) / len(ref_tokens)
        
        if precision + recall == 0:
            return 0.0
        
        f1 = 2 * precision * recall / (precision + recall)
        
        return f1
    
    def _calculate_bertscore(self, generated: str, reference: str) -> Dict[str, float]:
        """计算BERTScore"""
        try:
            from bert_score import score
            
            P, R, F1 = score(
                [generated], 
                [reference], 
                lang=self.lang, 
                device=self.device,
                verbose=False
            )
            
            return {
                'bertscore_precision': P.item(),
                'bertscore_recall': R.item(),
                'bertscore_f1': F1.item()
            }
        except ImportError:
            return {
                'bertscore_precision': None,
                'bertscore_recall': None,
                'bertscore_f1': None
            }
        except Exception as e:
            print(f"⚠️  BERTScore calculation failed: {e}")
            return {
                'bertscore_precision': None,
                'bertscore_recall': None,
                'bertscore_f1': None
            }
    
    def _calculate_rouge_l(self, generated: str, reference: str) -> float:
        """计算ROUGE-L"""
        try:
            from rouge import Rouge
            
            rouge = Rouge()
            scores = rouge.get_scores(generated, reference)[0]
            
            return scores['rouge-l']['f']
        except ImportError:
            return None
        except Exception:
            return 0.0
    
    def _calculate_bleu(self, generated: str, reference: str) -> float:
        """计算BLEU"""
        try:
            from nltk.translate.bleu_score import sentence_bleu
            
            gen_tokens = generated.split()
            ref_tokens = [reference.split()]
            
            return sentence_bleu(ref_tokens, gen_tokens)
        except ImportError:
            return None
        except Exception:
            return 0.0
    
    def _get_zero_scores(self) -> Dict[str, float]:
        """返回零分数"""
        return {
            'exact_match': 0.0,
            'f1_score': 0.0,
            'bertscore_precision': 0.0,
            'bertscore_recall': 0.0,
            'bertscore_f1': 0.0,
            'rouge_l': 0.0,
            'bleu': 0.0
        }
    
    def get_metric_categories(self) -> Dict[str, list]:
        """返回指标分类"""
        return {
            'exact': ['exact_match'],
            'overlap': ['f1_score', 'rouge_l', 'bleu'],
            'semantic': ['bertscore_precision', 'bertscore_recall', 'bertscore_f1']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向(True=越大越好)"""
        return {
            'exact_match': True,
            'f1_score': True,
            'bertscore_precision': True,
            'bertscore_recall': True,
            'bertscore_f1': True,
            'rouge_l': True,
            'bleu': True
        }
```



### 6.2 标准答案配置

```python
# 标准答案字典
QA_REFERENCE_ANSWERS = {
    'q01': 'Quicksort',
    'q02': 'Range search: Given values a and b, find all the records whose key value is in the range a, b.',
    'q03': 'It is a scanner which works by injecting packets to a range of addresses, and inferring what hosts and services might be at those addresses, based on the responses',
    'q04': '{AND, OR}',
    'q05': 'Privacy'
}
```

### 6.3 批量评估脚本

```python
# data/analize/scripts/evaluate_qa_quality_academic.py

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
from quality_evaluation.qa_evaluator import QAEvaluator

# 标准答案
REFERENCE_ANSWERS = {
    'q01': 'Quicksort',
    'q02': 'Range search: Given values a and b, find all the records whose key value is in the range a, b.',
    'q03': 'It is a scanner which works by injecting packets to a range of addresses, and inferring what hosts and services might be at those addresses, based on the responses',
    'q04': '{AND, OR}',
    'q05': 'Privacy'
}


def evaluate_qa_quality(data_dir: Path, output_dir: Path, use_bertscore: bool = False):
    """评估问答任务质量 - 学术标准指标"""
    
    print("\n" + "="*60)
    print("❓ Question Answering Quality Evaluation (Academic)")
    print("="*60)
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/qa/qa_responses.csv'
    df = pd.read_csv(responses_file)
    
    print(f"\n📂 Loaded {len(df)} models")
    print(f"📝 Questions: {len([c for c in df.columns if c != 'model'])}")
    
    # 初始化评估器
    config = {
        'use_bertscore': use_bertscore,
        'device': 'cuda',
        'lang': 'en'
    }
    evaluator = QAEvaluator(config)
    
    # 评估每个模型的每个响应
    results = []
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Evaluating models"):
        model = row['model']
        
        for col in df.columns:
            if col == 'model':
                continue
            
            response = row[col]
            
            if pd.isna(response) or len(str(response).strip()) == 0:
                continue
            
            # 获取标准答案
            reference = REFERENCE_ANSWERS.get(col)
            
            if reference is None:
                print(f"⚠️  No reference answer for {col}")
                continue
            
            # 评估质量
            scores = evaluator.evaluate(str(response), reference=reference)
            
            # 保存结果
            result = {
                'model': model,
                'question_id': col,
                'reference_answer': reference,
                **scores
            }
            results.append(result)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'qa_quality_scores_academic.csv'
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Evaluation completed!")
    print(f"📊 Results saved to: {output_file}")
    print(f"📈 Total evaluations: {len(results_df)}")
    
    # 生成汇总统计
    generate_summary_stats(results_df, output_dir)
    
    # 生成报告
    generate_report(results_df, output_dir)
    
    return results_df
```

## 7. 总结

### 7.1 指标体系总结

在问答任务中,**EM与F1是传统事实匹配的核心指标**,**BERTScore用于衡量深层语义一致性**,ROUGE-L与BLEU则用于长答案与生成式场景的补充评估。这套指标组合可全面衡量模型输出的**准确性、完整性、相关性与语义合理性**。

### 7.2 适用场景

| 场景 | 推荐指标 | 理由 |
|------|---------|------|
| 简短事实型QA | EM + F1 | 答案明确,精确匹配最重要 |
| 长答案QA | F1 + ROUGE-L | 考虑部分匹配和序列完整性 |
| 转述型QA | BERTScore + F1 | 语义理解比表面匹配更重要 |
| 多参考答案 | BLEU + F1 | 支持多种正确表述 |
| 综合评估 | EM + F1 + BERTScore | 全面覆盖精确、重叠、语义三个维度 |

### 7.3 实施建议

1. **优先实现EM和F1**: 计算成本低,无需外部依赖
2. **可选实现BERTScore**: 需要GPU,但能提供语义层面的评估
3. **保留多维度指标**: 不强制单一综合分数,支持多角度分析
4. **答案归一化**: 统一处理大小写、标点、冠词等,提高匹配准确性

---

**文档版本**: v2.0 (学术标准版)  
**创建日期**: 2026-03-04  
**作者**: Kiro AI Assistant  
**状态**: 设计完成,待实施
