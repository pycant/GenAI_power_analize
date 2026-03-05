# 翻译任务 (Translation) 质量评估方法设计

## 1. 评估目标

评估模型在机器翻译任务中的**准确性、流畅性、完整性与风格一致性**。

## 2. 数据特征分析

### 2.1 任务类型

基于提供的翻译问题，任务类型为：
- **英译中 (English → Chinese)**: q01, q02, q04, q05 - 4个问题
- **中译英 (Chinese → English)**: q03 - 1个问题
- **句子级翻译**: 所有问题均为单句翻译
- **领域多样**: 涵盖科技、历史、日常用语、环境等多个领域

### 2.2 翻译样本

| 问题ID | 源语言 | 目标语言 | 源文本 | 领域 |
|--------|--------|----------|--------|------|
| q01 | 英语 | 中文 | Artificial intelligence is transforming... | 科技 |
| q02 | 英语 | 中文 | The Renaissance was a period... | 历史文化 |
| q03 | 中文 | 英语 | 深度学习在计算机视觉领域... | 科技 |
| q04 | 英语 | 中文 | The quick brown fox jumps... | 日常用语 |
| q05 | 英语 | 中文 | Climate change poses... | 环境 |

### 2.3 评估挑战

- **无标准参考译文**: 数据集中没有提供人工翻译的参考答案
- **多样性**: 同一源文本可以有多种正确的翻译方式
- **语言对差异**: 英中翻译和中英翻译的评估标准可能不同
- **主观性**: 翻译质量评估具有一定主观性


## 3. 核心指标

### 3.1 BLEU (Bilingual Evaluation Understudy) ✅ 高度可行

**定义**：
- 机器翻译最经典的自动评估指标
- 基于 N-gram 精确匹配计算几何平均值
- 衡量生成译文与参考译文的词汇重叠度

**计算方法**：

1. 计算 N-gram 精确率（通常 N=1,2,3,4）
2. 应用简短惩罚因子（BP）
3. 计算几何平均值

**数学表达**：
```
BLEU = BP × exp(Σ(w_n × log(p_n)))

其中：
- p_n: n-gram 精确率
- w_n: 权重（通常均匀分配，各为 0.25）
- BP: 简短惩罚因子 = min(1, exp(1 - r/c))
  - r: 参考译文长度
  - c: 候选译文长度
```

**范围**: [0, 1]，越高越好

**优势**：
- ✅ 机器翻译领域最广泛使用的指标
- ✅ 计算快速，无需外部模型
- ✅ 对高资源语言对（如英↔中）效果好
- ✅ 可计算多个 N-gram 级别（BLEU-1, BLEU-2, BLEU-4）

**劣势**：
- ⚠️ 需要参考译文（本项目需要创建）
- ⚠️ 对同义词和改写不友好
- ⚠️ 不考虑语义和流畅性

**实现方案**：
```python
def calculate_bleu(generated: str, reference: str, 
                   max_n: int = 4, lang: str = 'zh') -> Dict[str, float]:
    """
    计算 BLEU 分数
    
    Args:
        generated: 生成的译文
        reference: 参考译文
        max_n: 最大 N-gram 长度
        lang: 语言（'zh' 中文按字符分词，'en' 英文按空格分词）
    
    Returns:
        Dict: BLEU-1, BLEU-2, BLEU-4 分数
    """
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    
    # 分词
    if lang == 'zh':
        # 中文按字符分词
        reference_tokens = [list(reference)]
        generated_tokens = list(generated)
    else:
        # 英文按空格分词
        reference_tokens = [reference.split()]
        generated_tokens = generated.split()
    
    # 平滑函数（避免零分）
    smoothing = SmoothingFunction().method1
    
    scores = {}
    
    # BLEU-1 (unigram)
    scores['bleu_1'] = sentence_bleu(
        reference_tokens, generated_tokens,
        weights=(1, 0, 0, 0),
        smoothing_function=smoothing
    )
    
    # BLEU-2 (bigram)
    scores['bleu_2'] = sentence_bleu(
        reference_tokens, generated_tokens,
        weights=(0.5, 0.5, 0, 0),
        smoothing_function=smoothing
    )
    
    # BLEU-4 (standard)
    scores['bleu_4'] = sentence_bleu(
        reference_tokens, generated_tokens,
        weights=(0.25, 0.25, 0.25, 0.25),
        smoothing_function=smoothing
    )
    
    return scores
```


### 3.2 chrF / chrF++ (Character n-gram F-score) ✅ 高度可行

**定义**：
- 基于字符级别的 F1 分数
- 对中↔英这种字符级语言非常友好
- 比 BLEU 更稳定，对形态丰富的语言更适用

**计算方法**：

1. 提取字符 N-gram（通常 N=6）
2. 计算精确率和召回率
3. 计算 F1 分数

**数学表达**：
```
chrF = (1 + β²) × (P × R) / (β² × P + R)

其中：
- P: 字符 N-gram 精确率
- R: 字符 N-gram 召回率
- β: 通常设为 1（F1）或 2（F2，更重视召回率）
```

**范围**: [0, 1]，越高越好

**优势**：
- ✅ 对中文等字符级语言更友好
- ✅ 比 BLEU 更稳定
- ✅ 对拼写错误和形态变化更宽容
- ✅ 不需要分词

