# 创意写作任务质量评估方法设计

## 1. 评估目标

创意写作任务的核心评估维度：
- **多样性 (Diversity)**: 词汇丰富度、表达多样性
- **流畅性 (Fluency)**: 语言流畅度、语法正确性
- **创造力 (Creativity)**: 新颖性、主题多样性

## 2. 提议方法的可行性分析

### 2.1 多样性指标

#### Distinct-1/2/3 ✅ 高度可行

**定义**：
- Distinct-N = unique_N-grams / total_N-grams
- 衡量词汇和短语的去重率

**优势**：
- ✅ 计算简单，无需外部模型
- ✅ 直接反映词汇多样性
- ✅ 已在多个研究中验证有效性
- ✅ 适合中文分词后计算

**实现方案**：
```python
def calculate_distinct_n(text, n=2):
    """计算Distinct-N指标"""
    import jieba
    tokens = list(jieba.cut(text))
    
    if len(tokens) < n:
        return 0.0
    
    ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
    
    if len(ngrams) == 0:
        return 0.0
    
    return len(set(ngrams)) / len(ngrams)
```

**推荐配置**：
- Distinct-1: 词级别多样性（基础）
- Distinct-2: 短语级别多样性（核心指标）
- Distinct-3: 长短语多样性（补充）


#### Self-BLEU ⚠️ 部分可行（需多次生成）

**定义**：
- 计算同一提示多次生成结果间的BLEU分数
- 分数越低表示生成越多样

**限制条件**：
- ❌ 当前数据集每个提示只有1次生成
- ❌ 无法计算Self-BLEU（需要至少2次生成）

**替代方案**：
1. **跨模型多样性**：计算不同模型对同一提示的响应差异
2. **跨提示一致性**：计算同一模型对不同提示的响应相似度（检测模板化）

**实现方案（替代）**：
```python
def calculate_cross_model_diversity(responses_dict):
    """计算跨模型的响应多样性"""
    from nltk.translate.bleu_score import sentence_bleu
    import jieba
    
    models = list(responses_dict.keys())
    bleu_scores = []
    
    for i, model_i in enumerate(models):
        for j, model_j in enumerate(models):
            if i < j:
                ref = [list(jieba.cut(responses_dict[model_i]))]
                hyp = list(jieba.cut(responses_dict[model_j]))
                score = sentence_bleu(ref, hyp)
                bleu_scores.append(score)
    
    # 平均BLEU越低，跨模型多样性越高
    return 1 - (sum(bleu_scores) / len(bleu_scores)) if bleu_scores else 0.0
```

**建议**：
- ⚠️ 暂不使用Self-BLEU（数据限制）
- ✅ 可选：使用跨模型多样性作为补充指标


#### 句向量语义多样性 ✅ 可行但成本较高

**定义**：
- 使用句向量模型（如Sentence-BERT）计算句子间的语义距离
- 距离越大表示语义多样性越高

**优势**：
- ✅ 捕捉深层语义多样性
- ✅ 不受表面词汇影响

**劣势**：
- ⚠️ 需要加载预训练模型（~400MB）
- ⚠️ 计算成本较高（需GPU加速）
- ⚠️ 对于单个响应内部的多样性评估效果有限

**实现方案**：
```python
def calculate_semantic_diversity(text):
    """计算文本内部句子的语义多样性"""
    from sentence_transformers import SentenceTransformer
    import numpy as np
    
    # 加载模型（首次会下载）
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    # 分句
    sentences = text.split('。')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
    
    if len(sentences) < 2:
        return 0.0
    
    # 计算句向量
    embeddings = model.encode(sentences)
    
    # 计算句子间平均余弦距离
    from sklearn.metrics.pairwise import cosine_similarity
    sim_matrix = cosine_similarity(embeddings)
    
    # 提取上三角（不含对角线）
    n = len(sentences)
    similarities = []
    for i in range(n):
        for j in range(i+1, n):
            similarities.append(sim_matrix[i][j])
    
    # 多样性 = 1 - 平均相似度
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0
    return 1 - avg_similarity
```

**建议**：
- ⚠️ 作为可选高级指标
- ✅ 优先使用Distinct-N（成本低、效果好）
- 💡 如果计算资源充足，可以补充使用


### 2.2 流畅性指标

#### 困惑度 (Perplexity, PPL) ✅ 可行

