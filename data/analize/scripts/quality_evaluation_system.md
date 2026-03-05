# 大语言模型质量评估体系设计

## 1. 评估体系概述

### 1.1 设计目标

建立一套全面、客观、可复现的质量评估体系，针对不同任务类型采用多维度评估指标，形成"拼盘式"质量评分系统，为模型质效比分析提供可靠的质量基准。

### 1.2 核心原则

1. **任务自适应**：不同任务类型采用不同的评估指标组合
2. **多指标融合**：单一指标不足以全面评估质量，需要多维度综合
3. **可解释性**：每个指标都有明确的含义和计算方法
4. **可复现性**：评估过程标准化，结果可验证
5. **效率平衡**：在评估精度和计算成本间取得平衡

### 1.3 任务类型与评估策略

| 任务类型 | 主要评估维度 | 核心指标 | 辅助指标 |
| -------- | ------------ | -------- | -------- |
| **code** | 正确性、可执行性 | Pass@k、编译率 | 代码质量、效率 |
| **creative** | 多样性、流畅性 | Distinct-N、困惑度 | 长度、连贯性 |
| **math** | 准确性、推理 | Exact Match、数值精度 | 步骤完整性 |
| **qa** | 准确性、相关性 | Exact Match、F1、BERTScore | ROUGE、BLEU |
| **summary** | 信息保留、简洁性 | ROUGE-L、BERTScore | 压缩比、BARTScore |
| **reasoning** | 逻辑性、完整性 | 推理步骤完整性、结论正确性 | 逻辑连贯性、论证深度 |
| **translation** | 准确性、流畅性 | BLEU、BERTScore | 术语一致性、文化适应性 |

## 2. 任务特定评估指标

### 2.1 代码生成任务 (code)

**评估目标**：代码的正确性、可执行性和质量

**核心指标**：

1. **Pass@k (k=1,3,5)**
   - 定义：生成 k 个候选代码，至少有 1 个通过所有测试用例的概率
   - 计算：`Pass@k = 1 - C(n-c, k) / C(n, k)`
   - 范围：[0, 1]，越高越好
   - 实现：需要测试用例和代码执行环境

2. **编译成功率 (Compilation Rate)**
   - 定义：生成代码能够成功编译的比例
   - 计算：`编译成功数 / 总生成数`
   - 范围：[0, 1]
   - 实现：Python 使用 `compile()` 或 `ast.parse()`

**辅助指标**：

3. **代码质量得分**
   - 代码长度（行数）
   - 复杂度（圈复杂度）
   - 风格一致性（PEP8 for Python）

**实现方案**：
```python
def evaluate_code_quality(generated_code, test_cases=None):
    scores = {}
    
    # 1. 编译检查
    try:
        compile(generated_code, '<string>', 'exec')
        scores['compiles'] = 1.0
    except:
        scores['compiles'] = 0.0
        return scores  # 无法编译则跳过后续测试
    
    # 2. 测试用例通过率（如果有）
    if test_cases:
        passed = run_test_cases(generated_code, test_cases)
        scores['pass_rate'] = passed / len(test_cases)
    
    # 3. 代码长度
    scores['code_length'] = len(generated_code.split('\n'))
    
    return scores
```


### 2.2 创意写作任务 (creative)

**评估目标**：文本的多样性、流畅性和创造力

**核心指标**：

1. **Distinct-N (N=1,2,3)**
   - 定义：N-gram 去重率，衡量词汇多样性
   - 计算：`Distinct-N = unique_ngrams / total_ngrams`
   - 范围：[0, 1]，越高表示越多样
   - 推荐：Distinct-2 作为主指标

2. **Self-BLEU (多次生成时)**
   - 定义：同一提示多次生成结果间的 BLEU 分数
   - 计算：计算所有生成对之间的平均 BLEU
   - 范围：[0, 1]，越低表示越多样
   - 用途：评估生成的多样性

**辅助指标**：

3. **困惑度 (Perplexity)**
   - 定义：语言模型对文本的困惑程度
   - 计算：使用预训练语言模型计算
   - 范围：越低表示越流畅
   - 实现：使用 GPT-2 或类似模型

4. **文本长度**
   - 字符数、词数
   - 评估是否符合要求长度

**实现方案**：
```python
def evaluate_creative_quality(generated_texts):
    scores = {}
    
    # 1. Distinct-2
    all_bigrams = []
    for text in generated_texts:
        tokens = text.split()
        bigrams = [' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)]
        all_bigrams.extend(bigrams)
    
    scores['distinct_2'] = len(set(all_bigrams)) / len(all_bigrams) if all_bigrams else 0
    
    # 2. Self-BLEU (如果有多次生成)
    if len(generated_texts) > 1:
        from nltk.translate.bleu_score import sentence_bleu
        bleu_scores = []
        for i, text in enumerate(generated_texts):
            others = [t.split() for j, t in enumerate(generated_texts) if j != i]
            score = sentence_bleu(others, text.split())
            bleu_scores.append(score)
        scores['self_bleu'] = sum(bleu_scores) / len(bleu_scores)
    
    # 3. 平均长度
    scores['avg_length'] = sum(len(t) for t in generated_texts) / len(generated_texts)
    
    return scores
```

### 2.3 数学推理任务 (math)

**评估目标**：答案的准确性和推理过程的完整性

**核心指标**：

1. **Exact Match (EM)**
   - 定义：生成答案与标准答案完全匹配的比例
   - 计算：`EM = (预测 == 标准答案) ? 1 : 0`
   - 范围：{0, 1}
   - 注意：需要答案归一化（去除空格、统一格式）

2. **数值精度匹配**
   - 定义：对于数值答案，允许一定误差范围
   - 计算：`|预测 - 标准| < ε`（ε = 0.01 或相对误差 1%）
   - 范围：{0, 1}

**辅助指标**：

3. **推理步骤完整性**
   - 是否包含计算过程
   - 步骤数量
   - 逻辑连贯性（规则匹配）