**实现方案**：
```python
def calculate_chrf(generated: str, reference: str, 
                   n: int = 6, beta: int = 2) -> float:
    """
    计算 chrF 分数
    
    Args:
        generated: 生成的译文
        reference: 参考译文
        n: 字符 N-gram 长度
        beta: F-score 的 beta 参数（1=F1, 2=F2）
    
    Returns:
        float: chrF 分数
    """
    try:
        from nltk.translate.chrf_score import sentence_chrf
        return sentence_chrf(reference, generated, 
                            min_len=1, max_len=n, beta=beta)
    except:
        # 手动实现简化版
        def char_ngrams(text, n):
            return [text[i:i+n] for i in range(len(text)-n+1)]
        
        ref_ngrams = set(char_ngrams(reference, n))
        gen_ngrams = set(char_ngrams(generated, n))
        
        if len(gen_ngrams) == 0 or len(ref_ngrams) == 0:
            return 0.0
        
        # 计算精确率和召回率
        common = ref_ngrams & gen_ngrams
        precision = len(common) / len(gen_ngrams)
        recall = len(common) / len(ref_ngrams)
        
        # 计算 F-score
        if precision + recall == 0:
            return 0.0
        
        f_score = ((1 + beta**2) * precision * recall) / (beta**2 * precision + recall)
        return f_score
```


### 3.3 BERTScore ✅ 高度可行

**定义**：
- 基于预训练语言模型 BERT 的语义相似度
- 使用上下文嵌入计算 token 级别的相似度
- 能识别同义词和语义等价的表达

**计算方法**：

1. 使用多语言 BERT 模型获取 token 向量
2. 计算译文与参考译文 token 间的余弦相似度
3. 通过最大匹配得到 Precision/Recall/F1

**数学表达**：
```
BERTScore_P = (1/|x|) × Σ_{x_i ∈ x} max_{y_j ∈ y} cos(e_{x_i}, e_{y_j})
BERTScore_R = (1/|y|) × Σ_{y_j ∈ y} max_{x_i ∈ x} cos(e_{x_i}, e_{y_j})
BERTScore_F1 = 2 × P × R / (P + R)
```

**范围**: [0, 1]，越高越好

**优势**：
- ✅ 能识别同义词和改写
- ✅ 更接近人类判断
- ✅ 对语义等价的不同表述友好
- ✅ 支持多语言

**劣势**：
- ⚠️ 需要 GPU 加速（CPU 较慢）
- ⚠️ 首次运行需下载模型（~400MB）

**实现方案**：
```python
def calculate_bertscore(generated: str, reference: str,
                       lang: str = 'zh', device: str = 'cuda') -> Dict[str, float]:
    """
    计算 BERTScore
    
    Args:
        generated: 生成的译文
        reference: 参考译文
        lang: 语言代码（'zh' 中文，'en' 英文）
        device: 'cuda' 或 'cpu'
    
    Returns:
        Dict: precision, recall, f1
    """
    try:
        from bert_score import score
        
        # 使用多语言 BERT 模型
        model_type = 'bert-base-multilingual-cased'
        
        P, R, F1 = score(
            [generated],
            [reference],
            model_type=model_type,
            lang=lang,
            device=device,
            verbose=False
        )
        
        return {
            'bertscore_precision': P.item(),
            'bertscore_recall': R.item(),
            'bertscore_f1': F1.item()
        }
    except Exception as e:
        print(f"⚠️  BERTScore calculation failed: {e}")
        return {
            'bertscore_precision': None,
            'bertscore_recall': None,
            'bertscore_f1': None
        }
```


## 4. 辅助指标

### 4.1 COMET ⚠️ 可行但成本较高

**定义**：
- 基于预训练模型的跨语言语义匹配评估
- 目前最接近人类判断的自动评估指标
- 使用 XLM-RoBERTa 等跨语言模型

**优势**：
- ✅ 最接近人类评分的自动指标
- ✅ 能捕捉深层语义
- ✅ 对改写和同义词友好

**劣势**：
- ⚠️ 需要 GPU 加速
- ⚠️ 计算成本高
- ⚠️ 模型较大（~2GB）

**建议**：作为可选的高级指标

### 4.2 长度比 (Length Ratio) ✅ 高度可行

**定义**：
- 译文长度与源文长度的比值
- 评估翻译的简洁性和完整性

**实现方案**：
```python
def calculate_length_ratio(generated: str, source: str) -> float:
    """计算长度比"""
    if len(source) == 0:
        return 0.0
    return len(generated) / len(source)
```

**应用**：
- 检测过度翻译或遗漏
- 评估翻译的简洁性
- 英中翻译通常比值 < 1，中英翻译通常比值 > 1

### 4.3 编辑距离 (Edit Distance) ✅ 可行

**定义**：
- 计算从生成译文转换到参考译文需要的最少编辑操作数
- 归一化后可作为相似度指标

**实现方案**：
```python
def calculate_edit_distance(generated: str, reference: str) -> Dict[str, float]:
    """计算归一化编辑距离"""
    try:
        from Levenshtein import distance
        
        edit_dist = distance(generated, reference)
        max_len = max(len(generated), len(reference))
        
        # 归一化为相似度（1 - 归一化距离）
        similarity = 1 - (edit_dist / max_len) if max_len > 0 else 0.0
        
        return {
            'edit_distance': edit_dist,
            'normalized_edit_distance': edit_dist / max_len if max_len > 0 else 0.0,
            'edit_similarity': similarity
        }
    except ImportError:
        return {
            'edit_distance': None,
            'normalized_edit_distance': None,
            'edit_similarity': None
        }
```


## 5. LLM-as-Judge 评估（可选高级方法）

### 5.1 定义

使用更强大的 LLM（如 GPT-4、Claude）作为评判者，对翻译质量进行多维度打分。

### 5.2 评估维度

1. **准确性 (Accuracy)**: 是否忠实原文，无增删改
2. **流畅性 (Fluency)**: 是否通顺自然、符合目标语习惯
3. **完整性 (Completeness)**: 是否完整覆盖原文所有信息
4. **术语一致性 (Terminology)**: 专业术语是否准确
5. **风格适配 (Style)**: 是否符合目标语言的表达习惯