**定义**：
- 使用语言模型计算文本的困惑度
- PPL越低表示文本越流畅、越符合语言规律

**优势**：
- ✅ 客观量化流畅度
- ✅ 广泛应用于文本生成评估
- ✅ 可使用开源中文语言模型

**实现方案**：
```python
def calculate_perplexity(text, model_name='uer/gpt2-chinese-cluecorpussmall'):
    """计算文本困惑度"""
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    
    # 加载模型
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # 编码
    encodings = tokenizer(text, return_tensors='pt')
    
    # 计算困惑度
    with torch.no_grad():
        outputs = model(**encodings, labels=encodings['input_ids'])
        loss = outputs.loss
        perplexity = torch.exp(loss).item()
    
    return perplexity
```

**推荐模型**：
- `uer/gpt2-chinese-cluecorpussmall` (小型，~300MB)
- `uer/gpt2-chinese-cluecorpusmedium` (中型，~600MB)

**注意事项**：
- ⚠️ 首次运行需下载模型
- ⚠️ 建议使用GPU加速（CPU较慢）
- ⚠️ 对于超长文本需要截断处理

**建议**：
- ✅ 作为核心流畅性指标
- 💡 可以缓存模型避免重复加载


#### 语法错误率 ⚠️ 可行但需谨慎

**定义**：
- 检测文本中的语法错误数量
- 错误率 = 错误数 / 总句子数

**实现方案**：
```python
def calculate_grammar_error_rate(text):
    """计算语法错误率（基于规则）"""
    import re
    
    errors = 0
    sentences = text.split('。')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
    
    if len(sentences) == 0:
        return 0.0
    
    for sent in sentences:
        # 检测常见语法错误
        # 1. 标点符号错误
        if re.search(r'[，。！？；：][\u4e00-\u9fa5]', sent):
            errors += 0.5  # 标点后缺少空格（轻微）
        
        # 2. 重复标点
        if re.search(r'[，。！？]{2,}', sent):
            errors += 1
        
        # 3. 括号不匹配
        if sent.count('(') != sent.count(')'):
            errors += 1
        if sent.count('（') != sent.count('）'):
            errors += 1
    
    return errors / len(sentences)
```

**限制**：
- ❌ 基于规则的方法覆盖有限
- ❌ 中文语法检测工具不成熟
- ⚠️ 创意写作可能故意使用非标准语法

**替代方案**：
- 使用困惑度（PPL）间接反映语法流畅性
- 人工抽样检查

**建议**：
- ⚠️ 不推荐作为核心指标
- ✅ 困惑度已经能较好反映语法质量


### 2.3 创造力指标

#### Novelty (新颖性) ⚠️ 概念模糊，需明确定义

**问题**：
- ❓ "新颖性"定义不明确
- ❓ 相对于什么的新颖性？（训练数据？其他模型？）

**可能的实现方向**：

**方案1：N-gram新颖性（相对于参考语料）**
```python
def calculate_ngram_novelty(text, reference_corpus):
    """计算N-gram新颖性"""
    import jieba
    
    # 构建参考语料的N-gram集合
    ref_ngrams = set()
    for ref_text in reference_corpus:
        tokens = list(jieba.cut(ref_text))
        ngrams = [tuple(tokens[i:i+3]) for i in range(len(tokens)-2)]
        ref_ngrams.update(ngrams)
    
    # 计算生成文本中的新N-gram比例
    tokens = list(jieba.cut(text))
    gen_ngrams = [tuple(tokens[i:i+3]) for i in range(len(tokens)-2)]
    
    if len(gen_ngrams) == 0:
        return 0.0
    
    novel_ngrams = [ng for ng in gen_ngrams if ng not in ref_ngrams]
    return len(novel_ngrams) / len(gen_ngrams)
```

**方案2：主题新颖性（基于LDA）**
```python
def calculate_topic_novelty(text, reference_topics):
    """计算主题新颖性"""
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import CountVectorizer
    import jieba
    
    # 提取主题分布
    tokens = ' '.join(jieba.cut(text))
    vectorizer = CountVectorizer()
    doc_term_matrix = vectorizer.fit_transform([tokens])
    
    lda = LatentDirichletAllocation(n_components=5)
    topic_dist = lda.fit_transform(doc_term_matrix)[0]
    
    # 计算与参考主题的距离
    from scipy.spatial.distance import jensenshannon
    novelty = jensenshannon(topic_dist, reference_topics)
    
    return novelty
```

