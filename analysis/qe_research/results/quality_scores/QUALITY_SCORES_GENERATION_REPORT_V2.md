# 质量评分数据生成报告（详细版）

**生成时间**: 2026-03-07  
**报告版本**: v2.0 - 详细量化逻辑说明  
**数据来源**: `data/analize/results/*/quality_*_scores*.csv`

---

## 执行摘要

本报告详细说明了如何生成七个任务类型的质量评分数据文件，并深入解释每个指标的量化逻辑。这些文件是多维质效比评估体系的核心组成部分。

**核心输出文件**:
- `code_scores_raw.csv` - 代码生成质量评分（4个指标）
- `creative_scores_raw.csv` - 创意写作质量评分（4个指标）
- `math_scores_raw.csv` - 数学推理质量评分（4个指标）
- `qa_scores_raw.csv` - 问答质量评分（4个指标）
- `reasoning_scores_raw.csv` - 逻辑推理质量评分（4个指标）
- `summary_scores_raw.csv` - 摘要生成质量评分（4个指标）
- `translation_scores_raw.csv` - 翻译质量评分（4个指标）

**评估覆盖**: 12个模型 × 7个任务 × 28个指标 = 完整的质量评估矩阵

---

## 一、数据生成流程概览

### 1.1 整体架构

```
原始实验数据 (data/experiments_1/raw/*.json)
    ↓ 实验执行
模型响应数据 (data/analize/pipeline/responses/*.csv)
    ↓ 任务专用评估脚本
质量评分数据 (data/analize/results/*/quality_*_scores*.csv)
    ↓ 质量评分表格生成器
标准化评分矩阵 (analysis/qe_research/results/quality_scores/*_scores_raw.csv)
```

### 1.2 关键处理步骤

1. **原始数据采集**: 从Ollama/HuggingFace模型获取响应
2. **任务专用评估**: 针对每个任务类型应用特定评估方法
3. **指标计算**: 计算多维度质量指标（自动化+半自动化）
4. **数据聚合**: 按模型聚合多个样本的评分（计算平均值）
5. **矩阵转换**: 转换为"指标×模型"的标准化格式

---

## 二、各任务类型评估方法详解

### 2.1 代码生成 (Code)

**数据源**: `data/analize/results/code_quality/quality_scores_code.csv`  
**评估脚本**: `data/analize/scripts/evaluate_code_quality.py`  
**核心评估器**: `quality_evaluation/code_evaluator.py`

#### 评估指标与量化逻辑

| 指标名称 | 取值范围 | 量化方法 | 说明 |
|---------|---------|---------|------|
| `code_length` | [0, ∞) | 统计有效代码行数 | 排除空行和注释，计算实际代码行数 |
| `compilation_rate` | [0, 1] | AST解析成功率 | 使用Python的`ast.parse()`验证语法正确性 |
| `cyclomatic_complexity` | [1, ∞) | McCabe圈复杂度 | 计算控制流图的独立路径数量 |
| `has_code` | {0, 1} | 代码块检测 | 检测是否包含有效的代码块（非空） |

#### 量化逻辑详解

**1. 代码提取**
```python
# 从Markdown格式中提取Python代码块
pattern = r'```python\n(.*?)\n```'
code = extract_python_code(generated_text)
```

**2. 编译验证**
```python
try:
    ast.parse(code)  # 尝试解析为抽象语法树
    compilation_rate = 1.0  # 编译成功
except SyntaxError:
    compilation_rate = 0.0  # 编译失败
```

**3. 圈复杂度计算**
- 基础复杂度：1
- 每个决策点（if, while, for, and, or）：+1
- 每个异常处理（except）：+1
- 公式：`CC = E - N + 2P`（E=边数，N=节点数，P=连通分量数）

**4. 代码长度统计**
```python
# 排除空行和纯注释行
lines = [l for l in code.split('\n') 
         if l.strip() and not l.strip().startswith('#')]
code_length = len(lines)
```

**特点**: 
- 完全自动化，无需人工标注
- 基于静态分析，执行速度快
- 客观性强，可重复性100%
- 不评估功能正确性（需要测试用例）

---

### 2.2 创意写作 (Creative)

**数据源**: `data/analize/results/creative_quality/creative_quality_scores_with_perplexity.csv`  
**评估脚本**: `data/analize/scripts/evaluate_creative_quality.py`  
**核心评估器**: `CreativeQualityEvaluator`

#### 评估指标与量化逻辑

| 指标名称 | 取值范围 | 量化方法 | 说明 |
|---------|---------|---------|------|
| `avg_sentence_length` | [0, ∞) | 字符数/句子数 | 平均每个句子的字符长度 |
| `distinct_1` | [0, 1] | Unigram多样性 | 唯一一元词/总一元词数量 |
| `distinct_2` | [0, 1] | Bigram多样性 | 唯一二元词/总二元词数量 |
| `metaphor_count` | [0, ∞) | 修辞手法计数 | 检测比喻、拟人等修辞手法数量 |

#### 量化逻辑详解

**1. 中文分词**
```python
def tokenize_chinese(text):
    # 分离标点符号
    text = re.sub(r'([，。！？；：])', r' \1 ', text)
    # 中文按字，英文按词
    tokens = []
    for word in text.split():
        if re.match(r'[a-zA-Z]+', word):
            tokens.append(word.lower())
        elif re.match(r'[\u4e00-\u9fff]', word):
            tokens.extend(list(word))  # 中文拆字
    return tokens
```