### 5.3 Prompt 模板

```
你是专业翻译评估专家，请从以下维度对译文打分（1-5分）：

源语言：{source_lang}
目标语言：{target_lang}

原文：{source_text}
参考译文（可选）：{reference}
模型译文：{generated}

评估维度：
1. 准确性：是否忠实原文，无增删改、无幻觉 (1-5分)
2. 流畅性：是否通顺自然、符合目标语习惯 (1-5分)
3. 完整性：是否完整覆盖原文所有信息 (1-5分)
4. 术语准确性：专业术语是否正确 (1-5分)
5. 风格适配：是否符合目标语言表达习惯 (1-5分)

输出格式（JSON）：
{
  "accuracy": <1-5>,
  "fluency": <1-5>,
  "completeness": <1-5>,
  "terminology": <1-5>,
  "style": <1-5>,
  "total_score": <总分/25>,
  "feedback": "<简短评语>",
  "errors": "<错误点，如有>"
}
```

### 5.4 优劣势

**优势**：
- ✅ 最接近人类评估
- ✅ 能评估细微的语义差异
- ✅ 提供详细反馈

**劣势**：
- ⚠️ 需要 API 调用（成本高）
- ⚠️ 评估速度慢
- ⚠️ 需要网络连接

**建议**：作为可选的验证方法，用于抽样检查


## 6. 参考译文创建策略

### 6.1 问题分析

由于数据集中没有提供标准参考译文，我们需要创建参考译文。有以下几种策略：

### 6.2 策略选项

#### 策略1：使用最佳模型输出作为参考（推荐）

**方法**：
1. 对所有模型的译文进行初步评估（使用无参考指标，如困惑度）
2. 选择质量最高的译文作为参考
3. 或使用多个高质量译文的共识

**优势**：
- ✅ 快速可行
- ✅ 基于实际模型输出
- ✅ 可自动化

**劣势**：
- ⚠️ 可能存在偏差
- ⚠️ 需要初步筛选

#### 策略2：人工创建参考译文

**方法**：
1. 由专业译者翻译源文本
2. 创建高质量的参考译文

**优势**：
- ✅ 质量最高
- ✅ 最权威

**劣势**：
- ⚠️ 成本高
- ⚠️ 耗时长

#### 策略3：使用商业翻译 API

**方法**：
1. 使用 Google Translate、DeepL 等商业 API
2. 获取高质量译文作为参考

**优势**：
- ✅ 质量较高
- ✅ 快速获取

**劣势**：
- ⚠️ 需要 API 调用
- ⚠️ 可能有成本

### 6.3 推荐方案

**阶段1：快速评估**
- 使用策略1（最佳模型输出）创建初步参考
- 结合多个模型的共识

**阶段2：精细评估**
- 使用策略3（商业 API）或策略2（人工翻译）
- 创建高质量参考译文

### 6.4 参考译文示例

基于源文本，创建参考译文：

```python
TRANSLATION_REFERENCES = {
    'q01': {
        'source': 'Artificial intelligence is transforming the way we live and work.',
        'reference': '人工智能正在改变我们的生活和工作方式。',
        'source_lang': 'eng',
        'target_lang': 'zho_Hans'
    },
    'q02': {
        'source': 'The Renaissance was a period of great cultural and artistic achievement in Europe.',
        'reference': '文艺复兴是欧洲文化和艺术成就辉煌的时期。',
        'source_lang': 'eng',
        'target_lang': 'zho_Hans'
    },
    'q03': {
        'source': '深度学习在计算机视觉领域取得了突破性进展。',
        'reference': 'Deep learning has made breakthrough progress in the field of computer vision.',
        'source_lang': 'zho_Hans',
        'target_lang': 'eng'
    },
    'q04': {
        'source': 'The quick brown fox jumps over the lazy dog.',
        'reference': '敏捷的棕色狐狸跳过了懒狗。',
        'source_lang': 'eng',
        'target_lang': 'zho_Hans'
    },
    'q05': {
        'source': 'Climate change poses significant challenges to global sustainability.',
        'reference': '气候变化对全球可持续发展构成重大挑战。',
        'source_lang': 'eng',
        'target_lang': 'zho_Hans'
    }
}
```


## 7. 推荐评估方案

### 7.1 核心指标组合

| 维度 | 指标 | 优先级 | 计算成本 | 可行性 | 适用场景 |
|------|------|--------|----------|--------|----------|
| 词汇匹配 | BLEU-4 | ⭐⭐⭐ | 低 | ✅ 高 | 标准评估 |
| 词汇匹配 | BLEU-1/2 | ⭐⭐ | 低 | ✅ 高 | 补充评估 |
| 字符匹配 | chrF++ | ⭐⭐⭐ | 低 | ✅ 高 | 中文友好 |
| 语义相似 | BERTScore | ⭐⭐⭐ | 中 | ✅ 高 | 语义评估 |
| 简洁性 | 长度比 | ⭐⭐ | 低 | ✅ 高 | 完整性检查 |
| 编辑距离 | Edit Distance | ⭐ | 低 | ✅ 高 | 辅助指标 |
| 深度评估 | COMET | ⭐ | 高 | ⚠️ 中 | 可选高级 |
| 综合评估 | LLM-as-Judge | ⭐ | 极高 | ⚠️ 中 | 验证抽样 |

### 7.2 评估流程