**限制**：
- ❌ 需要参考语料库（当前数据集没有）
- ❌ 计算成本高
- ⚠️ 新颖不等于好（可能是胡言乱语）

**建议**：
- ❌ 暂不实现（定义不清、数据不足）
- 💡 可以用Distinct-N间接反映词汇新颖性


#### 主题多样性 ⚠️ 需要多个样本

**定义**：
- 评估同一模型生成的多个文本是否覆盖不同主题

**实现方案**：
```python
def calculate_topic_diversity(texts, n_topics=5):
    """计算主题多样性"""
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import CountVectorizer
    import jieba
    import numpy as np
    
    # 分词
    tokenized_texts = [' '.join(jieba.cut(text)) for text in texts]
    
    # 构建词频矩阵
    vectorizer = CountVectorizer(max_features=1000)
    doc_term_matrix = vectorizer.fit_transform(tokenized_texts)
    
    # LDA主题建模
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    topic_distributions = lda.fit_transform(doc_term_matrix)
    
    # 计算主题分布的熵（熵越高，主题越多样）
    avg_topic_dist = topic_distributions.mean(axis=0)
    entropy = -np.sum(avg_topic_dist * np.log(avg_topic_dist + 1e-10))
    
    # 归一化到[0, 1]
    max_entropy = np.log(n_topics)
    diversity = entropy / max_entropy
    
    return diversity
```

**应用场景**：
- ✅ 评估模型在不同提示下的主题覆盖能力
- ✅ 检测模型是否过度依赖某些主题模板

**限制**：
- ⚠️ 需要足够多的样本（至少10+）
- ⚠️ 计算成本较高
- ⚠️ 对于单个响应无法评估

**建议**：
- ✅ 作为模型级别的补充指标
- ⚠️ 不作为单个响应的评分指标


## 3. 推荐评估方案

基于可行性分析，推荐以下评估方案：

### 3.1 核心指标（必须实现）

| 维度 | 指标 | 优先级 | 计算成本 | 可行性 |
|------|------|--------|----------|--------|
| 多样性 | Distinct-2 | ⭐⭐⭐ | 低 | ✅ 高 |
| 多样性 | Distinct-1 | ⭐⭐ | 低 | ✅ 高 |
| 流畅性 | Perplexity (PPL) | ⭐⭐⭐ | 中 | ✅ 高 |
| 基础 | 文本长度 | ⭐⭐ | 低 | ✅ 高 |

### 3.2 补充指标（可选实现）

| 维度 | 指标 | 优先级 | 计算成本 | 可行性 |
|------|------|--------|----------|--------|
| 多样性 | Distinct-3 | ⭐ | 低 | ✅ 高 |
| 多样性 | 句向量语义多样性 | ⭐ | 高 | ⚠️ 中 |
| 创造力 | 主题多样性（模型级） | ⭐ | 高 | ⚠️ 中 |

### 3.3 不推荐指标

| 指标 | 原因 |
|------|------|
| Self-BLEU | 数据限制（每个提示只有1次生成） |
| 语法错误率 | 中文工具不成熟，PPL已覆盖 |
| Novelty | 定义不清，缺少参考语料 |

## 4. 实现方案

### 4.1 评估器设计