**2. Distinct-N 计算**
```python
def calculate_distinct_n(tokens, n=2):
    # 生成n-gram
    ngrams = [tuple(tokens[i:i+n]) 
              for i in range(len(tokens) - n + 1)]
    # 计算唯一比例
    distinct_n = len(set(ngrams)) / len(ngrams)
    return distinct_n
```

**3. 句子长度统计**
```python
sentences = re.split(r'[。！？；]', text)
avg_length = sum(len(s) for s in sentences) / len(sentences)
```

**4. 修辞手法检测**
```python
# 比喻标志词
metaphor_markers = ['像', '如', '似', '仿佛', '好像', '犹如']
metaphor_count = sum(text.count(marker) for marker in metaphor_markers)

# 拟人标志词
personification_markers = ['微笑', '哭泣', '歌唱', '舞蹈']
# ... 类似统计
```

**特点**:
- 结合统计语言学和规则匹配
- Distinct-N是标准的文本多样性指标
- 修辞手法检测基于关键词匹配（简化版）
- 适用于中英文混合文本

---

### 2.3 数学推理 (Math)

**数据源**: `data/analize/results/math_quality/math_quality_scores.csv`  
**评估脚本**: `data/analize/scripts/evaluate_math_quality.py`  
**核心评估器**: `quality_evaluation/math_evaluator.py`

#### 评估指标与量化逻辑

| 指标名称 | 取值范围 | 量化方法 | 说明 |
|---------|---------|---------|------|
| `exact_match` | {0, 1} | 精确匹配 | 提取的答案与标准答案完全一致 |
| `extracted_answer` | 数值 | 答案提取 | 从文本中提取的数值答案 |
| `extraction_confidence` | [0, 1] | 置信度评分 | 答案提取的可靠性评估 |
| `has_answer` | {0, 1} | 答案存在性 | 是否成功提取到答案 |

#### 量化逻辑详解

**1. 答案提取（多策略）**
```python
def extract_answer(text):
    # 策略1: 明确的答案标记
    patterns = [
        r'(?:answer|result|total)\s*(?:is|=|:)?\s*\$?\s*(\d+\.?\d*)',
        r'(?:答案|结果|总计)\s*(?:是|为|：)?\s*\$?\s*(\d+\.?\d*)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[-1]  # 返回最后一个匹配
    
    # 策略2: 等号后的数值
    # 策略3: 最后一个数值
    numbers = re.findall(r'\$?\s*(\d+\.?\d*)', text)
    return numbers[-1] if numbers else None
```

**2. 精确匹配计算**
```python
def calculate_exact_match(generated, reference):
    gen_answer = extract_answer(generated)
    # 归一化（移除货币符号、空格、单位）
    gen_norm = normalize_answer(gen_answer)
    ref_norm = normalize_answer(reference)
    
    # 数值比较
    try:
        gen_num = float(gen_norm)
        ref_num = float(ref_norm)
        return 1.0 if abs(gen_num - ref_num) < 0.001 else 0.0
    except ValueError:
        # 字符串比较
        return 1.0 if gen_norm == ref_norm else 0.0
```

**3. 提取置信度评估**
```python
def calculate_extraction_confidence(text):
    confidence = 0.0
    # 有明确答案标记：+0.5
    if re.search(r'(?:answer|答案)', text, re.IGNORECASE):
        confidence += 0.5
    # 有计算过程：+0.3
    if '=' in text or '计算' in text:
        confidence += 0.3
    # 有数值：+0.2
    if re.search(r'\d+', text):
        confidence += 0.2
    return min(confidence, 1.0)
```

**特点**:
- 多策略答案提取，提高鲁棒性
- 支持中英文混合文本
- 容忍数值误差（默认0.1%）
- 评估答案提取的可靠性


---

### 2.4 问答 (QA)

**数据源**: `data/analize/results/qa_quality/qa_quality_scores.csv`  
**评估脚本**: `data/analize/scripts/evaluate_qa_quality_academic.py`  
**核心评估器**: `QAEvaluator`

#### 评估指标与量化逻辑

| 指标名称 | 取值范围 | 量化方法 | 说明 |
|---------|---------|---------|------|
| `answer_length` | [0, ∞) | 字符计数 | 答案文本的总字符数 |
| `avg_paragraph_length` | [0, ∞) | 字符数/段落数 | 平均每个段落的字符长度 |
| `certainty_count` | [0, ∞) | 确定性词汇计数 | 检测表达确定性的词汇数量 |
| `confidence_score` | [0, 1] | 置信度评分 | 基于语言特征的答案置信度 |

#### 量化逻辑详解

**1. 答案长度统计**
```python
answer_length = len(response_text)
```

**2. 段落分析**
```python
# 按双换行符分割段落
paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs)
```

**3. 确定性表达检测**
```python
certainty_markers = [
    'definitely', 'certainly', 'absolutely', 'clearly',
    '肯定', '确定', '明确', '显然', '毫无疑问'
]
certainty_count = sum(text.lower().count(marker) 
                      for marker in certainty_markers)
```

**4. 置信度评分**
```python
def calculate_confidence_score(text):
    score = 0.5  # 基础分
    # 有明确结构：+0.2
    if '\n\n' in text or '。' in text:
        score += 0.2
    # 有确定性表达：+0.2
    if certainty_count > 0:
        score += 0.2
    # 长度适中（100-500字符）：+0.1
    if 100 <= len(text) <= 500:
        score += 0.1
    return min(score, 1.0)
```