```
1. 准备阶段
   ├── 加载源文本和模型译文
   ├── 准备参考译文（策略1/2/3）
   └── 确定语言对和评估配置

2. 基础指标计算
   ├── BLEU-1/2/4（词汇匹配）
   ├── chrF++（字符匹配）
   └── 长度比（完整性）

3. 语义指标计算
   ├── BERTScore（语义相似度）
   └── 编辑距离（可选）

4. 可选高级评估
   ├── COMET（如果资源充足）
   └── LLM-as-Judge（抽样验证）

5. 结果汇总
   ├── 按模型汇总平均分数
   ├── 按语言对分析难度
   └── 生成评估报告
```

### 7.3 评分权重建议

#### 方案1：均衡评估（推荐）

```python
translation_quality_score = {
    'bleu_4': 0.30,              # 30% - 标准词汇匹配
    'chrf': 0.30,                # 30% - 字符级匹配
    'bertscore_f1': 0.30,        # 30% - 语义相似度
    'length_compliance': 0.10    # 10% - 长度合理性
}
```

**理由**：三大核心指标均衡，覆盖词汇、字符、语义三个层面

#### 方案2：语义优先

```python
translation_quality_score = {
    'bertscore_f1': 0.40,        # 40% - 语义最重要
    'bleu_4': 0.25,              # 25% - 词汇匹配
    'chrf': 0.25,                # 25% - 字符匹配
    'length_compliance': 0.10    # 10% - 长度合理性
}
```

#### 方案3：多维度呈现（强烈推荐）

不计算单一综合分数，保留所有原始指标：

```python
translation_quality_metrics = {
    'lexical': {
        'bleu_1': float,
        'bleu_2': float,
        'bleu_4': float
    },
    'character': {
        'chrf': float,
        'chrf_plus': float
    },
    'semantic': {
        'bertscore_precision': float,
        'bertscore_recall': float,
        'bertscore_f1': float
    },
    'fluency': {
        'length_ratio': float,
        'edit_similarity': float
    },
    'advanced': {
        'comet_score': float,      # 可选
        'llm_judge_score': float   # 可选
    }
}
```

**理由**：保留完整信息，支持多角度分析，避免主观权重


## 8. 实现方案

### 8.1 评估器设计