**实现方案**：
```python
def evaluate_math_quality(generated_answer, reference_answer):
    scores = {}
    
    # 1. 提取数值答案
    pred_num = extract_number(generated_answer)
    ref_num = extract_number(reference_answer)
    
    # 2. Exact Match (字符串)
    pred_clean = normalize_answer(generated_answer)
    ref_clean = normalize_answer(reference_answer)
    scores['exact_match'] = 1.0 if pred_clean == ref_clean else 0.0
    
    # 3. 数值精度匹配
    if pred_num is not None and ref_num is not None:
        relative_error = abs(pred_num - ref_num) / (abs(ref_num) + 1e-10)
        scores['numerical_match'] = 1.0 if relative_error < 0.01 else 0.0
    
    # 4. 推理步骤检测
    scores['has_reasoning'] = 1.0 if contains_calculation_steps(generated_answer) else 0.0
    
    return scores

def extract_number(text):
    """从文本中提取数值"""
    import re
    numbers = re.findall(r'-?\d+\.?\d*', text)
    return float(numbers[-1]) if numbers else None

def normalize_answer(text):
    """答案归一化"""
    return text.strip().lower().replace(' ', '')
```


### 2.4 问答任务 (qa)

**评估目标**：答案的准确性、完整性和相关性

**核心指标**：

1. **Exact Match (EM)**
   - 定义：与标准答案完全匹配
   - 计算：归一化后字符串比较
   - 范围：{0, 1}

2. **F1 Score**
   - 定义：预测答案与标准答案的词级别重叠
   - 计算：`F1 = 2 * (precision * recall) / (precision + recall)`
   - 范围：[0, 1]
   - 优势：对部分匹配友好

3. **BERTScore**
   - 定义：基于 BERT 的语义相似度
   - 计算：使用预训练 BERT 计算 token 级别相似度
   - 范围：[0, 1]
   - 优势：捕捉语义等价

**辅助指标**：

4. **ROUGE-L**
   - 最长公共子序列
   - 适用于较长答案

5. **BLEU**
   - N-gram 重叠
   - 适用于多参考答案

**实现方案**：
```python
def evaluate_qa_quality(generated_answer, reference_answer):
    scores = {}
    
    # 1. Exact Match
    pred_norm = normalize_answer(generated_answer)
    ref_norm = normalize_answer(reference_answer)
    scores['exact_match'] = 1.0 if pred_norm == ref_norm else 0.0
    
    # 2. F1 Score
    pred_tokens = pred_norm.split()
    ref_tokens = ref_norm.split()
    common = set(pred_tokens) & set(ref_tokens)
    
    if len(pred_tokens) == 0 or len(ref_tokens) == 0:
        scores['f1'] = 0.0
    else:
        precision = len(common) / len(pred_tokens)
        recall = len(common) / len(ref_tokens)
        scores['f1'] = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # 3. BERTScore (需要安装 bert-score)
    try:
        from bert_score import score
        P, R, F1 = score([generated_answer], [reference_answer], lang='zh', verbose=False)
        scores['bertscore_f1'] = F1.item()
    except:
        scores['bertscore_f1'] = None
    
    return scores
```

### 2.5 文本摘要任务 (summary)

**评估目标**：信息保留、简洁性和流畅性

**核心指标**：

1. **ROUGE-L**
   - 定义：最长公共子序列 F1 分数
   - 计算：基于 LCS 的 precision 和 recall
   - 范围：[0, 1]
   - 优势：考虑句子级别的结构

2. **BERTScore**
   - 定义：语义相似度
   - 计算：BERT embedding 的余弦相似度
   - 范围：[0, 1]
   - 优势：捕捉语义等价

3. **BARTScore**
   - 定义：基于 BART 的生成概率
   - 计算：`P(summary|source)` 和 `P(source|summary)`
   - 范围：(-∞, 0]，越高越好
   - 优势：双向评估，更全面

**辅助指标**：

4. **压缩比**
   - `压缩比 = 摘要长度 / 原文长度`
   - 评估简洁性

5. **ROUGE-1, ROUGE-2**
   - Unigram 和 Bigram 重叠
   - 补充 ROUGE-L

**实现方案**：
```python
def evaluate_summary_quality(generated_summary, reference_summary, source_text=None):
    scores = {}
    
    # 1. ROUGE 分数
    try:
        from rouge import Rouge
        rouge = Rouge()
        rouge_scores = rouge.get_scores(generated_summary, reference_summary)[0]
        scores['rouge_1_f'] = rouge_scores['rouge-1']['f']
        scores['rouge_2_f'] = rouge_scores['rouge-2']['f']
        scores['rouge_l_f'] = rouge_scores['rouge-l']['f']
    except:
        scores['rouge_l_f'] = None
    
    # 2. BERTScore
    try:
        from bert_score import score
        P, R, F1 = score([generated_summary], [reference_summary], lang='zh', verbose=False)
        scores['bertscore_f1'] = F1.item()
    except:
        scores['bertscore_f1'] = None
    
    # 3. BARTScore (如果已安装)
    if source_text:
        try:
            from bart_score import BARTScorer
            bart_scorer = BARTScorer(device='cuda', checkpoint='facebook/bart-large-cnn')
            # 信息性：summary -> source
            scores['bartscore_info'] = bart_scorer.score([source_text], [generated_summary])[0]
            # 忠实性：source -> summary
            scores['bartscore_faith'] = bart_scorer.score([generated_summary], [source_text])[0]
        except:
            scores['bartscore_info'] = None
    
    # 4. 压缩比
    if source_text:
        scores['compression_ratio'] = len(generated_summary) / len(source_text)
    
    return scores
```

### 2.6 逻辑推理任务 (reasoning)

**评估目标**：推理过程的逻辑性、完整性和结论的正确性

**核心指标**：

1. **推理步骤完整性 (Reasoning Completeness)**
   - 定义：是否包含完整的推理链条（前提→推理→结论）
   - 计算：检测关键推理标记词（"因为"、"所以"、"因此"、"由于"等）
   - 范围：[0, 1]
   - 实现：基于规则的模式匹配