```python
# data/analize/scripts/quality_evaluation/creative_evaluator.py

import jieba
from typing import Dict, List, Optional
from .base_evaluator import BaseEvaluator

class CreativeEvaluator(BaseEvaluator):
    """创意写作任务评估器"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.ppl_model = None  # 延迟加载
    
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict = None) -> Dict[str, float]:
        """
        评估创意写作质量
        
        Args:
            generated: 生成的文本
            reference: 参考答案（创意写作通常没有）
            context: 额外上下文
        
        Returns:
            Dict[str, float]: 多维度指标
        """
        scores = {}
        
        # 1. 多样性指标
        scores['distinct_1'] = self._calculate_distinct_n(generated, n=1)
        scores['distinct_2'] = self._calculate_distinct_n(generated, n=2)
        scores['distinct_3'] = self._calculate_distinct_n(generated, n=3)
        
        # 2. 流畅性指标
        scores['perplexity'] = self._calculate_perplexity(generated)
        
        # 3. 基础指标
        scores['text_length'] = len(generated)
        scores['word_count'] = len(list(jieba.cut(generated)))
        
        return scores
    
    def _calculate_distinct_n(self, text: str, n: int = 2) -> float:
        """计算Distinct-N"""
        tokens = list(jieba.cut(text))
        
        if len(tokens) < n:
            return 0.0
        
        ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
        
        if len(ngrams) == 0:
            return 0.0
        
        return len(set(ngrams)) / len(ngrams)
    
    def _calculate_perplexity(self, text: str) -> float:
        """计算困惑度"""
        if self.ppl_model is None:
            self._load_ppl_model()
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            # 编码
            encodings = self.tokenizer(text, return_tensors='pt', 
                                      max_length=512, truncation=True)
            
            # 计算困惑度
            with torch.no_grad():
                outputs = self.ppl_model(**encodings, labels=encodings['input_ids'])
                loss = outputs.loss
                perplexity = torch.exp(loss).item()
            
            return perplexity
        except Exception as e:
            print(f"⚠️  PPL calculation failed: {e}")
            return None
    
    def _load_ppl_model(self):
        """加载困惑度计算模型"""
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        model_name = self.config.get('ppl_model', 'uer/gpt2-chinese-cluecorpussmall')
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        print(f"Loading PPL model: {model_name} on {device}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.ppl_model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        self.ppl_model.eval()
    
    def get_metric_categories(self) -> Dict[str, List[str]]:
        """返回指标分类"""
        return {
            'diversity': ['distinct_1', 'distinct_2', 'distinct_3'],
            'fluency': ['perplexity'],
            'basic': ['text_length', 'word_count']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向"""
        return {
            'distinct_1': True,   # 越大越好
            'distinct_2': True,
            'distinct_3': True,
            'perplexity': False,  # 越小越好
            'text_length': True,  # 适中为好（但简化为越大越好）
            'word_count': True
        }
```


### 4.2 批量评估脚本

```python
# data/analize/scripts/evaluate_creative_quality.py

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from quality_evaluation.creative_evaluator import CreativeEvaluator

def evaluate_creative_quality(data_dir: Path, output_dir: Path):
    """评估创意写作任务质量"""
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/creative/creative_responses.csv'
    df = pd.read_csv(responses_file)
    
    # 初始化评估器
    config = {
        'ppl_model': 'uer/gpt2-chinese-cluecorpussmall',
        'aggregation': 'none'  # 保留所有原始指标
    }
    evaluator = CreativeEvaluator(config)
    
    # 评估每个模型的每个响应
    results = []
    
    for model in tqdm(df['model'], desc="Evaluating models"):
        for col in df.columns:
            if col == 'model':
                continue
            
            # 提取响应文本
            response = df[df['model'] == model][col].values[0]
            
            if pd.isna(response) or len(str(response).strip()) == 0:
                continue
            
            # 评估质量
            scores = evaluator.evaluate(str(response))
            
            # 保存结果
            result = {
                'model': model,
                'question_id': col,
                **scores
            }
            results.append(result)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存详细结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'creative_quality_scores.csv'
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Creative quality evaluation completed!")
    print(f"📊 Results saved to: {output_file}")
    print(f"📈 Total evaluations: {len(results_df)}")
    
    # 生成汇总统计
    generate_summary_stats(results_df, output_dir)
    
    return results_df

def generate_summary_stats(df: pd.DataFrame, output_dir: Path):
    """生成汇总统计"""
    
    # 按模型汇总
    metric_cols = ['distinct_1', 'distinct_2', 'distinct_3', 
                   'perplexity', 'text_length', 'word_count']
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'creative_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"📊 Summary statistics: {summary_file}")
    
    # 打印Top 3模型（按Distinct-2排序）
    print("\n🏆 Top 3 Models by Distinct-2:")
    top_models = df.groupby('model')['distinct_2'].mean().sort_values(ascending=False).head(3)
    for rank, (model, score) in enumerate(top_models.items(), 1):
        print(f"  {rank}. {model}: {score:.4f}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估创意写作质量')
    parser.add_argument('--data-dir', type=str, 
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/creative_quality',
                       help='输出目录')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_creative_quality(data_dir, output_dir)
```


## 5. 依赖安装

### 5.1 必需依赖

```bash
# 激活环境
conda activate bartscore

# 安装基础依赖
pip install jieba pandas numpy tqdm

# 安装深度学习依赖（用于PPL计算）
pip install transformers torch
```

### 5.2 模型下载

首次运行时会自动下载以下模型：