```python
# data/analize/scripts/quality_evaluation/translation_evaluator.py

from typing import Dict, Optional
from .base_evaluator import BaseEvaluator


class TranslationEvaluator(BaseEvaluator):
    """翻译任务评估器"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.use_bertscore = config.get('use_bertscore', True) if config else True
        self.use_comet = config.get('use_comet', False) if config else False
        self.device = config.get('device', 'cuda') if config else 'cuda'
    
    def evaluate(self, generated: str, reference: str = None,
                 context: Dict = None) -> Dict[str, float]:
        """
        评估翻译质量
        
        Args:
            generated: 生成的译文
            reference: 参考译文（必需）
            context: 额外上下文（包含源文本、语言对信息）
        
        Returns:
            Dict[str, float]: 多维度指标
        """
        scores = {}
        
        # 基础检查
        if not generated or not reference:
            return self._get_zero_scores()
        
        # 获取语言信息
        source_text = context.get('source_text', '') if context else ''
        target_lang = context.get('target_lang', 'zh') if context else 'zh'
        
        # 1. BLEU 分数
        bleu_scores = self._calculate_bleu(generated, reference, target_lang)
        scores.update(bleu_scores)
        
        # 2. chrF 分数
        scores['chrf'] = self._calculate_chrf(generated, reference)
        
        # 3. BERTScore（可选）
        if self.use_bertscore:
            bertscore_results = self._calculate_bertscore(
                generated, reference, target_lang
            )
            scores.update(bertscore_results)
        
        # 4. 长度比
        if source_text:
            scores['length_ratio'] = self._calculate_length_ratio(
                generated, source_text
            )
        else:
            scores['length_ratio'] = None
        
        # 5. 编辑距离
        edit_scores = self._calculate_edit_distance(generated, reference)
        scores.update(edit_scores)
        
        # 6. COMET（可选，成本高）
        if self.use_comet and source_text:
            scores['comet_score'] = self._calculate_comet(
                source_text, generated, reference
            )
        
        return scores
    
    def _calculate_bleu(self, generated: str, reference: str,
                       lang: str = 'zh') -> Dict[str, float]:
        """计算 BLEU 分数"""
        try:
            from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
            
            # 分词
            if lang == 'zh' or lang == 'zho_Hans':
                reference_tokens = [list(reference)]
                generated_tokens = list(generated)
            else:
                reference_tokens = [reference.split()]
                generated_tokens = generated.split()
            
            smoothing = SmoothingFunction().method1
            
            return {
                'bleu_1': sentence_bleu(
                    reference_tokens, generated_tokens,
                    weights=(1, 0, 0, 0), smoothing_function=smoothing
                ),
                'bleu_2': sentence_bleu(
                    reference_tokens, generated_tokens,
                    weights=(0.5, 0.5, 0, 0), smoothing_function=smoothing
                ),
                'bleu_4': sentence_bleu(
                    reference_tokens, generated_tokens,
                    weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=smoothing
                )
            }
        except Exception as e:
            print(f"⚠️  BLEU calculation failed: {e}")
            return {'bleu_1': None, 'bleu_2': None, 'bleu_4': None}
    
    def _calculate_chrf(self, generated: str, reference: str,
                       n: int = 6, beta: int = 2) -> float:
        """计算 chrF 分数"""
        try:
            from nltk.translate.chrf_score import sentence_chrf
            return sentence_chrf(reference, generated, 
                               min_len=1, max_len=n, beta=beta)
        except:
            # 手动实现
            def char_ngrams(text, n):
                return [text[i:i+n] for i in range(len(text)-n+1)]
            
            ref_ngrams = set(char_ngrams(reference, n))
            gen_ngrams = set(char_ngrams(generated, n))
            
            if len(gen_ngrams) == 0 or len(ref_ngrams) == 0:
                return 0.0
            
            common = ref_ngrams & gen_ngrams
            precision = len(common) / len(gen_ngrams)
            recall = len(common) / len(ref_ngrams)
            
            if precision + recall == 0:
                return 0.0
            
            return ((1 + beta**2) * precision * recall) / (beta**2 * precision + recall)
    
    def _calculate_bertscore(self, generated: str, reference: str,
                            lang: str = 'zh') -> Dict[str, float]:
        """计算 BERTScore"""
        try:
            from bert_score import score
            
            model_type = 'bert-base-multilingual-cased'
            
            P, R, F1 = score(
                [generated], [reference],
                model_type=model_type,
                lang=lang,
                device=self.device,
                verbose=False
            )
            
            return {
                'bertscore_precision': P.item(),
                'bertscore_recall': R.item(),
                'bertscore_f1': F1.item()
            }
        except Exception as e:
            print(f"⚠️  BERTScore calculation failed: {e}")
            return {
                'bertscore_precision': None,
                'bertscore_recall': None,
                'bertscore_f1': None
            }
    
    def _calculate_length_ratio(self, generated: str, source: str) -> float:
        """计算长度比"""
        if len(source) == 0:
            return 0.0
        return len(generated) / len(source)
    
    def _calculate_edit_distance(self, generated: str, 
                                 reference: str) -> Dict[str, float]:
        """计算编辑距离"""
        try:
            from Levenshtein import distance
            
            edit_dist = distance(generated, reference)
            max_len = max(len(generated), len(reference))
            
            return {
                'edit_distance': edit_dist,
                'normalized_edit_distance': edit_dist / max_len if max_len > 0 else 0.0,
                'edit_similarity': 1 - (edit_dist / max_len) if max_len > 0 else 0.0
            }
        except ImportError:
            return {
                'edit_distance': None,
                'normalized_edit_distance': None,
                'edit_similarity': None
            }
    
    def _calculate_comet(self, source: str, generated: str,
                        reference: str) -> float:
        """计算 COMET 分数（可选）"""
        try:
            from comet import download_model, load_from_checkpoint
            
            model_path = download_model("Unbabel/wmt22-comet-da")
            model = load_from_checkpoint(model_path)
            
            data = [{
                "src": source,
                "mt": generated,
                "ref": reference
            }]
            
            output = model.predict(data, batch_size=1, gpus=1)
            return output.scores[0]
        except Exception as e:
            print(f"⚠️  COMET calculation failed: {e}")
            return None
    
    def _get_zero_scores(self) -> Dict[str, float]:
        """返回零分数"""
        return {
            'bleu_1': 0.0,
            'bleu_2': 0.0,
            'bleu_4': 0.0,
            'chrf': 0.0,
            'bertscore_f1': 0.0,
            'length_ratio': 0.0,
            'edit_similarity': 0.0
        }
    
    def get_metric_categories(self) -> Dict[str, list]:
        """返回指标分类"""
        return {
            'lexical': ['bleu_1', 'bleu_2', 'bleu_4'],
            'character': ['chrf'],
            'semantic': ['bertscore_precision', 'bertscore_recall', 'bertscore_f1'],
            'fluency': ['length_ratio', 'edit_similarity'],
            'advanced': ['comet_score']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向(True=越大越好)"""
        return {
            'bleu_1': True,
            'bleu_2': True,
            'bleu_4': True,
            'chrf': True,
            'bertscore_precision': True,
            'bertscore_recall': True,
            'bertscore_f1': True,
            'length_ratio': True,  # 适中为好，但简化为越接近1越好
            'edit_similarity': True,
            'comet_score': True
        }
```


### 8.2 参考译文配置文件

```python
# data/analize/scripts/translation_config.py

# 参考译文配置
TRANSLATION_REFERENCES = {
    'q01': {
        'source': 'Artificial intelligence is transforming the way we live and work.',
        'reference': '人工智能正在改变我们的生活和工作方式。',
        'source_lang': 'eng',
        'target_lang': 'zho_Hans',
        'domain': 'technology'
    },
    'q02': {
        'source': 'The Renaissance was a period of great cultural and artistic achievement in Europe.',
        'reference': '文艺复兴是欧洲文化和艺术成就辉煌的时期。',
        'source_lang': 'eng',
        'target_lang': 'zho_Hans',
        'domain': 'history'
    },
    'q03': {
        'source': '深度学习在计算机视觉领域取得了突破性进展。',
        'reference': 'Deep learning has made breakthrough progress in the field of computer vision.',
        'source_lang': 'zho_Hans',
        'target_lang': 'eng',
        'domain': 'technology'
    },
    'q04': {
        'source': 'The quick brown fox jumps over the lazy dog.',
        'reference': '敏捷的棕色狐狸跳过了懒狗。',
        'source_lang': 'eng',
        'target_lang': 'zho_Hans',
        'domain': 'general'
    },
    'q05': {
        'source': 'Climate change poses significant challenges to global sustainability.',
        'reference': '气候变化对全球可持续发展构成重大挑战。',
        'source_lang': 'eng',
        'target_lang': 'zho_Hans',
        'domain': 'environment'
    }
}
```

### 8.3 批量评估脚本