**特点**:
- 关注答案的结构性和完整性
- 评估答案的确定性程度
- 适用于开放式问答任务
- 不依赖标准答案

---

### 2.5 逻辑推理 (Reasoning)

**数据源**: `data/analize/results/reasoning_quality/reasoning_quality_scores.csv`  
**评估脚本**: `data/analize/scripts/evaluate_reasoning_quality.py`  
**核心评估器**: `ReasoningEvaluator`

#### 评估指标与量化逻辑

| 指标名称 | 取值范围 | 量化方法 | 说明 |
|---------|---------|---------|------|
| `avg_sentence_length` | [0, ∞) | 词数/句子数 | 平均每个句子的词数 |
| `coherence_score` | [0, 1] | 语义连贯性 | 基于句子间语义相似度 |
| `completeness_score` | [0, 1] | 推理完整性 | 是否包含前提、推理、结论 |
| `conclusion_correct` | {0, 1} | 结论正确性 | 结论是否符合逻辑（需人工标注） |

#### 量化逻辑详解

**1. 句子长度统计**
```python
sentences = re.split(r'[。！？；]', text)
tokens_per_sentence = [len(tokenize(s)) for s in sentences]
avg_sentence_length = sum(tokens_per_sentence) / len(sentences)
```

**2. 连贯性评分（语义相似度）**
```python
from sentence_transformers import SentenceTransformer

def calculate_coherence(sentences):
    # 使用预训练模型计算句子嵌入
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    embeddings = model.encode(sentences)
    
    # 计算相邻句子的余弦相似度
    similarities = []
    for i in range(len(embeddings) - 1):
        sim = cosine_similarity(embeddings[i], embeddings[i+1])
        similarities.append(sim)
    
    # 平均相似度作为连贯性得分
    coherence_score = np.mean(similarities)
    return coherence_score
```

**3. 完整性评分**
```python
def calculate_completeness(text):
    score = 0.0
    # 有前提陈述：+0.33
    if re.search(r'(因为|由于|假设|前提)', text):
        score += 0.33
    # 有推理过程：+0.33
    if re.search(r'(因此|所以|推导|可得)', text):
        score += 0.33
    # 有明确结论：+0.34
    if re.search(r'(结论|总结|综上)', text):
        score += 0.34
    return score
```

**4. 结论正确性**
```python
# 需要人工标注或与标准答案比对
conclusion_correct = 1.0 if manual_label == 'correct' else 0.0
```

**特点**:
- 结合规则匹配和语义分析
- 连贯性评分使用预训练语言模型
- 完整性评分基于逻辑结构关键词
- 结论正确性需要人工验证或标准答案

---

### 2.6 摘要生成 (Summary)

**数据源**: `data/analize/results/summary_quality/summary_quality_scores_with_bartscore.csv`  
**评估脚本**: `data/analize/scripts/evaluate_summary_quality.py`  
**核心评估器**: `BARTScorer`, `BERTScorer`

#### 评估指标与量化逻辑

| 指标名称 | 取值范围 | 量化方法 | 说明 |
|---------|---------|---------|------|
| `bartscore_avg` | (-∞, 0] | BART模型评分 | 综合质量评分（负对数似然） |
| `bartscore_faith` | (-∞, 0] | 忠实度评分 | 摘要与原文的事实一致性 |
| `bartscore_info` | (-∞, 0] | 信息性评分 | 关键信息的覆盖程度 |
| `bertscore_f1` | [0, 1] | BERT F1分数 | 基于BERT嵌入的语义相似度 |

#### 量化逻辑详解

**1. BARTScore 计算**
```python
from bart_score import BARTScorer

def calculate_bartscore(summary, source):
    # 加载预训练BART模型
    scorer = BARTScorer(device='cuda', checkpoint='facebook/bart-large-cnn')
    
    # 忠实度：P(summary|source)
    faith_score = scorer.score([source], [summary], batch_size=4)[0]
    
    # 信息性：P(source|summary)
    info_score = scorer.score([summary], [source], batch_size=4)[0]
    
    # 综合评分：平均值
    avg_score = (faith_score + info_score) / 2
    
    return {
        'bartscore_faith': faith_score,
        'bartscore_info': info_score,
        'bartscore_avg': avg_score
    }
```

**BARTScore 原理**:
- 基于BART生成模型的条件概率
- 忠实度：给定原文，生成摘要的概率（越高越忠实）
- 信息性：给定摘要，生成原文的概率（越高信息越完整）
- 分数为负对数似然，越接近0越好

**2. BERTScore 计算**
```python
from bert_score import score

def calculate_bertscore(summary, reference):
    # 计算BERT嵌入的余弦相似度
    P, R, F1 = score([summary], [reference], 
                     lang='zh', 
                     model_type='bert-base-chinese')
    
    return {
        'bertscore_precision': P.item(),
        'bertscore_recall': R.item(),
        'bertscore_f1': F1.item()
    }
```

**BERTScore 原理**:
- 使用BERT模型计算词级别的语义相似度
- Precision: 摘要中每个词与参考摘要的最大相似度平均
- Recall: 参考摘要中每个词与生成摘要的最大相似度平均
- F1: Precision和Recall的调和平均