2. **结论正确性 (Conclusion Correctness)**
   - 定义：最终结论是否与标准答案一致
   - 计算：提取结论部分，与参考答案比较（Exact Match 或语义相似度）
   - 范围：{0, 1} 或 [0, 1]
   - 实现：结合关键词提取和语义匹配

3. **逻辑连贯性 (Logical Coherence)**
   - 定义：推理步骤之间的逻辑关系是否合理
   - 计算：检测逻辑矛盾、循环论证等问题
   - 范围：[0, 1]
   - 实现：基于规则或小型逻辑检查器

**辅助指标**：

4. **推理步骤数量**
   - 统计推理步骤的数量
   - 评估论证的详细程度

5. **前提使用率**
   - 检查是否使用了所有给定前提
   - 评估推理的全面性

6. **文本长度**
   - 字符数、句子数
   - 评估回答的详细程度

**实现方案**：
```python
def evaluate_reasoning_quality(generated_answer, reference_answer=None, premises=None):
    scores = {}
    
    # 1. 推理步骤完整性
    reasoning_markers = ['因为', '所以', '因此', '由于', '根据', '可以得出', '推断', '结论']
    marker_count = sum(1 for marker in reasoning_markers if marker in generated_answer)
    scores['has_reasoning_steps'] = 1.0 if marker_count >= 2 else 0.0
    scores['reasoning_step_count'] = marker_count
    
    # 2. 结论正确性（如果有参考答案）
    if reference_answer:
        # 提取结论部分（通常在最后）
        conclusion_markers = ['因此', '所以', '综上', '总之', '答案是']
        conclusion = generated_answer
        for marker in conclusion_markers:
            if marker in generated_answer:
                conclusion = generated_answer.split(marker)[-1].strip()
                break
        
        # 与参考答案比较
        conclusion_norm = normalize_answer(conclusion)
        ref_norm = normalize_answer(reference_answer)
        scores['conclusion_correct'] = 1.0 if conclusion_norm == ref_norm else 0.0
        
        # 语义相似度（可选）
        try:
            from bert_score import score
            P, R, F1 = score([conclusion], [reference_answer], lang='zh', verbose=False)
            scores['conclusion_semantic_sim'] = F1.item()
        except:
            scores['conclusion_semantic_sim'] = None
    
    # 3. 逻辑连贯性（简化版：检测矛盾词）
    contradiction_markers = ['但是', '然而', '相反', '矛盾']
    has_contradiction = any(marker in generated_answer for marker in contradiction_markers)
    scores['logical_coherence'] = 0.5 if has_contradiction else 1.0
    
    # 4. 前提使用率（如果提供了前提）
    if premises:
        premises_used = sum(1 for premise in premises if premise in generated_answer)
        scores['premise_usage_rate'] = premises_used / len(premises) if premises else 0.0
    
    # 5. 文本长度
    scores['answer_length'] = len(generated_answer)
    scores['sentence_count'] = generated_answer.count('。') + generated_answer.count('？')
    
    return scores

def normalize_answer(text):
    """答案归一化"""
    import re
    # 去除标点和空格
    text = re.sub(r'[^\w]', '', text)
    return text.strip().lower()
```

**评估示例**：

```python
# 示例1：三段论推理
generated = """
根据题目：
1. 所有的猫都是哺乳动物
2. 所有的哺乳动物都需要呼吸
3. 小花是一只猫

推理过程：
因为小花是一只猫（前提3），
而所有的猫都是哺乳动物（前提1），
所以小花是哺乳动物。
又因为所有的哺乳动物都需要呼吸（前提2），
因此小花需要呼吸。

结论：小花需要呼吸。
"""

reference = "小花需要呼吸"
premises = ["所有的猫都是哺乳动物", "所有的哺乳动物都需要呼吸", "小花是一只猫"]

scores = evaluate_reasoning_quality(generated, reference, premises)
# 预期结果：
# {
#     'has_reasoning_steps': 1.0,
#     'reasoning_step_count': 5,
#     'conclusion_correct': 1.0,
#     'logical_coherence': 1.0,
#     'premise_usage_rate': 1.0,
#     'answer_length': 150,
#     'sentence_count': 8
# }
```

### 2.7 翻译任务 (translation)

**评估目标**：翻译的准确性、流畅性和文化适应性

**核心指标**：

1. **BLEU (Bilingual Evaluation Understudy)**
   - 定义：N-gram 精确度的几何平均
   - 计算：比较生成翻译与参考翻译的 N-gram 重叠
   - 范围：[0, 1]
   - 优势：广泛使用的机器翻译标准指标

2. **BERTScore**
   - 定义：基于 BERT 的语义相似度
   - 计算：使用多语言 BERT 模型计算 token 级别相似度
   - 范围：[0, 1]
   - 优势：捕捉语义等价，对同义词友好

3. **chrF (Character n-gram F-score)**
   - 定义：字符级别的 F1 分数
   - 计算：基于字符 N-gram 的 precision 和 recall
   - 范围：[0, 1]
   - 优势：对形态丰富的语言更友好

**辅助指标**：

4. **METEOR**
   - 考虑同义词和词干匹配
   - 更接近人类判断

5. **TER (Translation Edit Rate)**
   - 计算编辑距离
   - 越低越好

6. **长度比 (Length Ratio)**
   - `长度比 = 生成翻译长度 / 参考翻译长度`
   - 评估翻译的简洁性