```python
# GPT-2中文模型（用于困惑度计算）
# 模型：uer/gpt2-chinese-cluecorpussmall
# 大小：约300MB
# 缓存位置：~/.cache/huggingface/
```

### 5.3 GPU加速配置

```python
# 检测GPU可用性
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
```

## 6. 运行指南

### 6.1 快速开始

```bash
# 1. 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 2. 运行评估
cd data/analize/scripts
python evaluate_creative_quality.py

# 3. 查看结果
type ..\results\creative_quality\creative_quality_scores.csv
```

### 6.2 预期输出

```
data/analize/results/creative_quality/
├── creative_quality_scores.csv      # 详细评分
│   ├── model
│   ├── question_id
│   ├── distinct_1
│   ├── distinct_2
│   ├── distinct_3
│   ├── perplexity
│   ├── text_length
│   └── word_count
└── creative_quality_summary.csv     # 汇总统计
    ├── model
    ├── distinct_2_mean
    ├── distinct_2_std
    ├── perplexity_mean
    └── ...
```

### 6.3 性能估算

基于当前硬件配置（RTX 4060 8GB）：

- 每个响应评估时间：~0.5-1秒（含PPL计算）
- 总评估时间：~5-10分钟（12个模型 × 5个问题）
- GPU显存占用：~2GB（GPT-2模型）


## 7. 指标解释与应用

### 7.1 指标含义

#### Distinct-1/2/3
- **含义**：N-gram去重率，衡量词汇/短语多样性
- **范围**：[0, 1]
- **解释**：
  - 0.8-1.0：非常多样，词汇丰富
  - 0.5-0.8：中等多样性
  - 0.0-0.5：重复度高，词汇贫乏
- **应用**：
  - 检测模板化生成
  - 评估创造力
  - 对比不同模型的表达丰富度

#### Perplexity (困惑度)
- **含义**：语言模型对文本的困惑程度
- **范围**：[1, +∞)
- **解释**：
  - 10-50：非常流畅，符合语言规律
  - 50-100：较流畅
  - 100-200：一般流畅
  - >200：不流畅，可能有语法错误
- **应用**：
  - 评估语言流畅度
  - 检测语法错误
  - 对比不同模型的语言质量

#### 文本长度
- **含义**：生成文本的字符数/词数
- **范围**：[0, +∞)
- **解释**：
  - 过短：可能未完成任务
  - 适中：符合要求
  - 过长：可能冗余
- **应用**：
  - 检测生成完整性
  - 评估简洁性
  - 对比不同模型的生成长度偏好

### 7.2 综合评分建议

#### 方案1：加权平均（简单）

```python
def calculate_creative_score(metrics):
    """计算创意写作综合分数"""
    # 归一化
    distinct_2_norm = metrics['distinct_2']  # 已在[0,1]
    ppl_norm = 1 / (1 + metrics['perplexity'] / 100)  # 转换为越大越好
    
    # 加权平均
    score = 0.6 * distinct_2_norm + 0.4 * ppl_norm
    
    return score
```

**权重说明**：
- Distinct-2: 60%（多样性是创意写作的核心）
- Perplexity: 40%（流畅性是基础要求）

#### 方案2：多维度呈现（推荐）

不计算单一综合分数，而是保留多维度指标：

```python
# 多样性维度
diversity_score = (distinct_1 + distinct_2 + distinct_3) / 3

# 流畅性维度
fluency_score = 1 / (1 + perplexity / 100)

# 完整性维度
completeness_score = min(text_length / 200, 1.0)  # 假设200字为完整
```

**优势**：
- 保留完整信息
- 支持不同应用场景
- 避免主观权重


## 8. 可视化分析

### 8.1 推荐图表

#### 图表1：多样性对比（柱状图）
```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_diversity_comparison(summary_df):
    """绘制多样性对比图"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    models = summary_df.index
    distinct_2 = summary_df[('distinct_2', 'mean')]
    
    sns.barplot(x=models, y=distinct_2, ax=ax)
    ax.set_xlabel('Model')
    ax.set_ylabel('Distinct-2 Score')
    ax.set_title('Creative Writing Diversity Comparison')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('creative_diversity_comparison.png', dpi=300)
```