```python
# data/analize/scripts/evaluate_translation_quality.py

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))

from quality_evaluation.translation_evaluator import TranslationEvaluator
from translation_config import TRANSLATION_REFERENCES


def evaluate_translation_quality(data_dir: Path, output_dir: Path,
                                 use_bertscore: bool = True,
                                 use_comet: bool = False):
    """评估翻译任务质量"""
    
    print("\n" + "="*60)
    print("🌐 Translation Quality Evaluation")
    print("="*60)
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/translation/translation_responses.csv'
    
    if not responses_file.exists():
        print(f"❌ Error: File not found: {responses_file}")
        return None
    
    df = pd.read_csv(responses_file)
    
    print(f"\n📂 Loaded {len(df)} models")
    print(f"🌐 Questions: {len([c for c in df.columns if c != 'model'])}")
    
    # 初始化评估器
    config = {
        'use_bertscore': use_bertscore,
        'use_comet': use_comet,
        'device': 'cuda'
    }
    evaluator = TranslationEvaluator(config)
    
    print(f"\n⚙️  Configuration:")
    print(f"   - BERTScore: {'✅ Enabled' if use_bertscore else '❌ Disabled'}")
    print(f"   - COMET: {'✅ Enabled' if use_comet else '❌ Disabled'}")
    
    # 评估每个模型的每个响应
    results = []
    
    total_evaluations = len(df) * len([c for c in df.columns if c != 'model'])
    
    with tqdm(total=total_evaluations, desc="Evaluating") as pbar:
        for _, row in df.iterrows():
            model = row['model']
            
            for col in df.columns:
                if col == 'model':
                    continue
                
                response = row[col]
                
                if pd.isna(response) or len(str(response).strip()) == 0:
                    pbar.update(1)
                    continue
                
                # 获取参考译文和源文本
                ref_data = TRANSLATION_REFERENCES.get(col)
                
                if ref_data is None:
                    print(f"\n⚠️  No reference data for {col}")
                    pbar.update(1)
                    continue
                
                reference = ref_data['reference']
                source_text = ref_data['source']
                target_lang = ref_data['target_lang']
                
                # 构建上下文
                context = {
                    'source_text': source_text,
                    'source_lang': ref_data['source_lang'],
                    'target_lang': target_lang,
                    'domain': ref_data['domain']
                }
                
                # 评估质量
                scores = evaluator.evaluate(
                    str(response),
                    reference=reference,
                    context=context
                )
                
                # 保存结果
                result = {
                    'model': model,
                    'question_id': col,
                    'source_lang': ref_data['source_lang'],
                    'target_lang': target_lang,
                    'domain': ref_data['domain'],
                    **scores
                }
                results.append(result)
                
                pbar.update(1)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'translation_quality_scores.csv'
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Evaluation completed!")
    print(f"📊 Results saved to: {output_file}")
    print(f"📈 Total evaluations: {len(results_df)}")
    
    # 生成汇总统计
    generate_summary_stats(results_df, output_dir)
    
    # 生成报告
    generate_report(results_df, output_dir)
    
    return results_df


def generate_summary_stats(df: pd.DataFrame, output_dir: Path):
    """生成汇总统计"""
    
    print(f"\n📊 Generating summary statistics...")
    
    # 按模型汇总
    metric_cols = [col for col in df.columns 
                   if col not in ['model', 'question_id', 'source_lang', 
                                 'target_lang', 'domain'] 
                   and df[col].dtype in ['float64', 'int64']]
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'translation_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型
    if 'bleu_4' in df.columns:
        print(f"\n🏆 Top 3 Models by BLEU-4:")
        top_models = df.groupby('model')['bleu_4'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")
    
    if 'bertscore_f1' in df.columns:
        print(f"\n🎯 Top 3 Models by BERTScore F1:")
        top_models = df.groupby('model')['bertscore_f1'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")
    
    if 'chrf' in df.columns:
        print(f"\n📝 Top 3 Models by chrF:")
        top_models = df.groupby('model')['chrf'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")


def generate_report(df: pd.DataFrame, output_dir: Path):
    """生成评估报告"""
    
    report_file = output_dir / 'translation_quality_report.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 翻译质量评估报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. 评估概览\n\n")
        f.write(f"- 评估模型数: {df['model'].nunique()}\n")
        f.write(f"- 评估问题数: {df['question_id'].nunique()}\n")
        f.write(f"- 总评估次数: {len(df)}\n")
        f.write(f"- 语言对: 英→中 (4题), 中→英 (1题)\n\n")
        
        f.write("## 2. 核心指标排名\n\n")
        
        # BLEU-4排名
        if 'bleu_4' in df.columns:
            f.write("### 2.1 BLEU-4 排名\n\n")
            f.write("BLEU-4 是机器翻译最经典的评估指标，衡量词汇级别的匹配度。\n\n")
            bleu_ranking = df.groupby('model')['bleu_4'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(bleu_ranking.items(), 1):
                status = "✅" if score >= 0.4 else "⚠️" if score >= 0.2 else "❌"
                f.write(f"{rank}. {status} **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # chrF排名
        if 'chrf' in df.columns:
            f.write("### 2.2 chrF 排名\n\n")
            f.write("chrF 是字符级别的F分数，对中文等字符级语言更友好。\n\n")
            chrf_ranking = df.groupby('model')['chrf'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(chrf_ranking.items(), 1):
                status = "✅" if score >= 0.5 else "⚠️" if score >= 0.3 else "❌"
                f.write(f"{rank}. {status} **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # BERTScore排名
        if 'bertscore_f1' in df.columns:
            f.write("### 2.3 BERTScore F1 排名\n\n")
            f.write("BERTScore 基于语义相似度，能识别同义词和改写。\n\n")
            bert_ranking = df.groupby('model')['bertscore_f1'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(bert_ranking.items(), 1):
                status = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
                f.write(f"{rank}. {status} **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # 按语言对分析
        if 'source_lang' in df.columns and 'bleu_4' in df.columns:
            f.write("### 2.4 按语言对分析\n\n")
            lang_analysis = df.groupby(['source_lang', 'model'])['bleu_4'].mean().unstack()
            f.write("各模型在不同语言对上的BLEU-4分数：\n\n")
            f.write(lang_analysis.to_markdown())
            f.write("\n\n")
        
        f.write("## 3. 指标说明\n\n")
        f.write("### 3.1 BLEU-4\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 4-gram词汇匹配度\n")
        f.write("- **解释**: 0.4+ 优秀，0.2-0.4 良好，<0.2 需改进\n\n")
        
        f.write("### 3.2 chrF\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 字符级F分数\n")
        f.write("- **解释**: 0.5+ 优秀，0.3-0.5 良好，<0.3 需改进\n\n")
        
        f.write("### 3.3 BERTScore F1\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 语义相似度\n")
        f.write("- **解释**: 0.8+ 优秀，0.6-0.8 良好，<0.6 需改进\n\n")
        
        f.write("## 4. 详细数据\n\n")
        f.write("详细评分数据请参考:\n")
        f.write("- `translation_quality_scores.csv` - 每个模型每个问题的详细评分\n")
        f.write("- `translation_quality_summary.csv` - 按模型汇总的统计数据\n")
    
    print(f"📄 Report generated: {report_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估翻译质量')
    parser.add_argument('--data-dir', type=str,
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/translation_quality',
                       help='输出目录')
    parser.add_argument('--use-bertscore', action='store_true', default=True,
                       help='启用BERTScore（默认：是）')
    parser.add_argument('--use-comet', action='store_true', default=False,
                       help='启用COMET（默认：否，成本高）')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_translation_quality(
        data_dir,
        output_dir,
        use_bertscore=args.use_bertscore,
        use_comet=args.use_comet
    )
```