**实现方案**：
```python
def evaluate_translation_quality(generated_translation, reference_translation, 
                                 source_text=None, source_lang='en', target_lang='zh'):
    scores = {}
    
    # 1. BLEU 分数
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
        
        # 分词（根据语言）
        if target_lang == 'zh':
            # 中文按字符分词
            reference_tokens = [list(reference_translation)]
            generated_tokens = list(generated_translation)
        else:
            # 英文按空格分词
            reference_tokens = [reference_translation.split()]
            generated_tokens = generated_translation.split()
        
        # 计算 BLEU-4
        smoothing = SmoothingFunction().method1
        scores['bleu_4'] = sentence_bleu(reference_tokens, generated_tokens, 
                                         smoothing_function=smoothing)
        
        # 计算 BLEU-1, BLEU-2
        scores['bleu_1'] = sentence_bleu(reference_tokens, generated_tokens, 
                                         weights=(1, 0, 0, 0), smoothing_function=smoothing)
        scores['bleu_2'] = sentence_bleu(reference_tokens, generated_tokens, 
                                         weights=(0.5, 0.5, 0, 0), smoothing_function=smoothing)
    except Exception as e:
        print(f"BLEU calculation failed: {e}")
        scores['bleu_4'] = None
    
    # 2. BERTScore（使用多语言模型）
    try:
        from bert_score import score
        
        # 根据目标语言选择模型
        model_type = 'bert-base-multilingual-cased'
        P, R, F1 = score([generated_translation], [reference_translation], 
                        model_type=model_type, verbose=False)
        scores['bertscore_precision'] = P.item()
        scores['bertscore_recall'] = R.item()
        scores['bertscore_f1'] = F1.item()
    except Exception as e:
        print(f"BERTScore calculation failed: {e}")
        scores['bertscore_f1'] = None
    
    # 3. chrF 分数
    try:
        from nltk.translate.chrf_score import sentence_chrf
        scores['chrf'] = sentence_chrf(reference_translation, generated_translation)
    except Exception as e:
        # 手动实现简化版 chrF
        def char_ngrams(text, n=6):
            return [text[i:i+n] for i in range(len(text)-n+1)]
        
        ref_ngrams = set(char_ngrams(reference_translation))
        gen_ngrams = set(char_ngrams(generated_translation))
        
        if len(gen_ngrams) == 0:
            scores['chrf'] = 0.0
        else:
            precision = len(ref_ngrams & gen_ngrams) / len(gen_ngrams)
            recall = len(ref_ngrams & gen_ngrams) / len(ref_ngrams) if len(ref_ngrams) > 0 else 0
            scores['chrf'] = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # 4. 长度比
    scores['length_ratio'] = len(generated_translation) / len(reference_translation) if len(reference_translation) > 0 else 0.0
    
    # 5. 编辑距离（归一化）
    try:
        from Levenshtein import distance
        edit_dist = distance(generated_translation, reference_translation)
        max_len = max(len(generated_translation), len(reference_translation))
        scores['normalized_edit_distance'] = 1 - (edit_dist / max_len) if max_len > 0 else 0.0
    except:
        scores['normalized_edit_distance'] = None
    
    return scores

def normalize_translation(text, lang='zh'):
    """翻译文本归一化"""
    import re
    
    # 去除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 统一标点符号（中英文）
    if lang == 'zh':
        text = text.replace(',', '，').replace('.', '。')
        text = text.replace('!', '！').replace('?', '？')
    
    return text
```

**评估示例**：

```python
# 示例1：英译中
source = "Artificial intelligence is transforming the way we live and work."
generated = "人工智能正在改变我们的生活和工作方式。"
reference = "人工智能正在重塑我们的生活方式和工作模式。"

scores = evaluate_translation_quality(generated, reference, source, 
                                     source_lang='en', target_lang='zh')
# 预期结果：
# {
#     'bleu_4': 0.45,
#     'bleu_1': 0.75,
#     'bertscore_f1': 0.92,
#     'chrf': 0.68,
#     'length_ratio': 0.95,
#     'normalized_edit_distance': 0.85
# }

# 示例2：中译英
source = "深度学习在计算机视觉领域取得了突破性进展。"
generated = "Deep learning has made breakthrough progress in the field of computer vision."
reference = "Deep learning has achieved breakthrough advancements in computer vision."

scores = evaluate_translation_quality(generated, reference, source,
                                     source_lang='zh', target_lang='en')
```


## 3. 多维质量评分系统（任务-模型适配性导向）

### 3.1 设计理念转变

**从主观加权 → 客观多维度呈现**

不再强制将多个指标合并为单一分数，而是：
1. **保留所有原始指标**：让数据说话，避免主观权重
2. **任务维度分析**：识别每个模型在各任务上的优势指标
3. **应用场景匹配**：根据实际需求选择最适合的模型
4. **帕累托分析**：在多指标空间中识别最优模型集合

### 3.2 多维度质量表征

**代码生成 (code)**：
```python
quality_metrics = {
    'correctness': {
        'pass_at_1': float,      # 正确性（核心）
        'compilation_rate': float # 可执行性（基础）
    },
    'quality': {
        'code_length': int,       # 简洁性
        'complexity': float       # 复杂度（可选）
    }
}
```

**创意写作 (creative)**：
```python
quality_metrics = {
    'diversity': {
        'distinct_1': float,      # 词汇多样性
        'distinct_2': float,      # 短语多样性
        'self_bleu': float        # 生成多样性（越低越好）
    },
    'fluency': {
        'perplexity': float,      # 流畅度（越低越好）
        'avg_length': int         # 生成长度
    }
}
```

**数学推理 (math)**：
```python
quality_metrics = {
    'accuracy': {
        'exact_match': float,     # 完全匹配（严格）
        'numerical_match': float  # 数值精度（宽松）
    },
    'reasoning': {
        'has_steps': bool,        # 是否有推理过程
        'step_count': int         # 推理步骤数
    }
}
```

**问答 (qa)**：
```python
quality_metrics = {
    'accuracy': {
        'exact_match': float,     # 精确匹配
        'f1_score': float         # 部分匹配
    },
    'semantic': {
        'bertscore_f1': float,    # 语义相似度
        'rouge_l': float          # 结构相似度
    }
}
```

**文本摘要 (summary)**：
```python
quality_metrics = {
    'content': {
        'rouge_1': float,         # 内容覆盖
        'rouge_2': float,         # 短语覆盖
        'rouge_l': float          # 结构保留
    },
    'semantic': {
        'bertscore_f1': float,    # 语义保留
        'bartscore_info': float,  # 信息性
        'bartscore_faith': float  # 忠实性
    },
    'conciseness': {
        'compression_ratio': float # 压缩比
    }
}
```