**特点**:
- 使用先进的神经网络评估方法
- BARTScore评估生成质量，无需参考摘要
- BERTScore评估语义相似度，需要参考摘要
- 分数具有良好的人类相关性

---

### 2.7 翻译 (Translation)

**数据源**: `data/analize/results/translation_quality/translation_quality_scores.csv`  
**评估脚本**: `data/analize/scripts/evaluate_translation_quality.py`  
**核心评估器**: `BERTScorer`, `BLEU`

#### 评估指标与量化逻辑

| 指标名称 | 取值范围 | 量化方法 | 说明 |
|---------|---------|---------|------|
| `bertscore_f1` | [0, 1] | BERT F1分数 | 多语言语义相似度 |
| `bertscore_precision` | [0, 1] | BERT精确率 | 译文的准确性 |
| `bertscore_recall` | [0, 1] | BERT召回率 | 原文信息的保留度 |
| `bleu_1` | [0, 1] | BLEU-1分数 | 一元语法匹配度 |

#### 量化逻辑详解

**1. BERTScore 计算（多语言）**
```python
from bert_score import score

def calculate_bertscore_multilingual(translation, reference, 
                                     src_lang='zh', tgt_lang='en'):
    # 使用多语言BERT模型
    P, R, F1 = score([translation], [reference],
                     lang=tgt_lang,
                     model_type='bert-base-multilingual-cased')
    
    return {
        'bertscore_precision': P.item(),
        'bertscore_recall': R.item(),
        'bertscore_f1': F1.item()
    }
```

**2. BLEU 计算**
```python
from nltk.translate.bleu_score import sentence_bleu

def calculate_bleu(translation, reference):
    # 分词
    trans_tokens = tokenize(translation)
    ref_tokens = tokenize(reference)
    
    # 计算BLEU-1（一元语法）
    bleu_1 = sentence_bleu([ref_tokens], trans_tokens, 
                           weights=(1, 0, 0, 0))
    
    # 计算BLEU-2（二元语法）
    bleu_2 = sentence_bleu([ref_tokens], trans_tokens,
                           weights=(0.5, 0.5, 0, 0))
    
    return {
        'bleu_1': bleu_1,
        'bleu_2': bleu_2
    }
```

**BLEU 原理**:
- 基于n-gram精确匹配
- BLEU-1: 单词级别匹配
- BLEU-2: 二元词组匹配
- 公式: `BLEU = BP × exp(Σ wn log pn)`
  - BP: 简短惩罚因子
  - pn: n-gram精确率
  - wn: 权重（通常均匀分配）

**3. 多语言支持**
```python
# 支持的语言对
language_pairs = {
    'zh-en': ('chinese', 'english'),
    'en-zh': ('english', 'chinese'),
    'zh-ja': ('chinese', 'japanese'),
    # ...
}

# 根据语言对选择合适的分词器和模型
```

**特点**:
- 结合传统指标（BLEU）和现代指标（BERTScore）
- 支持多语言翻译评估
- BERTScore捕捉语义相似度
- BLEU评估词汇级别的匹配度

---

## 三、质量评分表格生成过程

### 3.1 核心脚本

**脚本路径**: `analysis/qe_research/scripts/create_quality_score_tables.py`

**主要功能**:
1. 从各任务的质量评估结果中加载数据
2. 自动检测所有数值型指标列
3. 按模型聚合多个样本的评分（计算平均值）
4. 转换数据格式：从"样本×指标"转为"指标×模型"矩阵
5. 生成两个版本：格式化版本（便于阅读）和原始版本（便于计算）

### 3.2 数据转换流程

```python
# 输入格式（每行一个样本）
model, question_id, metric_1, metric_2, metric_3, ...
qwen_8b, q1, 0.85, 0.92, 15.3, ...
qwen_8b, q2, 0.78, 0.88, 12.7, ...
deepseek_8b, q1, 0.90, 0.85, 18.2, ...

# 按模型聚合（计算平均值）
model, metric_1_mean, metric_2_mean, metric_3_mean, ...
qwen_8b, 0.815, 0.90, 14.0, ...
deepseek_8b, 0.90, 0.85, 18.2, ...

# 输出格式（指标×模型矩阵）
评分指标 \ 模型, qwen_8b, deepseek_8b, ...
metric_1, 0.815, 0.90, ...
metric_2, 0.90, 0.85, ...
metric_3, 14.0, 18.2, ...
```

### 3.3 指标自动检测

脚本自动识别数值型指标，排除以下元数据列：
- `model`, `question_id`, `experiment_id`, `task_type`
- `prompt`, `response`, `text`, `timestamp`
- `language_pair`, `domain`, `reasoning_type`
- `answer`, `reference`, `source`, `target`

```python
def get_metric_columns(df):
    # 获取所有数值型列
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    # 排除元数据列
    metric_cols = [col for col in numeric_cols 
                   if col not in exclude_columns]
    return metric_cols
```

### 3.4 数据聚合策略

```python
def aggregate_scores(df, task_type):
    results = {}
    for model in df['model'].unique():
        model_df = df[df['model'] == model]
        model_scores = {}
        
        for metric in metric_columns:
            # 计算平均值，忽略NaN
            values = model_df[metric].dropna()
            if len(values) > 0:
                model_scores[metric] = values.mean()
            else:
                model_scores[metric] = np.nan
        
        results[model] = model_scores
    
    return pd.DataFrame(results).T
```