## 9. 依赖安装

### 9.1 必需依赖

```bash
# 激活环境
conda activate bartscore

# 安装基础依赖
pip install nltk pandas numpy tqdm

# 下载NLTK数据
python -c "import nltk; nltk.download('punkt')"

# 安装BERTScore（推荐）
pip install bert-score transformers torch
```

### 9.2 可选依赖

```bash
# 编辑距离计算（推荐）
pip install python-Levenshtein

# COMET评估（可选，成本高）
pip install unbabel-comet
```

### 9.3 模型下载

首次运行时会自动下载以下模型：

- **多语言BERT模型**（用于BERTScore）
  - 模型：`bert-base-multilingual-cased`
  - 大小：约700MB
  - 缓存位置：`~/.cache/huggingface/`

- **COMET模型**（可选）
  - 模型：`Unbabel/wmt22-comet-da`
  - 大小：约2GB
  - 需要GPU加速

## 10. 运行指南

### 10.1 快速开始

```bash
# 1. 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 2. 运行评估（基础指标）
cd data/analize/scripts
python evaluate_translation_quality.py

# 3. 运行评估（包含COMET）
python evaluate_translation_quality.py --use-comet

# 4. 查看结果
type ..\results\translation_quality\translation_quality_report.md
```

### 10.2 预期输出

```
data/analize/results/translation_quality/
├── translation_quality_scores.csv       # 详细评分
│   ├── model
│   ├── question_id
│   ├── source_lang
│   ├── target_lang
│   ├── domain
│   ├── bleu_1, bleu_2, bleu_4
│   ├── chrf
│   ├── bertscore_f1
│   ├── length_ratio
│   └── edit_similarity
├── translation_quality_summary.csv      # 汇总统计
└── translation_quality_report.md        # 评估报告
```

### 10.3 性能估算

基于当前硬件配置（RTX 4060 8GB）：

**不使用COMET（推荐）**：
- 每个响应评估时间：~1-2秒
- 总评估时间：~1-3分钟（12个模型 × 5个问题）
- GPU显存占用：~2GB（BERT模型）

**使用COMET（可选）**：
- 每个响应评估时间：~5-10秒
- 总评估时间：~5-10分钟
- GPU显存占用：~4-5GB（BERT + COMET模型）

## 11. 指标解释与应用

### 11.1 指标含义

#### BLEU-4
- **含义**: 4-gram词汇匹配度
- **范围**: [0, 1]
- **解释**:
  - 0.4-1.0: 优秀，词汇匹配度高
  - 0.2-0.4: 良好，基本准确
  - 0.0-0.2: 需改进，词汇匹配度低
- **应用**: 标准机器翻译评估

#### chrF
- **含义**: 字符级F分数
- **范围**: [0, 1]
- **解释**:
  - 0.5-1.0: 优秀，字符匹配度高
  - 0.3-0.5: 良好
  - 0.0-0.3: 需改进
- **应用**: 对中文等字符级语言更友好

#### BERTScore F1
- **含义**: 语义相似度
- **范围**: [0, 1]
- **解释**:
  - 0.8-1.0: 优秀，语义高度相似
  - 0.6-0.8: 良好，语义较相似
  - 0.0-0.6: 需改进，语义差异较大
- **应用**: 评估语义正确性，对同义词友好

#### 长度比
- **含义**: 译文长度/源文长度
- **范围**: [0, +∞)
- **解释**:
  - 英→中: 通常 0.6-0.9（中文更简洁）
  - 中→英: 通常 1.2-1.8（英文更冗长）
  - 偏离过大可能表示遗漏或过度翻译
- **应用**: 检测完整性

### 11.2 综合评分建议

#### 方案1：加权平均
```python
def calculate_translation_score(metrics):
    """计算翻译综合分数"""
    score = (
        0.30 * metrics['bleu_4'] +
        0.30 * metrics['chrf'] +
        0.30 * metrics['bertscore_f1'] +
        0.10 * (1 - abs(metrics['length_ratio'] - 1.0))  # 长度合理性
    )
    return score
```