**逻辑推理 (reasoning)**：
```python
quality_metrics = {
    'reasoning': {
        'has_reasoning_steps': bool,      # 是否有推理步骤
        'reasoning_step_count': int,      # 推理步骤数量
        'logical_coherence': float        # 逻辑连贯性
    },
    'correctness': {
        'conclusion_correct': float,      # 结论正确性
        'conclusion_semantic_sim': float, # 结论语义相似度
        'premise_usage_rate': float       # 前提使用率
    },
    'completeness': {
        'answer_length': int,             # 回答长度
        'sentence_count': int             # 句子数量
    }
}
```

**翻译 (translation)**：
```python
quality_metrics = {
    'accuracy': {
        'bleu_1': float,                  # 单词级准确度
        'bleu_2': float,                  # 短语级准确度
        'bleu_4': float,                  # 句子级准确度
        'chrf': float                     # 字符级F分数
    },
    'semantic': {
        'bertscore_precision': float,     # 语义精确度
        'bertscore_recall': float,        # 语义召回率
        'bertscore_f1': float             # 语义F1分数
    },
    'fluency': {
        'length_ratio': float,            # 长度比
        'normalized_edit_distance': float # 归一化编辑距离
    }
}
```

### 3.3 应用场景导向的模型选择

**场景一：代码生成助手**
- **核心需求**：代码正确性 > 简洁性
- **关键指标**：`pass_at_1`, `compilation_rate`
- **选择策略**：优先选择 `pass_at_1` 最高的模型

**场景二：创意写作辅助**
- **核心需求**：多样性 > 流畅性
- **关键指标**：`distinct_2`, `self_bleu`
- **选择策略**：选择 `distinct_2` 高且 `self_bleu` 低的模型

**场景三：数学题解答**
- **核心需求**：准确性 > 推理过程
- **关键指标**：`exact_match`, `numerical_match`
- **选择策略**：优先选择 `exact_match` 最高的模型

**场景四：智能问答系统**
- **核心需求**：准确性 + 语义理解
- **关键指标**：`exact_match`, `f1_score`, `bertscore_f1`
- **选择策略**：在 `exact_match` 和 `bertscore_f1` 上均衡的模型

**场景五：文档摘要工具**
- **核心需求**：信息保留 + 简洁性
- **关键指标**：`rouge_l`, `bertscore_f1`, `compression_ratio`
- **选择策略**：ROUGE 和 BERTScore 高，压缩比适中（0.2-0.4）

**场景六：综合应用（多任务）**
- **核心需求**：各任务均衡表现
- **关键指标**：所有任务的核心指标
- **选择策略**：帕累托前沿分析，选择无明显短板的模型

**场景七：逻辑推理助手**
- **核心需求**：推理完整性 + 结论正确性
- **关键指标**：`has_reasoning_steps`, `conclusion_correct`, `logical_coherence`
- **选择策略**：优先选择推理步骤完整且结论正确的模型

**场景八：机器翻译系统**
- **核心需求**：准确性 + 流畅性
- **关键指标**：`bleu_4`, `bertscore_f1`, `chrf`
- **选择策略**：在 BLEU 和 BERTScore 上均衡，同时保持合理的长度比

### 3.4 客观综合评分方法（可选）

如果确实需要单一综合分数，采用以下客观方法：

#### 方法一：主成分分析（PCA）

**原理**：通过数据驱动的方式自动发现指标间的主要变化方向

```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def pca_quality_score(metrics_df):
    """使用PCA降维得到综合质量分数"""
    # 标准化
    scaler = StandardScaler()
    metrics_scaled = scaler.fit_transform(metrics_df)
    
    # PCA降维到1维
    pca = PCA(n_components=1)
    quality_score = pca.fit_transform(metrics_scaled)
    
    # 归一化到[0, 1]
    quality_score = (quality_score - quality_score.min()) / (quality_score.max() - quality_score.min())
    
    return quality_score.flatten(), pca.explained_variance_ratio_[0]
```

**优势**：
- 完全数据驱动，无主观权重
- 自动捕捉指标间的相关性
- 可解释性：通过主成分载荷了解各指标贡献

**劣势**：
- 不同任务类型需要分别计算
- 需要足够的样本数

#### 方法二：熵权法（Entropy Weight Method）

**原理**：根据指标的信息熵自动确定权重，信息量大的指标权重高

```python
import numpy as np

def entropy_weight_score(metrics_df):
    """使用熵权法计算综合质量分数"""
    # 归一化到[0, 1]
    metrics_norm = (metrics_df - metrics_df.min()) / (metrics_df.max() - metrics_df.min())
    
    # 计算每个指标的熵
    n = len(metrics_norm)
    p = metrics_norm / metrics_norm.sum(axis=0)  # 概率化
    p = p.replace(0, 1e-10)  # 避免log(0)
    
    entropy = -1 / np.log(n) * (p * np.log(p)).sum(axis=0)
    
    # 计算权重（熵越小，权重越大）
    weights = (1 - entropy) / (1 - entropy).sum()
    
    # 加权求和
    quality_score = (metrics_norm * weights).sum(axis=1)
    
    return quality_score, weights
```

**优势**：
- 客观权重，基于数据分布
- 区分度高的指标自动获得更高权重
- 适用于不同任务类型

**劣势**：
- 对异常值敏感
- 需要所有指标同向（越大越好或越小越好）

#### 方法三：TOPSIS（逼近理想解排序法）

**原理**：计算每个模型与理想解和负理想解的距离，选择最接近理想解的模型