#### 图表2：多样性vs流畅性（散点图）
```python
def plot_diversity_vs_fluency(df):
    """绘制多样性vs流畅性散点图"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        ax.scatter(model_data['distinct_2'], 
                  1 / (1 + model_data['perplexity'] / 100),
                  label=model, alpha=0.6, s=100)
    
    ax.set_xlabel('Diversity (Distinct-2)')
    ax.set_ylabel('Fluency (1 / (1 + PPL/100))')
    ax.set_title('Diversity vs Fluency Trade-off')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('diversity_vs_fluency.png', dpi=300)
```

#### 图表3：雷达图（多维度对比）
```python
def plot_radar_chart(summary_df):
    """绘制雷达图"""
    from math import pi
    
    # 选择Top 5模型
    top_models = summary_df.nlargest(5, ('distinct_2', 'mean')).index
    
    # 指标
    categories = ['Distinct-1', 'Distinct-2', 'Distinct-3', 'Fluency']
    N = len(categories)
    
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    for model in top_models:
        values = [
            summary_df.loc[model, ('distinct_1', 'mean')],
            summary_df.loc[model, ('distinct_2', 'mean')],
            summary_df.loc[model, ('distinct_3', 'mean')],
            1 / (1 + summary_df.loc[model, ('perplexity', 'mean')] / 100)
        ]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, label=model)
        ax.fill(angles, values, alpha=0.15)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 1)
    ax.set_title('Creative Writing Quality Radar Chart', size=16, y=1.08)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    plt.savefig('creative_radar_chart.png', dpi=300)
```

### 8.2 统计分析

#### 相关性分析
```python
def analyze_correlations(df):
    """分析指标间相关性"""
    import seaborn as sns
    
    metric_cols = ['distinct_1', 'distinct_2', 'distinct_3', 
                   'perplexity', 'text_length']
    
    corr_matrix = df[metric_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', 
                center=0, square=True, linewidths=1)
    plt.title('Creative Quality Metrics Correlation Matrix')
    plt.tight_layout()
    plt.savefig('creative_correlation_matrix.png', dpi=300)
    
    print("\n📊 Correlation Analysis:")
    print(corr_matrix)
```

#### 显著性检验
```python
def significance_test(df):
    """模型间差异显著性检验"""
    from scipy import stats
    
    models = df['model'].unique()
    
    print("\n📊 Pairwise T-test (Distinct-2):")
    for i, model_i in enumerate(models):
        for model_j in models[i+1:]:
            data_i = df[df['model'] == model_i]['distinct_2']
            data_j = df[df['model'] == model_j]['distinct_2']
            
            t_stat, p_value = stats.ttest_ind(data_i, data_j)
            
            if p_value < 0.05:
                print(f"  {model_i} vs {model_j}: p={p_value:.4f} ✅ Significant")
            else:
                print(f"  {model_i} vs {model_j}: p={p_value:.4f} ❌ Not significant")
```


## 9. 潜在问题与解决方案

### 9.1 困惑度计算问题

**问题1：模型加载失败**
```
解决方案：
1. 检查网络连接（首次需下载模型）
2. 手动指定缓存目录：
   export HF_HOME=/path/to/cache
3. 使用国内镜像：
   export HF_ENDPOINT=https://hf-mirror.com
```

**问题2：显存不足**
```
解决方案：
1. 使用更小的模型：
   config = {'ppl_model': 'uer/gpt2-chinese-cluecorpussmall'}
2. 减小batch size（逐个处理）
3. 使用CPU计算（较慢）：
   device = 'cpu'
```

**问题3：文本过长导致截断**
```
解决方案：
1. 设置max_length参数：
   encodings = tokenizer(text, max_length=512, truncation=True)
2. 分段计算后平均：
   chunks = split_text(text, max_length=512)
   ppls = [calculate_ppl(chunk) for chunk in chunks]
   avg_ppl = sum(ppls) / len(ppls)
```

### 9.2 中文分词问题

**问题：jieba分词不准确**
```
解决方案：
1. 使用自定义词典：
   jieba.load_userdict('custom_dict.txt')
2. 添加专业词汇：
   jieba.add_word('生成式AI')
3. 使用其他分词工具：
   - pkuseg（更准确但较慢）
   - thulac（清华分词）
```

### 9.3 评估速度优化

**优化策略**：

1. **批量处理**
```python
def batch_evaluate(texts, batch_size=8):
    """批量评估"""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_results = evaluator.evaluate_batch(batch)
        results.extend(batch_results)
    return results
```