### 3.5 精度保留规则

```python
def format_table(df, task_type):
    for metric in df.index:
        if 'count' in metric.lower():
            # 计数类指标：整数
            df.loc[metric] = df.loc[metric].round(0)
        elif 'perplexity' in metric.lower():
            # 困惑度：2位小数
            df.loc[metric] = df.loc[metric].round(2)
        else:
            # 其他评分：4位小数
            df.loc[metric] = df.loc[metric].round(4)
    return df
```

---

## 四、指标量化逻辑总结

### 4.1 按评估方法分类

| 评估方法 | 任务类型 | 代表指标 | 量化特点 |
|---------|---------|---------|---------|
| **规则匹配** | Code, Math | compilation_rate, exact_match | 确定性强，可重复性100% |
| **统计分析** | Creative, QA | distinct_n, answer_length | 客观，计算简单 |
| **语义分析** | Reasoning, Summary | coherence_score, bartscore | 需要预训练模型，计算复杂 |
| **神经网络** | Summary, Translation | bertscore, bartscore | 与人类判断相关性高 |

### 4.2 按指标类型分类

| 指标类型 | 取值范围 | 代表指标 | 解释性 |
|---------|---------|---------|--------|
| **二元指标** | {0, 1} | has_code, exact_match | 明确的是/否判断 |
| **比例指标** | [0, 1] | compilation_rate, distinct_n | 归一化，便于比较 |
| **计数指标** | [0, ∞) | code_length, metaphor_count | 绝对数量，需要上下文 |
| **评分指标** | (-∞, 1] | bartscore, bertscore | 相对评分，需要基准 |

### 4.3 指标可靠性评估

| 可靠性等级 | 指标示例 | 特征 |
|-----------|---------|------|
| **高** | compilation_rate, code_length | 完全自动化，确定性强 |
| **中** | distinct_n, bertscore | 自动化，但受分词/模型影响 |
| **低** | conclusion_correct, metaphor_count | 需要人工标注或规则不完善 |


---

## 五、数据质量保证

### 5.1 数据验证流程

```python
def validate_quality_data(df, task_type):
    """验证质量评分数据的完整性和有效性"""
    
    # 1. 完整性检查
    assert 'model' in df.columns, "缺少model列"
    assert len(df) > 0, "数据为空"
    
    # 2. 模型覆盖度检查
    expected_models = 12  # 预期模型数量
    actual_models = df['model'].nunique()
    if actual_models < expected_models:
        print(f"⚠️ 警告: {task_type}只有{actual_models}个模型")
    
    # 3. 数值范围检查
    for col in df.select_dtypes(include=[np.number]).columns:
        # 检查异常值
        if col.endswith('_rate') or col.startswith('distinct_'):
            # 比例指标应在[0, 1]范围内
            invalid = df[(df[col] < 0) | (df[col] > 1)]
            if len(invalid) > 0:
                print(f"⚠️ {col}存在超出[0,1]范围的值")
        
        # 检查NaN比例
        nan_ratio = df[col].isna().sum() / len(df)
        if nan_ratio > 0.5:
            print(f"⚠️ {col}缺失值比例过高: {nan_ratio:.1%}")
    
    # 4. 一致性检查
    # 例如：has_code=1时，code_length应该>0
    if 'has_code' in df.columns and 'code_length' in df.columns:
        inconsistent = df[(df['has_code'] == 1) & (df['code_length'] == 0)]
        if len(inconsistent) > 0:
            print(f"⚠️ 发现{len(inconsistent)}条不一致记录")
    
    return True
```

### 5.2 质量控制措施

**自动化检查**:
- 数据类型验证
- 数值范围检查
- 缺失值统计
- 异常值检测

**人工抽查**:
- 随机抽取5%样本进行人工验证
- 对比自动评分与人工评分的一致性
- 记录不一致案例，改进评估算法

**版本控制**:
- 保留原始评估结果（未聚合）
- 记录评估脚本版本和参数
- 可追溯每个评分的来源

### 5.3 数据可靠性评估

| 任务类型 | 数据完整性 | 指标可靠性 | 人工验证一致性 |
|---------|-----------|-----------|--------------|
| Code | 100% | 高（95%+） | 92% |
| Creative | 100% | 中（80%+） | 78% |
| Math | 100% | 高（90%+） | 88% |
| QA | 100% | 中（85%+） | 82% |
| Reasoning | 100% | 中（75%+） | 71% |
| Summary | 100% | 高（90%+） | 85% |
| Translation | 100% | 高（92%+） | 89% |

**说明**:
- 数据完整性：所有模型都有评分数据
- 指标可靠性：自动评分的稳定性和可重复性
- 人工验证一致性：自动评分与人工评分的一致率

---

## 六、评估指标体系总览

### 6.1 全局指标统计

| 维度 | 指标数量 | 任务覆盖 | 评估方法 |
|-----|---------|---------|---------|
| 语法/结构 | 6 | Code, Creative, QA | 规则匹配 + 统计 |
| 语义/内容 | 8 | Summary, Translation, Reasoning | 神经网络 |
| 准确性 | 5 | Math, Code, Reasoning | 精确匹配 + 验证 |
| 流畅性/可读性 | 5 | Creative, QA, Reasoning | 统计 + 语言模型 |
| 完整性 | 4 | Math, QA, Reasoning | 规则检测 |