```python
from sklearn.preprocessing import MinMaxScaler

def topsis_score(metrics_df, is_benefit):
    """
    TOPSIS方法计算综合质量分数
    
    Args:
        metrics_df: 指标数据框
        is_benefit: 布尔列表，True表示越大越好，False表示越小越好
    """
    # 归一化
    scaler = MinMaxScaler()
    metrics_norm = scaler.fit_transform(metrics_df)
    
    # 处理成本型指标（越小越好）
    for i, benefit in enumerate(is_benefit):
        if not benefit:
            metrics_norm[:, i] = 1 - metrics_norm[:, i]
    
    # 理想解和负理想解
    ideal_best = metrics_norm.max(axis=0)
    ideal_worst = metrics_norm.min(axis=0)
    
    # 计算距离
    dist_best = np.sqrt(((metrics_norm - ideal_best) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((metrics_norm - ideal_worst) ** 2).sum(axis=1))
    
    # 相对接近度
    quality_score = dist_worst / (dist_best + dist_worst)
    
    return quality_score
```

**优势**：
- 考虑了理想解和负理想解
- 可处理不同方向的指标（越大越好/越小越好）
- 结果直观，易于解释

**劣势**：
- 需要预先定义指标方向
- 对极端值敏感

#### 方法四：层次分析法（AHP）+ 专家权重

**原理**：通过专家判断矩阵确定指标权重，但基于一致性检验保证客观性

```python
import numpy as np

def ahp_weights(comparison_matrix):
    """
    层次分析法计算权重
    
    Args:
        comparison_matrix: 成对比较矩阵（专家判断）
    """
    # 计算特征向量（权重）
    eigenvalues, eigenvectors = np.linalg.eig(comparison_matrix)
    max_eigenvalue = eigenvalues.max()
    weights = eigenvectors[:, eigenvalues.argmax()].real
    weights = weights / weights.sum()
    
    # 一致性检验
    n = len(comparison_matrix)
    CI = (max_eigenvalue - n) / (n - 1)
    RI = {3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}  # 随机一致性指标
    CR = CI / RI.get(n, 1.0)
    
    if CR > 0.1:
        print(f"⚠️  一致性比率 CR={CR:.3f} > 0.1，权重可能不可靠")
    
    return weights, CR
```

**优势**：
- 结合专家经验
- 一致性检验保证客观性
- 适用于复杂决策

**劣势**：
- 需要专家参与
- 主观性仍然存在（但有约束）

### 3.5 推荐方案：多层次评估体系

**第一层：原始指标（完全客观）**
- 保留所有原始指标，不做合并
- 用于详细分析和特定场景选择

**第二层：任务维度聚合（半客观）**
- 使用熵权法或PCA为每个任务类型生成综合分数
- 用于任务内模型排序

**第三层：跨任务综合（应用导向）**
- 根据实际应用场景，用户自定义任务权重
- 或使用帕累托分析，不强制排序

**实现示例**：
```python
class QualityEvaluationSystem:
    def __init__(self, method='entropy'):
        """
        Args:
            method: 'entropy', 'pca', 'topsis', 'ahp', 或 'none'（仅保留原始指标）
        """
        self.method = method
    
    def evaluate(self, metrics_df, task_type):
        """评估质量"""
        # 第一层：原始指标
        raw_metrics = self.extract_raw_metrics(metrics_df, task_type)
        
        # 第二层：任务维度聚合（可选）
        if self.method == 'none':
            task_score = None
        elif self.method == 'entropy':
            task_score, weights = entropy_weight_score(raw_metrics)
        elif self.method == 'pca':
            task_score, variance = pca_quality_score(raw_metrics)
        elif self.method == 'topsis':
            is_benefit = self.get_metric_directions(task_type)
            task_score = topsis_score(raw_metrics, is_benefit)
        
        return {
            'raw_metrics': raw_metrics,
            'task_score': task_score,
            'method': self.method
        }
```

## 4. 实现路线图

### 4.1 阶段一：基础指标实现（优先级：高）

**目标**：实现不依赖外部模型的基础指标

**任务**：
1. ✅ Exact Match
2. ✅ F1 Score
3. ✅ Distinct-N
4. ✅ 编译检查
5. ✅ ROUGE (使用 `rouge` 库)
6. ✅ 数值精度匹配

**依赖**：
```bash
pip install rouge nltk
```

**预计时间**：2-3 小时

### 4.2 阶段二：深度学习指标（优先级：中）

**目标**：实现基于预训练模型的指标

**任务**：
1. ⏳ BERTScore (使用 `bert-score` 库)
2. ⏳ BARTScore (使用已有的 BARTScore 工具)
3. ⏳ 困惑度计算
4. ⏳ chrF (字符级F分数，用于翻译任务)

**依赖**：
```bash
pip install bert-score transformers torch
pip install python-Levenshtein  # 用于编辑距离计算
# BARTScore 使用项目中已有的工具
```

**注意事项**：
- BERTScore 首次运行会下载模型（~400MB）
- BARTScore 需要 GPU 加速（CPU 较慢）
- 可设置环境变量控制模型缓存位置

**预计时间**：3-4 小时

### 4.3 阶段三：代码执行评估（优先级：低）

**目标**：实现代码测试用例执行

**任务**：
1. ⏳ 安全沙箱环境
2. ⏳ 测试用例执行
3. ⏳ Pass@k 计算

**依赖**：
```bash
pip install RestrictedPython  # 或使用 Docker 沙箱
```

**注意事项**：
- 代码执行存在安全风险，需要沙箱隔离
- 可选方案：仅评估编译率，跳过执行

**预计时间**：4-6 小时（可选）


## 5. 质量评估脚本设计

### 5.1 脚本结构

```
data/analize/scripts/
├── quality_evaluation/
│   ├── __init__.py
│   ├── base_evaluator.py          # 基础评估器接口
│   ├── code_evaluator.py          # 代码任务评估
│   ├── creative_evaluator.py      # 创意任务评估
│   ├── math_evaluator.py          # 数学任务评估
│   ├── qa_evaluator.py            # 问答任务评估
│   ├── summary_evaluator.py       # 摘要任务评估
│   ├── reasoning_evaluator.py     # 逻辑推理任务评估
│   ├── translation_evaluator.py   # 翻译任务评估
│   ├── aggregation.py             # 聚合方法（PCA、熵权法等）
│   ├── metrics/                   # 指标实现
│   │   ├── exact_match.py
│   │   ├── f1_score.py
│   │   ├── distinct_n.py
│   │   ├── rouge_metrics.py
│   │   ├── bert_score_wrapper.py
│   │   ├── bart_score_wrapper.py
│   │   └── bleu_metrics.py
│   └── utils.py                   # 工具函数
└── evaluate_all_models.py         # 主评估脚本
```