2. **缓存模型**
```python
# 全局加载一次
evaluator = CreativeEvaluator(config)
evaluator._load_ppl_model()  # 预加载

# 重复使用
for text in texts:
    scores = evaluator.evaluate(text)
```

3. **并行计算**
```python
from multiprocessing import Pool

def parallel_evaluate(texts, n_workers=4):
    """并行评估（仅用于Distinct-N等轻量指标）"""
    with Pool(n_workers) as pool:
        results = pool.map(calculate_distinct_metrics, texts)
    return results
```


## 10. 总结与建议

### 10.1 方法可行性总结

| 方法 | 可行性 | 推荐度 | 理由 |
|------|--------|--------|------|
| **Distinct-1/2/3** | ✅ 高 | ⭐⭐⭐ | 计算简单、效果好、无需外部模型 |
| **Perplexity** | ✅ 高 | ⭐⭐⭐ | 客观量化流畅度、广泛应用 |
| **Self-BLEU** | ❌ 低 | ⭐ | 数据限制（需多次生成） |
| **句向量语义多样性** | ⚠️ 中 | ⭐ | 成本高、收益有限 |
| **语法错误率** | ⚠️ 中 | ⭐ | 工具不成熟、PPL已覆盖 |
| **Novelty** | ❌ 低 | ⭐ | 定义不清、缺少参考语料 |
| **主题多样性** | ⚠️ 中 | ⭐⭐ | 适合模型级评估、单样本无效 |

### 10.2 最终推荐方案

#### 核心指标组合（必须实现）
```python
creative_quality_metrics = {
    'diversity': {
        'distinct_2': float,      # 核心多样性指标
        'distinct_1': float,      # 补充
    },
    'fluency': {
        'perplexity': float,      # 核心流畅性指标
    },
    'basic': {
        'text_length': int,       # 基础指标
        'word_count': int
    }
}
```

#### 可选扩展（资源充足时）
- Distinct-3（低成本扩展）
- 主题多样性（模型级别分析）

### 10.3 实施建议

#### 阶段1：基础实现（1-2天）
1. ✅ 实现Distinct-1/2/3计算
2. ✅ 实现文本长度统计
3. ✅ 批量评估脚本
4. ✅ 结果保存和汇总

#### 阶段2：深度指标（2-3天）
1. ⏳ 集成困惑度计算
2. ⏳ 模型下载和缓存管理
3. ⏳ GPU加速优化
4. ⏳ 错误处理和日志

#### 阶段3：分析可视化（1-2天）
1. ⏳ 生成对比图表
2. ⏳ 统计分析报告
3. ⏳ 集成到主分析流程

### 10.4 预期成果

#### 输出文件
```
data/analize/results/creative_quality/
├── creative_quality_scores.csv          # 详细评分（60行）
├── creative_quality_summary.csv         # 汇总统计（12行）
├── creative_diversity_comparison.png    # 多样性对比图
├── diversity_vs_fluency.png            # 散点图
├── creative_radar_chart.png            # 雷达图
└── creative_correlation_matrix.png     # 相关性矩阵
```

#### 关键发现（预期）
- 识别多样性最高的模型
- 发现多样性与流畅性的权衡关系
- 检测模板化生成问题
- 为模型选择提供数据支持

### 10.5 后续优化方向

1. **人工评估对比**：抽样进行人工评分，验证自动指标的有效性
2. **领域适配**：针对不同创意写作类型（诗歌、故事、广告）调整权重
3. **时间序列分析**：跟踪模型迭代过程中的质量变化
4. **公平性分析**：检测模型在不同主题/风格上的表现差异

---

## 附录

### A. 参考文献

1. Li, J., et al. (2016). "A Diversity-Promoting Objective Function for Neural Conversation Models." NAACL.
2. Zhu, W., et al. (2018). "Texygen: A Benchmarking Platform for Text Generation Models." SIGIR.
3. Hashimoto, T., et al. (2019). "Unifying Human and Statistical Evaluation for Natural Language Generation." NAACL.

### B. 相关工具

- **jieba**: https://github.com/fxsjy/jieba
- **transformers**: https://huggingface.co/docs/transformers
- **GPT-2中文模型**: https://huggingface.co/uer/gpt2-chinese-cluecorpussmall

### C. 联系方式

如有问题或建议，请参考项目文档或提交Issue。

---

**文档版本**: v1.0  
**创建日期**: 2026-03-04  
**作者**: Kiro AI Assistant  
**状态**: 设计完成，待实施