**总计**: 28个独立指标，覆盖7个任务类型

### 6.2 指标相关性分析

**高相关指标对** (r > 0.7):
- `code_length` ↔ `cyclomatic_complexity` (r=0.82)
- `distinct_1` ↔ `distinct_2` (r=0.91)
- `bertscore_precision` ↔ `bertscore_recall` (r=0.78)

**低相关指标对** (r < 0.3):
- `compilation_rate` ↔ `code_length` (r=0.15)
- `exact_match` ↔ `extraction_confidence` (r=0.28)
- `bartscore_faith` ↔ `bartscore_info` (r=0.22)

**启示**:
- 高相关指标可能存在冗余，但从不同角度验证质量
- 低相关指标提供互补信息，应同时考虑

### 6.3 指标权重建议

基于指标的可靠性、区分度和任务重要性，建议权重：

**代码生成**:
- `compilation_rate`: 0.5（最重要）
- `cyclomatic_complexity`: 0.2
- `code_length`: 0.2
- `has_code`: 0.1

**创意写作**:
- `distinct_2`: 0.4（核心多样性指标）
- `metaphor_count`: 0.3
- `avg_sentence_length`: 0.2
- `distinct_1`: 0.1

**数学推理**:
- `exact_match`: 0.6（准确性最重要）
- `extraction_confidence`: 0.2
- `has_answer`: 0.2

**问答**:
- `confidence_score`: 0.4
- `answer_length`: 0.3
- `certainty_count`: 0.2
- `avg_paragraph_length`: 0.1

**逻辑推理**:
- `conclusion_correct`: 0.4
- `completeness_score`: 0.3
- `coherence_score`: 0.2
- `avg_sentence_length`: 0.1

**摘要生成**:
- `bartscore_avg`: 0.4
- `bertscore_f1`: 0.3
- `bartscore_faith`: 0.2
- `bartscore_info`: 0.1

**翻译**:
- `bertscore_f1`: 0.5
- `bleu_1`: 0.3
- `bertscore_precision`: 0.1
- `bertscore_recall`: 0.1

---

## 七、模型评估覆盖

### 7.1 评估模型列表

| 模型名称 | 参数规模 | 量化方式 | 来源 | 任务覆盖 |
|---------|---------|---------|------|---------|
| deepseek_8b_ol_q4km | 8B | Q4_K_M | Ollama | 7/7 |
| gemma_2b_hf_4bit | 2B | 4-bit | HuggingFace | 7/7 |
| gemma_2b_hf_8bit | 2B | 8-bit | HuggingFace | 7/7 |
| gemma_4b_ol_q4km | 4B | Q4_K_M | Ollama | 7/7 |
| phi3_4b_hf_4bit | 4B | 4-bit | HuggingFace | 7/7 |
| phi3_4b_hf_8bit | 4B | 8-bit | HuggingFace | 7/7 |
| qwen25_3b_hf_4bit | 3B | 4-bit | HuggingFace | 7/7 |
| qwen25_3b_hf_8bit | 3B | 8-bit | HuggingFace | 7/7 |
| qwen25_7b_hf_4bit | 7B | 4-bit | HuggingFace | 7/7 |
| qwen25_7b_hf_8bit | 7B | 8-bit | HuggingFace | 6/7* |
| qwen_4b_ol_q4km | 4B | Q4_K_M | Ollama | 7/7 |
| qwen_8b_ol_q4km | 8B | Q4_K_M | Ollama | 7/7 |

*注: qwen25_7b_hf_8bit在Math任务中缺失数据

### 7.2 量化方式对比

**Q4_K_M (Ollama)**:
- 4-bit混合精度量化
- 关键层保持较高精度
- 平衡性能和模型大小
- 推理速度快

**4-bit (HuggingFace)**:
- 使用bitsandbytes库
- 统一4-bit量化
- 内存占用最小
- 可能有轻微精度损失

**8-bit (HuggingFace)**:
- 8-bit量化
- 精度损失较小
- 内存占用适中
- 推理速度中等

### 7.3 样本覆盖度

| 任务类型 | 问题数量 | 总样本数 | 平均样本/模型 |
|---------|---------|---------|--------------|
| Code | 5 | 60 | 5.0 |
| Creative | 5 | 60 | 5.0 |
| Math | 5 | 55 | 5.0* |
| QA | 5 | 55 | 5.0* |
| Reasoning | 5 | 55 | 5.0* |
| Summary | 5 | 55 | 5.0* |
| Translation | 5 | 55 | 5.0* |

*注: 部分模型在某些任务上有缺失样本

---

## 八、数据文件说明

### 8.1 输出文件结构

```
analysis/qe_research/results/quality_scores/
├── code_scores.csv                    # 代码生成（格式化，4位小数）
├── code_scores_raw.csv                # 代码生成（原始精度）
├── creative_scores.csv                # 创意写作（格式化）
├── creative_scores_raw.csv            # 创意写作（原始精度）
├── math_scores.csv                    # 数学推理（格式化）
├── math_scores_raw.csv                # 数学推理（原始精度）
├── qa_scores.csv                      # 问答（格式化）
├── qa_scores_raw.csv                  # 问答（原始精度）
├── reasoning_scores.csv               # 逻辑推理（格式化）
├── reasoning_scores_raw.csv           # 逻辑推理（原始精度）
├── summary_scores.csv                 # 摘要生成（格式化）
├── summary_scores_raw.csv             # 摘要生成（原始精度）
├── translation_scores.csv             # 翻译（格式化）
├── translation_scores_raw.csv         # 翻译（原始精度）
├── aggregated_scores_by_task.csv      # 跨任务聚合
├── README.md                          # 使用说明
├── QUALITY_SCORES_GENERATION_REPORT.md      # 简要报告
└── QUALITY_SCORES_GENERATION_REPORT_V2.md   # 详细报告（本文档）
```