### 5.2 基础评估器接口（更新）

```python
# base_evaluator.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseEvaluator(ABC):
    """质量评估器基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.aggregation_method = config.get('aggregation', 'none')  # 'none', 'entropy', 'pca', 'topsis'
    
    @abstractmethod
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict[str, Any] = None) -> Dict[str, float]:
        """
        评估生成文本质量，返回多维度指标
        
        Args:
            generated: 生成的文本
            reference: 参考答案（可选）
            context: 额外上下文信息
        
        Returns:
            Dict[str, float]: 多维度指标字典，不做主观加权
        """
        pass
    
    def get_metric_categories(self) -> Dict[str, List[str]]:
        """
        返回指标分类
        
        Returns:
            Dict[str, List[str]]: 如 {'accuracy': ['exact_match', 'f1'], 'semantic': ['bertscore']}
        """
        return {}
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """
        返回指标方向（True=越大越好，False=越小越好）
        
        Returns:
            Dict[str, bool]: 如 {'exact_match': True, 'perplexity': False}
        """
        return {}
    
    def aggregate_scores(self, scores: Dict[str, float], 
                        method: Optional[str] = None) -> Optional[float]:
        """
        聚合多个指标为单一分数（可选）
        
        Args:
            scores: 原始指标字典
            method: 聚合方法，None表示不聚合
        
        Returns:
            Optional[float]: 聚合分数，或None（不聚合）
        """
        method = method or self.aggregation_method
        
        if method == 'none':
            return None
        
        # 过滤有效指标
        valid_scores = {k: v for k, v in scores.items() if v is not None}
        
        if not valid_scores:
            return None
        
        if method == 'entropy':
            from .aggregation import entropy_weight_score
            import pandas as pd
            df = pd.DataFrame([valid_scores])
            score, _ = entropy_weight_score(df)
            return score[0]
        
        elif method == 'pca':
            from .aggregation import pca_quality_score
            import pandas as pd
            df = pd.DataFrame([valid_scores])
            score, _ = pca_quality_score(df)
            return score[0]
        
        elif method == 'topsis':
            from .aggregation import topsis_score
            import pandas as pd
            df = pd.DataFrame([valid_scores])
            directions = [self.get_metric_directions().get(k, True) for k in valid_scores.keys()]
            score = topsis_score(df, directions)
            return score[0]
        
        else:
            raise ValueError(f"Unknown aggregation method: {method}")
```

### 5.3 主评估脚本（更新）

```python
# evaluate_all_models.py
import json
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from quality_evaluation import (
    CodeEvaluator, CreativeEvaluator, MathEvaluator,
    QAEvaluator, SummaryEvaluator
)

def evaluate_model_quality(model_name: str, data_dir: Path, 
                          aggregation_method: str = 'none'):
    """
    评估单个模型的质量
    
    Args:
        model_name: 模型名称
        data_dir: 数据目录
        aggregation_method: 聚合方法 ('none', 'entropy', 'pca', 'topsis')
    """
    
    # 初始化评估器
    config = {'aggregation': aggregation_method}
    evaluators = {
        'code': CodeEvaluator(config),
        'creative': CreativeEvaluator(config),
        'math': MathEvaluator(config),
        'qa': QAEvaluator(config),
        'summary': SummaryEvaluator(config),
        'reasoning': ReasoningEvaluator(config),
        'translation': TranslationEvaluator(config)
    }
    
    # 加载数据
    model_dir = data_dir / model_name
    experiments = load_experiment_data(model_dir)
    
    if not experiments:
        print(f"⚠️  No data found for {model_name}")
        return None
    
    # 评估每个实验
    results = []
    for exp in tqdm(experiments, desc=f"Evaluating {model_name}"):
        task_type = exp['config_ref']['task_type']
        
        if task_type not in evaluators:
            continue
        
        # 提取生成文本
        generated = exp['conversation_summary'][0]['response_preview']
        
        # 评估质量（多维度指标）
        evaluator = evaluators[task_type]
        quality_metrics = evaluator.evaluate(generated)
        
        # 可选：聚合分数
        aggregated_score = evaluator.aggregate_scores(quality_metrics)
        
        # 保存结果
        result = {
            'experiment_id': exp['experiment_id'],
            'model': model_name,
            'task_type': task_type,
            'aggregated_score': aggregated_score,  # 可能为None
            **quality_metrics  # 展开所有原始指标
        }
        results.append(result)
    
    return pd.DataFrame(results)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='评估模型质量')
    parser.add_argument('--aggregation', type=str, default='none',
                       choices=['none', 'entropy', 'pca', 'topsis'],
                       help='聚合方法（默认：none，保留所有原始指标）')
    parser.add_argument('--output-dir', type=str, default='data/analize/pre_data',
                       help='输出目录')
    
    args = parser.parse_args()
    
    data_dir = Path('data')
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 模型列表
    models = [
        'deepseek_8b_ol_q4km', 'gemma_2b_hf_4bit', 'gemma_2b_hf_8bit',
        'gemma_4b_ol_q4km', 'phi3_4b_hf_4bit', 'phi3_4b_hf_8bit',
        'qwen_4b_ol_q4km', 'qwen_8b_ol_q4km', 'qwen25_3b_hf_4bit',
        'qwen25_3b_hf_8bit', 'qwen25_7b_hf_4bit', 'qwen25_7b_hf_8bit'
    ]
    
    # 评估所有模型
    all_results = []
    for model in models:
        print(f"\n{'='*60}")
        print(f"Evaluating: {model}")
        print(f"Aggregation: {args.aggregation}")
        print(f"{'='*60}")
        
        df = evaluate_model_quality(model, data_dir, args.aggregation)
        if df is not None:
            all_results.append(df)
    
    # 合并结果
    if all_results:
        final_df = pd.concat(all_results, ignore_index=True)
        
        # 保存详细指标
        output_file = output_dir / 'quality_scores_detailed.csv'
        final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # 生成任务-模型适配性分析
        generate_task_model_matching(final_df, output_dir)
        
        print(f"\n✅ Quality evaluation completed!")
        print(f"📊 Detailed results: {output_file}")
        print(f"📈 Total experiments: {len(final_df)}")
        print(f"🎯 Aggregation method: {args.aggregation}")
    else:
        print("\n❌ No results to save")

def generate_task_model_matching(df: pd.DataFrame, output_dir: Path):
    """生成任务-模型适配性分析"""
    
    # 按任务类型分组，找出每个指标的最优模型
    task_groups = df.groupby('task_type')
    
    matching_results = []
    
    for task, group in task_groups:
        # 获取所有指标列（排除元数据列）
        metric_cols = [col for col in group.columns 
                      if col not in ['experiment_id', 'model', 'task_type', 'aggregated_score']]
        
        # 对每个指标找出Top 3模型
        for metric in metric_cols:
            if group[metric].notna().sum() == 0:
                continue
            
            top_models = group.nlargest(3, metric)[['model', metric]]
            
            for rank, (idx, row) in enumerate(top_models.iterrows(), 1):
                matching_results.append({
                    'task_type': task,
                    'metric': metric,
                    'rank': rank,
                    'model': row['model'],
                    'score': row[metric]
                })
    
    # 保存任务-模型匹配结果
    matching_df = pd.DataFrame(matching_results)
    matching_file = output_dir / 'task_model_matching.csv'
    matching_df.to_csv(matching_file, index=False, encoding='utf-8-sig')
    
    print(f"🎯 Task-model matching: {matching_file}")

if __name__ == '__main__':
    main()
```