#### 方案2：多维度呈现（推荐）
保留所有原始指标，支持不同应用场景的灵活分析


## 12. 总结

### 12.1 方法可行性总结

| 方法 | 可行性 | 推荐度 | 理由 |
|------|--------|--------|------|
| **BLEU-1/2/4** | ✅ 高 | ⭐⭐⭐ | 经典标准、计算快、广泛认可 |
| **chrF++** | ✅ 高 | ⭐⭐⭐ | 字符级友好、对中文更适用 |
| **BERTScore** | ✅ 高 | ⭐⭐⭐ | 语义评估、对改写友好 |
| **长度比** | ✅ 高 | ⭐⭐ | 简单有效、检测完整性 |
| **编辑距离** | ✅ 高 | ⭐⭐ | 辅助指标、易于计算 |
| **COMET** | ⚠️ 中 | ⭐ | 效果最好但成本极高 |
| **LLM-as-Judge** | ⚠️ 中 | ⭐ | 最接近人类但需API |

### 12.2 最终推荐方案

#### 核心指标组合（必须实现）
- **BLEU-4**（词汇匹配，机器翻译标准）
- **chrF++**（字符匹配，中文友好）
- **BERTScore**（语义相似度，改写友好）
- **长度比**（完整性检查）

#### 可选扩展（资源充足时）
- **COMET**（最高质量评估，需GPU）
- **LLM-as-Judge**（人工验证，抽样使用）

### 12.3 实施建议

#### 阶段1：基础实现（1-2天）
1. ✅ 创建参考译文配置
2. ✅ 实现BLEU计算
3. ✅ 实现chrF计算
4. ✅ 批量评估脚本
5. ✅ 结果保存和汇总

#### 阶段2：语义评估（1-2天）
1. ⏳ 集成BERTScore
2. ⏳ 模型下载和缓存管理
3. ⏳ GPU加速优化
4. ⏳ 错误处理和日志

#### 阶段3：高级评估（可选，2-3天）
1. ⏳ 集成COMET
2. ⏳ 实现LLM-as-Judge
3. ⏳ 可视化分析

### 12.4 预期成果

- 识别翻译质量最高的模型
- 分析不同语言对的翻译难度
- 评估词汇、字符、语义三个层面的质量
- 为模型选择提供数据支持

### 12.5 与其他任务的对比

| 维度 | 代码生成 | 创意写作 | 数学推理 | 问答 | 摘要 | 翻译 |
|------|---------|---------|---------|------|------|------|
| **核心指标** | Pass@k | Distinct-N | Exact Match | F1 | ROUGE | BLEU |
| **评估难度** | 高 | 中 | 中 | 中 | 高 | 中 |
| **需要参考** | 否 | 否 | 是 | 是 | 是 | 是 |
| **需要外部模型** | 否 | 可选 | 否 | 可选 | 可选 | 可选 |
| **计算成本** | 低 | 中 | 低 | 中 | 高 | 中 |
| **主观性** | 低 | 中 | 低 | 低 | 中 | 中 |

### 12.6 翻译任务的特点

**优势**：
- ✅ 评估方法成熟（BLEU等经典指标）
- ✅ 有明确的参考标准
- ✅ 多层次评估（词汇、字符、语义）
- ✅ 工业界广泛应用

**挑战**：
- ⚠️ 需要创建参考译文
- ⚠️ 同一源文本可能有多种正确译法
- ⚠️ 语言对差异（英中 vs 中英）
- ⚠️ 领域专业性（科技、历史等）

## 13. 参考文献

1. Papineni, K., et al. (2002). "BLEU: a Method for Automatic Evaluation of Machine Translation." ACL.
2. Popović, M. (2015). "chrF: character n-gram F-score for automatic MT evaluation." WMT.
3. Zhang, T., et al. (2020). "BERTScore: Evaluating Text Generation with BERT." ICLR.
4. Rei, R., et al. (2020). "COMET: A Neural Framework for MT Evaluation." EMNLP.
5. Freitag, M., et al. (2021). "Experts, Errors, and Context: A Large-Scale Study of Human Evaluation for Machine Translation." TACL.

## 14. 附录

### 14.1 常见问题

**Q1: 为什么需要参考译文？**
A: BLEU、chrF、BERTScore等指标都需要参考译文来计算相似度。可以使用人工翻译、商业API或最佳模型输出作为参考。

**Q2: BLEU分数多高算好？**
A: 一般来说，BLEU-4 > 0.4为优秀，0.2-0.4为良好，<0.2需要改进。但不同语言对和领域的标准可能不同。

**Q3: 为什么chrF对中文更友好？**
A: chrF基于字符级别匹配，不需要分词，对中文等字符级语言更稳定。BLEU需要分词，中文分词可能引入误差。

**Q4: BERTScore和BLEU有什么区别？**
A: BLEU基于表面词汇匹配，BERTScore基于语义相似度。BERTScore能识别同义词和改写，更接近人类判断。

**Q5: 是否需要使用COMET？**
A: COMET是目前最接近人类评分的自动指标，但计算成本高。如果资源充足且需要最高质量评估，可以使用。

### 14.2 工具链接

- **NLTK**: https://www.nltk.org/
- **BERTScore**: https://github.com/Tiiiger/bert_score
- **COMET**: https://github.com/Unbabel/COMET
- **SacreBLEU**: https://github.com/mjpost/sacrebleu

---

**文档版本**: v1.0  
**创建日期**: 2026-03-05  
**作者**: Kiro AI Assistant  
**状态**: 设计完成，待实施