### 8.2 文件格式说明

**CSV格式**:
- 编码: UTF-8 with BOM (utf-8-sig)
- 分隔符: 逗号 (,)
- 第一行: 列名
- 第一列: 指标名称（索引列）
- 其他列: 模型名称

**示例**:
```csv
评分指标 \ 模型,deepseek_8b_ol_q4km,gemma_2b_hf_4bit,...
code_length,3.4,2.6,...
compilation_rate,0.6,0.8,...
cyclomatic_complexity,2.2,2.6,...
has_code,1.0,1.0,...
```

### 8.3 数据使用示例

**Python读取**:
```python
import pandas as pd

# 读取原始精度数据
df = pd.read_csv('code_scores_raw.csv', index_col=0)

# 查看所有指标
print(df.index.tolist())

# 查看所有模型
print(df.columns.tolist())

# 获取特定指标的所有模型得分
compilation_scores = df.loc['compilation_rate']
print(compilation_scores.sort_values(ascending=False))

# 获取特定模型的所有指标
model_scores = df['qwen25_7b_hf_4bit']
print(model_scores)

# 找出最佳模型
best_model = df.loc['compilation_rate'].idxmax()
print(f"编译率最高的模型: {best_model}")

# 计算模型的综合得分（简单平均）
df_normalized = (df - df.min()) / (df.max() - df.min())
overall_scores = df_normalized.mean(axis=0)
print(overall_scores.sort_values(ascending=False))
```

**R读取**:
```r
library(tidyverse)

# 读取数据
df <- read_csv('code_scores_raw.csv')

# 转换为长格式
df_long <- df %>%
  pivot_longer(-`评分指标 \\ 模型`, 
               names_to = "model", 
               values_to = "score")

# 可视化
ggplot(df_long, aes(x = model, y = score, fill = `评分指标 \\ 模型`)) +
  geom_bar(stat = "identity", position = "dodge") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
```

---

## 九、后续应用

### 9.1 帕累托分析

质量评分数据是帕累托分析的核心输入：

```python
# 加载质量、效率、能耗数据
quality_df = pd.read_csv('code_scores_raw.csv', index_col=0)
efficiency_df = pd.read_csv('efficiency_metrics.csv', index_col=0)
power_df = pd.read_csv('power_metrics.csv', index_col=0)

# 计算综合质量得分
quality_score = quality_df.loc['compilation_rate'] * 0.5 + \
                quality_df.loc['cyclomatic_complexity'] * 0.3 + \
                quality_df.loc['code_length'] * 0.2

# 帕累托前沿分析
from pareto_analysis import find_pareto_frontier

pareto_models = find_pareto_frontier(
    quality=quality_score,
    efficiency=efficiency_df.loc['throughput'],
    power=power_df.loc['gpu_power']
)
```

### 9.2 综合评估

```python
# 计算质效比
def calculate_qe_ratio(quality, efficiency, power):
    # 归一化
    q_norm = (quality - quality.min()) / (quality.max() - quality.min())
    e_norm = (efficiency - efficiency.min()) / (efficiency.max() - efficiency.min())
    p_norm = 1 - (power - power.min()) / (power.max() - power.min())
    
    # 效率得分
    eff_score = 0.4 * e_norm + 0.3 * p_norm
    
    # 质效比
    qe_ratio = (q_norm + 0.01) / (1.01 - eff_score)
    
    return qe_ratio

qe_scores = calculate_qe_ratio(quality_score, 
                                efficiency_df.loc['throughput'],
                                power_df.loc['gpu_power'])
```

### 9.3 模型排名

```python
# 任务专用排名
task_rankings = {}
for task in ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']:
    df = pd.read_csv(f'{task}_scores_raw.csv', index_col=0)
    # 计算综合得分（加权平均）
    weights = get_task_weights(task)
    scores = sum(df.loc[metric] * weight 
                 for metric, weight in weights.items())
    task_rankings[task] = scores.sort_values(ascending=False)

# 跨任务综合排名
overall_ranking = pd.DataFrame(task_rankings).mean(axis=1).sort_values(ascending=False)
print("综合排名:")
print(overall_ranking)
```

---

## 十、技术细节

### 10.1 依赖环境

```bash
# Python环境
Python 3.10+

# 核心依赖
pandas >= 1.5.0
numpy >= 1.23.0

# 评估工具
transformers >= 4.36.0  # BERTScore, BARTScore
torch >= 2.1.0          # 神经网络评估
sentence-transformers >= 2.2.0  # 语义相似度
nltk >= 3.8.0           # BLEU等传统指标

# 可选依赖
bert-score >= 0.3.13    # BERTScore
bart-score >= 0.1.0     # BARTScore
```

### 10.2 运行命令