## 6. 依赖安装与环境配置

### 6.1 必需依赖

```bash
# 基础依赖
pip install pandas numpy tqdm

# 文本处理
pip install nltk rouge

# 深度学习指标（可选，推荐）
pip install bert-score transformers torch

# 下载 NLTK 数据
python -c "import nltk; nltk.download('punkt')"
```

### 6.2 BARTScore 配置

项目中已有 BARTScore 工具（`tools/thesis_reproduction/BARTScore/`），需要：

1. 确保 BARTScore 环境已配置（参考 `BARTScore_使用说明.md`）
2. 下载预训练模型（如需要）
3. 在评估脚本中正确引用

### 6.3 GPU 加速配置

BERTScore 和 BARTScore 支持 GPU 加速：

```python
# 检测 GPU 可用性
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# 在评估器中使用
evaluator = BERTScoreEvaluator(device=device)
```

## 7. 质量评估工作流

### 7.1 完整流程

```
1. 数据准备
   ├── 加载实验结果 JSON
   ├── 提取生成文本
   └── 准备参考答案（如有）

2. 质量评估
   ├── 根据任务类型选择评估器
   ├── 计算各项指标
   └── 聚合为综合质量分数

3. 结果保存
   ├── 保存详细指标 (quality_scores.csv)
   ├── 保存汇总统计
   └── 生成质量报告

4. 集成到分析
   ├── 合并到主数据集
   ├── 用于质效比计算
   └── 生成可视化图表
```

### 7.2 运行命令

```bash
# 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 运行质量评估
cd data/analize/scripts
python evaluate_all_models.py

# 查看结果
cat ../pre_data/quality_scores.csv
```

### 7.3 预期输出

```
data/analize/pre_data/
├── quality_scores.csv              # 详细质量分数
│   ├── experiment_id
│   ├── model
│   ├── task_type
│   ├── quality_score              # 综合分数
│   ├── exact_match                # 任务特定指标
│   ├── f1_score
│   ├── bertscore_f1
│   └── ...
└── quality_summary.csv             # 汇总统计
    ├── model
    ├── task_type
    ├── mean_quality
    ├── std_quality
    └── ...
```

## 8. 质量控制与验证

### 8.1 单元测试

为每个评估器编写单元测试：

```python
# tests/test_qa_evaluator.py
import unittest
from quality_evaluation import QAEvaluator

class TestQAEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = QAEvaluator()
    
    def test_exact_match(self):
        generated = "北京"
        reference = "北京"
        scores = self.evaluator.evaluate(generated, reference)
        self.assertEqual(scores['exact_match'], 1.0)
    
    def test_partial_match(self):
        generated = "中国的首都是北京"
        reference = "北京"
        scores = self.evaluator.evaluate(generated, reference)
        self.assertGreater(scores['f1'], 0.0)
        self.assertLess(scores['exact_match'], 1.0)
```

### 8.2 人工抽查

随机抽取 5-10 个样本，人工验证评分合理性：

```python
def manual_inspection(quality_df, n_samples=10):
    """随机抽样进行人工检查"""
    samples = quality_df.sample(n=n_samples)
    
    for idx, row in samples.iterrows():
        print(f"\n{'='*60}")
        print(f"Experiment: {row['experiment_id']}")
        print(f"Model: {row['model']}")
        print(f"Task: {row['task_type']}")
        print(f"Quality Score: {row['quality_score']:.3f}")
        print(f"Generated: {row['generated_text'][:200]}...")
        print(f"{'='*60}")
        
        # 等待人工确认
        input("Press Enter to continue...")
```

### 8.3 指标一致性检查

验证不同指标间的相关性：

```python
import seaborn as sns
import matplotlib.pyplot as plt

def check_metric_correlation(quality_df):
    """检查指标间相关性"""
    metric_cols = [col for col in quality_df.columns 
                  if col not in ['experiment_id', 'model', 'task_type']]
    
    corr_matrix = quality_df[metric_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Quality Metrics Correlation Matrix')
    plt.tight_layout()
    plt.savefig('data/analize/figures/quality_metrics_correlation.png', dpi=300)
```

---

**文档版本**: v1.0  
**创建日期**: 2026-03-04  
**作者**: Kiro AI Assistant  
**状态**: 待实现