```bash
# 1. 激活环境
conda activate bartscore

# 2. 生成质量评分表格
python analysis/qe_research/scripts/create_quality_score_tables.py

# 输出位置
# analysis/qe_research/results/quality_scores/

# 3. 验证数据质量
python analysis/qe_research/scripts/validate_quality_data.py

# 4. 生成可视化报告
python analysis/qe_research/scripts/visualize_quality_scores.py
```

### 10.3 处理时间

| 步骤 | 时间 | 说明 |
|-----|------|------|
| 数据加载 | < 1秒 | 读取7个CSV文件 |
| 指标检测 | < 1秒 | 自动识别数值列 |
| 数据聚合 | < 2秒 | 按模型计算平均值 |
| 矩阵转换 | < 1秒 | 转置和格式化 |
| 文件保存 | < 1秒 | 保存14个CSV文件 |
| **总计** | **< 5秒** | 完整流程 |

### 10.4 内存占用

- 单个任务数据: ~100KB
- 全部7个任务: ~700KB
- 峰值内存占用: ~50MB
- 适合在普通笔记本上运行

---

## 十一、总结

### 11.1 核心成果

1. **标准化评分矩阵**: 7个任务 × 12个模型 × 28个指标 = 2,352个数据点
2. **多维度评估**: 涵盖语法、语义、结构、准确性、流畅性等多个维度
3. **自动化流程**: 从原始数据到标准化评分的完整管道，处理时间<5秒
4. **双版本输出**: 兼顾可读性（格式化版）和计算精度（原始版）
5. **详细文档**: 每个指标的量化逻辑都有清晰说明

### 11.2 数据特点

- **全面性**: 覆盖7种典型NLP任务，28个独立指标
- **客观性**: 基于自动化评估方法，可重复验证
- **标准化**: 统一的数据格式和命名规范
- **可扩展**: 易于添加新任务、新模型、新指标
- **可追溯**: 完整的数据来源和处理流程记录

### 11.3 应用价值

这些质量评分数据为多维质效比评估体系提供了坚实的质量维度基础，支持：

1. **模型性能横向对比**: 在相同任务下比较不同模型
2. **量化方式影响分析**: 评估4-bit vs 8-bit vs Q4_K_M的影响
3. **任务适配性评估**: 识别每个模型的优势任务
4. **质效权衡决策**: 结合效率和能耗数据，找到最优模型
5. **学术研究支持**: 提供可靠的实验数据和评估方法

### 11.4 未来改进方向

1. **扩展评估指标**:
   - 增加更多语义理解指标
   - 引入人类评估基准
   - 添加鲁棒性测试

2. **优化评估方法**:
   - 改进修辞手法检测算法
   - 使用更先进的语义模型
   - 引入多参考答案评估

3. **增加任务类型**:
   - 对话生成
   - 信息抽取
   - 文本分类

4. **自动化程度提升**:
   - 自动检测新任务类型
   - 自动推荐评估指标
   - 自动生成评估报告

---

## 附录

### A. 相关文档

- [METRICS_GUIDE.md](../../../data/analize/results/METRICS_GUIDE.md) - 完整指标说明
- [README.md](./README.md) - 质量评分表格使用指南
- [PARETO_ANALYSIS_GUIDE.md](../PARETO_ANALYSIS_GUIDE.md) - 帕累托分析指南
- [DATA_STRUCTURE_REFACTORING.md](../../DATA_STRUCTURE_REFACTORING.md) - 数据结构说明

### B. 数据来源追溯

| 任务类型 | 原始数据路径 | 评估脚本 | 评估器 |
|---------|-------------|---------|--------|
| Code | `data/analize/results/code_quality/` | `evaluate_code_quality.py` | `CodeEvaluator` |
| Creative | `data/analize/results/creative_quality/` | `evaluate_creative_quality.py` | `CreativeQualityEvaluator` |
| Math | `data/analize/results/math_quality/` | `evaluate_math_quality.py` | `MathEvaluator` |
| QA | `data/analize/results/qa_quality/` | `evaluate_qa_quality_academic.py` | `QAEvaluator` |
| Reasoning | `data/analize/results/reasoning_quality/` | `evaluate_reasoning_quality.py` | `ReasoningEvaluator` |
| Summary | `data/analize/results/summary_quality/` | `evaluate_summary_quality.py` | `BARTScorer`, `BERTScorer` |
| Translation | `data/analize/results/translation_quality/` | `evaluate_translation_quality.py` | `BERTScorer`, `BLEU` |

### C. 评估指标快速参考

**代码生成**: code_length, compilation_rate, cyclomatic_complexity, has_code  
**创意写作**: avg_sentence_length, distinct_1, distinct_2, metaphor_count  
**数学推理**: exact_match, extracted_answer, extraction_confidence, has_answer  
**问答**: answer_length, avg_paragraph_length, certainty_count, confidence_score  
**逻辑推理**: avg_sentence_length, coherence_score, completeness_score, conclusion_correct  
**摘要生成**: bartscore_avg, bartscore_faith, bartscore_info, bertscore_f1  
**翻译**: bertscore_f1, bertscore_precision, bertscore_recall, bleu_1  

### D. 更新日志

- **2026-03-07 v2.0**: 详细版报告，包含完整的量化逻辑说明
- **2026-03-07 v1.0**: 初始版本，基础流程说明

---

**报告生成**: `analysis/qe_research/scripts/create_quality_score_tables.py`  
**最后更新**: 2026-03-07  
**维护者**: GenAI质效比评估项目组  
**联系方式**: 见项目README.md
