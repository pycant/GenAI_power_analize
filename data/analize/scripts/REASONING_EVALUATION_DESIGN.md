# 逻辑推理任务 (Reasoning) 质量评估方法设计

## 1. 评估目标

评估模型在逻辑推理任务中的**正确性、逻辑性、严谨性与可解释性**。

## 2. 数据特征分析

### 2.1 任务类型

基于提供的推理问题，任务类型为：
- **逻辑谜题 (Logic Puzzles)**: q01, q03 - 需要逻辑推理和策略思考
- **演绎推理 (Deductive Reasoning)**: q02, q04 - 基于前提推导结论
- **博弈论推理 (Game Theory)**: q05 - 需要策略分析和多步推理

### 2.2 标准答案

| 问题ID | 问题类型 | 标准答案 | 推理要点 |
|--------|----------|----------|----------|
| q01 | 逻辑谜题 | 从标签"一金一银"的盒子取硬币 | 利用标签错误信息推断 |
| q02 | 演绎推理 | 是，小花需要呼吸 | 三段论：猫→哺乳动物→需要呼吸 |
| q03 | 逻辑谜题 | 利用灯泡温度状态 | 开关1开后关(热)，开关2开(亮)，开关3不动(冷) |
| q04 | 演绎推理 | 小红更高 | 传递性：小红>小明>小刚 → 小红>小刚 |
| q05 | 博弈论 | 1号海盗提案：97,0,1,0,2或97,0,1,2,0 | 逆向归纳法 |

### 2.3 评估挑战

- **无唯一标准答案**: 部分问题可能有多种合理解法
- **推理过程重要性**: 答案正确但推理错误不应得高分
- **长文本输出**: 模型通常输出详细的思考过程
- **主观性**: 逻辑严谨性和完整性难以量化

## 3. 核心指标

### 3.1 结论正确性 (Conclusion Correctness) ✅ 高度可行

**定义**：
- 提取的最终结论与标准答案是否一致
- 类似于QA任务的Exact Match

**实现方案**：
```python
def calculate_conclusion_correctness(generated: str, reference: str) -> float:
    """
    计算结论正确性
    
    Args:
        generated: 生成的推理文本
        reference: 标准答案
    
    Returns:
        float: 1.0 (正确) 或 0.0 (错误)
    """
    # 提取最终结论
    conclusion = extract_conclusion(generated)
    
    # 归一化比较
    gen_normalized = normalize_answer(conclusion)
    ref_normalized = normalize_answer(reference)
    
    # 检查是否包含关键信息
    if ref_normalized in gen_normalized or gen_normalized in ref_normalized:
        return 1.0
    
    # 使用F1分数作为软匹配
    f1 = calculate_f1_score(conclusion, reference)
    return 1.0 if f1 > 0.7 else 0.0
```

**优势**：
- ✅ 评估标准明确
- ✅ 无需外部模型
- ✅ 计算快速

**挑战**：
- ⚠️ 需要准确提取结论
- ⚠️ 需要处理不同表述方式


### 3.2 推理步骤完整性 (Reasoning Completeness) ✅ 高度可行

**定义**：
- 评估推理过程是否包含必要的步骤
- 检测推理链的完整性

**计算方法**：
1. 检测推理关键词（首先、然后、因此等）
2. 统计推理步骤数量
3. 检测逻辑连接词
4. 评估是否有明确的前提和结论

**实现方案**：
```python
def calculate_reasoning_completeness(text: str) -> Dict[str, float]:
    """
    评估推理完整性
    
    Returns:
        Dict with:
        - has_premise: 是否包含前提
        - has_reasoning_steps: 是否包含推理步骤
        - has_conclusion: 是否包含结论
        - step_count: 推理步骤数量
        - completeness_score: 综合完整性得分
    """
    scores = {}
    
    # 1. 检测前提关键词
    premise_keywords = [
        'given', 'assume', 'suppose', 'if', 'premise',
        '假设', '已知', '前提', '如果', '条件'
    ]
    has_premise = any(kw in text.lower() for kw in premise_keywords)
    scores['has_premise'] = 1.0 if has_premise else 0.0
    
    # 2. 检测推理关键词
    reasoning_keywords = [
        'first', 'then', 'next', 'because', 'since', 'therefore', 'thus',
        '首先', '然后', '接下来', '因为', '由于', '所以', '因此'
    ]
    reasoning_count = sum(1 for kw in reasoning_keywords if kw in text.lower())
    scores['has_reasoning_steps'] = 1.0 if reasoning_count > 0 else 0.0
    scores['reasoning_keyword_count'] = reasoning_count
    
    # 3. 检测结论关键词
    conclusion_keywords = [
        'therefore', 'thus', 'hence', 'so', 'conclusion', 'answer',
        '因此', '所以', '综上', '结论', '答案'
    ]
    has_conclusion = any(kw in text.lower() for kw in conclusion_keywords)
    scores['has_conclusion'] = 1.0 if has_conclusion else 0.0
    
    # 4. 统计推理步骤（基于句子分割）
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    scores['step_count'] = len(sentences)
    
    # 5. 综合完整性得分
    completeness = (
        scores['has_premise'] * 0.3 +
        scores['has_reasoning_steps'] * 0.4 +
        scores['has_conclusion'] * 0.3
    )
    scores['completeness_score'] = completeness
    
    return scores
```

**优势**：
- ✅ 评估推理过程质量
- ✅ 无需外部模型
- ✅ 可解释性强

**范围**: [0, 1]

### 3.3 逻辑连贯性 (Logical Coherence) ✅ 可行

**定义**：
- 评估推理步骤之间的逻辑连贯性
- 检测是否存在逻辑跳跃或矛盾

**实现方案**：
```python
def calculate_logical_coherence(text: str) -> Dict[str, float]:
    """
    评估逻辑连贯性
    
    Returns:
        Dict with:
        - has_logical_connectors: 是否包含逻辑连接词
        - connector_density: 逻辑连接词密度
        - coherence_score: 连贯性得分
    """
    scores = {}
    
    # 1. 逻辑连接词
    logical_connectors = [
        'because', 'since', 'therefore', 'thus', 'hence', 'so',
        'if', 'then', 'when', 'while', 'although', 'however',
        '因为', '由于', '所以', '因此', '如果', '那么', '当', '虽然', '但是'
    ]
    
    connector_count = sum(1 for conn in logical_connectors if conn in text.lower())
    word_count = len(text.split())
    
    scores['has_logical_connectors'] = 1.0 if connector_count > 0 else 0.0
    scores['connector_density'] = connector_count / word_count if word_count > 0 else 0.0
    
    # 2. 连贯性得分（基于连接词密度）
    # 理想密度：每50-100个词有1个连接词
    ideal_density = 0.01  # 1%
    actual_density = scores['connector_density']
    
    # 使用高斯函数评分
    import math
    coherence = math.exp(-((actual_density - ideal_density) ** 2) / (2 * 0.005 ** 2))
    scores['coherence_score'] = coherence
    
    return scores
```

**优势**：
- ✅ 量化逻辑连贯性
- ✅ 无需外部模型
- ✅ 计算简单

**范围**: [0, 1]


## 4. 辅助指标

### 4.1 推理深度 (Reasoning Depth) ✅ 可行

**定义**：
- 评估推理的深度和复杂度
- 衡量多步推理的层次

**实现方案**：
```python
def calculate_reasoning_depth(text: str) -> Dict[str, float]:
    """
    评估推理深度
    
    Returns:
        Dict with:
        - sentence_count: 句子数量
        - avg_sentence_length: 平均句子长度
        - depth_score: 深度得分
    """
    scores = {}
    
    # 1. 句子数量
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    scores['sentence_count'] = len(sentences)
    
    # 2. 平均句子长度
    if sentences:
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        scores['avg_sentence_length'] = avg_length
    else:
        scores['avg_sentence_length'] = 0.0
    
    # 3. 深度得分（基于句子数量和长度）
    # 理想：5-10个句子，每句10-20个词
    sentence_score = min(1.0, scores['sentence_count'] / 7.0)
    length_score = min(1.0, scores['avg_sentence_length'] / 15.0)
    
    scores['depth_score'] = (sentence_score + length_score) / 2
    
    return scores
```

**优势**：
- ✅ 评估推理复杂度
- ✅ 简单直观

**范围**: [0, 1]

### 4.2 关键词覆盖 (Keyword Coverage) ✅ 可行

**定义**：
- 评估是否包含问题相关的关键词
- 检测推理是否切题

**实现方案**：
```python
def calculate_keyword_coverage(text: str, question: str) -> float:
    """
    计算关键词覆盖率
    
    Args:
        text: 生成的推理文本
        question: 原始问题
    
    Returns:
        float: 关键词覆盖率 [0, 1]
    """
    # 提取问题中的关键词（去除停用词）
    stopwords = {'的', '是', '在', '有', '和', '了', '吗', '呢', '请', '问',
                 'the', 'is', 'are', 'a', 'an', 'and', 'or', 'but', 'in', 'on'}
    
    question_words = set(question.lower().split()) - stopwords
    text_words = set(text.lower().split())
    
    if not question_words:
        return 1.0
    
    # 计算覆盖率
    covered = question_words & text_words
    coverage = len(covered) / len(question_words)
    
    return coverage
```

**优势**：
- ✅ 检测推理相关性
- ✅ 防止答非所问

**范围**: [0, 1]

### 4.3 答案提取置信度 (Extraction Confidence) ✅ 可行

**定义**：
- 评估答案提取的可靠性
- 检测答案的明确性

**实现方案**：
```python
def calculate_extraction_confidence(text: str) -> float:
    """
    评估答案提取置信度
    
    Returns:
        float: 置信度 [0, 1]
    """
    # 检测明确的答案标记
    answer_markers = [
        'answer is', 'the answer', 'conclusion is', 'therefore',
        '答案是', '结论是', '因此', '所以'
    ]
    
    has_marker = any(marker in text.lower() for marker in answer_markers)
    
    if has_marker:
        return 1.0
    
    # 检测最后一句是否像答案
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
    if sentences:
        last_sentence = sentences[-1]
        # 短句子更可能是答案
        if len(last_sentence.split()) < 20:
            return 0.7
    
    return 0.3
```

**优势**：
- ✅ 评估答案明确性
- ✅ 辅助答案提取

**范围**: [0, 1]


## 5. 高级评估方法（可选）

### 5.1 LLM-as-Judge (模型打分法) ⚠️ 成本高但效果好

**定义**：
- 使用大型语言模型（如GPT-4）作为评判者
- 对推理质量进行多维度打分

**评估维度**：
1. **正确性 (Correctness)**: 最终答案是否正确
2. **逻辑性 (Logic)**: 推理步骤是否自洽、无矛盾
3. **严谨性 (Rigor)**: 是否有幻觉、错误前提
4. **完整性 (Completeness)**: 是否缺少关键步骤
5. **可解释性 (Explainability)**: 推理链是否清晰

**Prompt模板**：
```
你是专业的逻辑推理评估专家，请严格按下面维度评分（1-5分）。

任务：
问题：{question}
标准答案：{reference}
模型输出：{generation}

评估维度：
1. 最终答案是否正确 (1-5分)
2. 推理步骤是否完整 (1-5分)
3. 推理逻辑是否严谨、无矛盾 (1-5分)
4. 是否存在幻觉、错误前提 (1-5分，越低越好)
5. 整体推理质量 (1-5分)

输出格式（JSON）：
{
  "correctness": <1-5>,
  "completeness": <1-5>,
  "logic": <1-5>,
  "rigor": <5-1>,  # 反向评分
  "overall": <1-5>,
  "total_score": <总分/25>,
  "is_correct": <true/false>,
  "feedback": "<简短评语>",
  "errors": "<错误点，如有>"
}
```

**实现方案**：
```python
def evaluate_with_llm_judge(question: str, generated: str, 
                           reference: str, model: str = "gpt-4") -> Dict:
    """
    使用LLM作为评判者
    
    Args:
        question: 原始问题
        generated: 生成的推理文本
        reference: 标准答案
        model: 评判模型名称
    
    Returns:
        Dict: 多维度评分
    """
    import openai
    
    prompt = f"""你是专业的逻辑推理评估专家，请严格按下面维度评分（1-5分）。

任务：
问题：{question}
标准答案：{reference}
模型输出：{generated}

评估维度：
1. 最终答案是否正确 (1-5分)
2. 推理步骤是否完整 (1-5分)
3. 推理逻辑是否严谨、无矛盾 (1-5分)
4. 是否存在幻觉、错误前提 (1-5分，越低越好)
5. 整体推理质量 (1-5分)

输出格式（JSON）：
{{
  "correctness": <1-5>,
  "completeness": <1-5>,
  "logic": <1-5>,
  "rigor": <5-1>,
  "overall": <1-5>,
  "total_score": <总分/25>,
  "is_correct": <true/false>,
  "feedback": "<简短评语>",
  "errors": "<错误点，如有>"
}}
"""
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"⚠️  LLM-as-Judge failed: {e}")
        return None
```

**优势**：
- ✅ 最接近人类评估
- ✅ 能评估复杂的逻辑问题
- ✅ 提供详细反馈

**劣势**：
- ⚠️ 需要API调用（成本高）
- ⚠️ 评估速度慢
- ⚠️ 需要网络连接

**建议**：
- 作为可选的高级评估方法
- 用于验证自动评估结果
- 用于生成训练数据

### 5.2 Self-Consistency (自洽性检测) ⚠️ 需要多次采样

**定义**：
- 对同一问题采样多次
- 选择最多数答案
- 提高评估鲁棒性

**实现方案**：
```python
def evaluate_self_consistency(question: str, model, n_samples: int = 5) -> Dict:
    """
    自洽性评估
    
    Args:
        question: 问题
        model: 生成模型
        n_samples: 采样次数
    
    Returns:
        Dict: 包含最多数答案和一致性得分
    """
    from collections import Counter
    
    # 生成多个答案
    answers = []
    for _ in range(n_samples):
        response = model.generate(question)
        answer = extract_conclusion(response)
        answers.append(answer)
    
    # 统计最多数答案
    answer_counts = Counter(answers)
    most_common_answer, count = answer_counts.most_common(1)[0]
    
    # 计算一致性得分
    consistency_score = count / n_samples
    
    return {
        'most_common_answer': most_common_answer,
        'consistency_score': consistency_score,
        'all_answers': answers,
        'answer_distribution': dict(answer_counts)
    }
```

**优势**：
- ✅ 提高评估鲁棒性
- ✅ 检测模型稳定性

**劣势**：
- ⚠️ 需要多次推理（成本高）
- ⚠️ 评估时间长


## 6. 推荐评估方案

### 6.1 核心指标组合

| 维度 | 指标 | 优先级 | 计算成本 | 可行性 |
|------|------|--------|----------|--------|
| 正确性 | 结论正确性 | ⭐⭐⭐ | 低 | ✅ 高 |
| 完整性 | 推理步骤完整性 | ⭐⭐⭐ | 低 | ✅ 高 |
| 连贯性 | 逻辑连贯性 | ⭐⭐ | 低 | ✅ 高 |
| 深度 | 推理深度 | ⭐⭐ | 低 | ✅ 高 |
| 相关性 | 关键词覆盖 | ⭐⭐ | 低 | ✅ 高 |
| 明确性 | 答案提取置信度 | ⭐ | 低 | ✅ 高 |
| 综合 | LLM-as-Judge | ⭐ | 极高 | ⚠️ 中 |

### 6.2 评估流程

```
1. 基础检查
   ├── 提取生成文本
   ├── 加载标准答案
   └── 检查文本长度

2. 核心指标计算
   ├── 结论正确性（最重要）
   ├── 推理步骤完整性
   └── 逻辑连贯性

3. 辅助指标计算
   ├── 推理深度
   ├── 关键词覆盖
   └── 答案提取置信度

4. 可选高级评估
   └── LLM-as-Judge（如果资源充足）

5. 结果汇总
   ├── 按模型汇总平均分数
   ├── 按问题类型分析难度
   └── 生成评估报告
```

### 6.3 评分权重建议

#### 方案1：正确性优先（推荐）
```python
reasoning_quality_score = {
    'conclusion_correctness': 0.40,      # 40% - 结论正确性
    'completeness_score': 0.25,          # 25% - 推理完整性
    'coherence_score': 0.20,             # 20% - 逻辑连贯性
    'depth_score': 0.10,                 # 10% - 推理深度
    'keyword_coverage': 0.05             # 5% - 关键词覆盖
}
```

**理由**: 推理任务的核心是得出正确结论，推理过程次之

#### 方案2：过程与结果并重
```python
reasoning_quality_score = {
    'conclusion_correctness': 0.30,
    'completeness_score': 0.30,
    'coherence_score': 0.25,
    'depth_score': 0.10,
    'keyword_coverage': 0.05
}
```

#### 方案3：多维度呈现（强烈推荐）
不计算单一综合分数，保留所有原始指标：
```python
reasoning_quality_metrics = {
    'correctness': {
        'conclusion_correct': bool,
        'conclusion_f1': float
    },
    'completeness': {
        'has_premise': float,
        'has_reasoning_steps': float,
        'has_conclusion': float,
        'step_count': int,
        'completeness_score': float
    },
    'coherence': {
        'has_logical_connectors': float,
        'connector_density': float,
        'coherence_score': float
    },
    'depth': {
        'sentence_count': int,
        'avg_sentence_length': float,
        'depth_score': float
    },
    'relevance': {
        'keyword_coverage': float,
        'extraction_confidence': float
    }
}
```

**理由**: 保留完整信息，支持多角度分析，避免主观权重

## 7. 实现方案

### 7.1 评估器设计

```python
# data/analize/scripts/quality_evaluation/reasoning_evaluator.py

from typing import Dict, Optional
from .base_evaluator import BaseEvaluator


class ReasoningEvaluator(BaseEvaluator):
    """逻辑推理任务评估器"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.use_llm_judge = config.get('use_llm_judge', False) if config else False
        self.llm_model = config.get('llm_model', 'gpt-4') if config else 'gpt-4'
    
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict = None) -> Dict[str, float]:
        """
        评估推理质量
        
        Args:
            generated: 生成的推理文本
            reference: 标准答案（必需）
            context: 额外上下文（可包含原始问题）
        
        Returns:
            Dict[str, float]: 多维度指标
        """
        scores = {}
        
        # 基础检查
        if not generated or not reference:
            return self._get_zero_scores()
        
        # 1. 结论正确性
        conclusion_scores = self._calculate_conclusion_correctness(
            generated, reference
        )
        scores.update(conclusion_scores)
        
        # 2. 推理完整性
        completeness_scores = self._calculate_reasoning_completeness(generated)
        scores.update(completeness_scores)
        
        # 3. 逻辑连贯性
        coherence_scores = self._calculate_logical_coherence(generated)
        scores.update(coherence_scores)
        
        # 4. 推理深度
        depth_scores = self._calculate_reasoning_depth(generated)
        scores.update(depth_scores)
        
        # 5. 关键词覆盖（如果有原始问题）
        if context and 'question' in context:
            scores['keyword_coverage'] = self._calculate_keyword_coverage(
                generated, context['question']
            )
        else:
            scores['keyword_coverage'] = None
        
        # 6. 答案提取置信度
        scores['extraction_confidence'] = self._calculate_extraction_confidence(
            generated
        )
        
        # 7. LLM-as-Judge（可选）
        if self.use_llm_judge and context and 'question' in context:
            llm_scores = self._evaluate_with_llm_judge(
                context['question'], generated, reference
            )
            if llm_scores:
                scores.update({f'llm_{k}': v for k, v in llm_scores.items()})
        
        return scores
```


### 7.2 标准答案配置

```python
# data/analize/scripts/reasoning_config.py

# 标准答案配置
REASONING_REFERENCE_ANSWERS = {
    'q01': {
        'answer': '从标签"一金一银"的盒子中取硬币',
        'key_points': ['标签错误', '一金一银', '推断其他盒子'],
        'reasoning_type': 'logic_puzzle'
    },
    'q02': {
        'answer': '是，小花需要呼吸',
        'key_points': ['三段论', '猫是哺乳动物', '哺乳动物需要呼吸'],
        'reasoning_type': 'deductive'
    },
    'q03': {
        'answer': '利用灯泡的温度状态：开关1开后关(热)，开关2开(亮)，开关3不动(冷)',
        'key_points': ['温度', '开关1热', '开关2亮', '开关3冷'],
        'reasoning_type': 'logic_puzzle'
    },
    'q04': {
        'answer': '小红更高',
        'key_points': ['传递性', '小红>小明', '小明>小刚', '小红>小刚'],
        'reasoning_type': 'deductive'
    },
    'q05': {
        'answer': '1号海盗提案：97,0,1,0,2 或 97,0,1,2,0',
        'key_points': ['逆向归纳', '博弈论', '最小化分配', '保证通过'],
        'reasoning_type': 'game_theory'
    }
}
```

### 7.3 批量评估脚本

```python
# data/analize/scripts/evaluate_reasoning_quality.py

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from quality_evaluation.reasoning_evaluator import ReasoningEvaluator
from reasoning_config import REASONING_REFERENCE_ANSWERS


def evaluate_reasoning_quality(data_dir: Path, output_dir: Path,
                               use_llm_judge: bool = False):
    """评估逻辑推理任务质量"""
    
    print("\n" + "="*60)
    print("🧠 Reasoning Quality Evaluation")
    print("="*60)
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/reasoning/reasoning_responses.csv'
    prompts_file = data_dir / 'comparison_matrices/reasoning/reasoning_prompts.csv'
    
    if not responses_file.exists():
        print(f"❌ Error: File not found: {responses_file}")
        return None
    
    df_responses = pd.read_csv(responses_file)
    df_prompts = pd.read_csv(prompts_file)
    
    print(f"\n📂 Loaded {len(df_responses)} models")
    print(f"🧠 Questions: {len([c for c in df_responses.columns if c != 'model'])}")
    
    # 初始化评估器
    config = {
        'use_llm_judge': use_llm_judge,
        'llm_model': 'gpt-4'
    }
    evaluator = ReasoningEvaluator(config)
    
    print(f"\n⚙️  Configuration:")
    print(f"   - LLM-as-Judge: {'✅ Enabled' if use_llm_judge else '❌ Disabled'}")
    
    # 评估每个模型的每个响应
    results = []
    
    total_evaluations = len(df_responses) * len([c for c in df_responses.columns if c != 'model'])
    
    with tqdm(total=total_evaluations, desc="Evaluating") as pbar:
        for _, row in df_responses.iterrows():
            model = row['model']
            
            for col in df_responses.columns:
                if col == 'model':
                    continue
                
                response = row[col]
                
                if pd.isna(response) or len(str(response).strip()) == 0:
                    pbar.update(1)
                    continue
                
                # 获取标准答案和问题
                ref_data = REASONING_REFERENCE_ANSWERS.get(col)
                question_row = df_prompts[df_prompts['question_id'] == col]
                
                if ref_data is None or question_row.empty:
                    print(f"\n⚠️  No reference data for {col}")
                    pbar.update(1)
                    continue
                
                reference = ref_data['answer']
                question = question_row['prompt'].values[0]
                
                # 构建上下文
                context = {
                    'question': question,
                    'reasoning_type': ref_data['reasoning_type'],
                    'key_points': ref_data['key_points']
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
                    'reasoning_type': ref_data['reasoning_type'],
                    **scores
                }
                results.append(result)
                
                pbar.update(1)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'reasoning_quality_scores.csv'
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
                   if col not in ['model', 'question_id', 'reasoning_type'] 
                   and df[col].dtype in ['float64', 'int64']]
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'reasoning_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型
    if 'conclusion_correct' in df.columns:
        print(f"\n🏆 Top 3 Models by Conclusion Correctness:")
        top_models = df.groupby('model')['conclusion_correct'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.2%}")
    
    if 'completeness_score' in df.columns:
        print(f"\n📝 Top 3 Models by Reasoning Completeness:")
        top_models = df.groupby('model')['completeness_score'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")


def generate_report(df: pd.DataFrame, output_dir: Path):
    """生成评估报告"""
    
    report_file = output_dir / 'reasoning_quality_report.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 逻辑推理质量评估报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. 评估概览\n\n")
        f.write(f"- 评估模型数: {df['model'].nunique()}\n")
        f.write(f"- 评估问题数: {df['question_id'].nunique()}\n")
        f.write(f"- 总评估次数: {len(df)}\n\n")
        
        f.write("## 2. 核心指标排名\n\n")
        
        # 结论正确性排名
        if 'conclusion_correct' in df.columns:
            f.write("### 2.1 结论正确性排名\n\n")
            f.write("结论正确性衡量最终答案是否正确。\n\n")
            correctness_ranking = df.groupby('model')['conclusion_correct'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(correctness_ranking.items(), 1):
                status = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
                f.write(f"{rank}. {status} **{model}**: {score:.2%}\n")
            f.write("\n")
        
        # 推理完整性排名
        if 'completeness_score' in df.columns:
            f.write("### 2.2 推理完整性排名\n\n")
            f.write("推理完整性衡量推理过程是否包含前提、步骤和结论。\n\n")
            completeness_ranking = df.groupby('model')['completeness_score'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(completeness_ranking.items(), 1):
                status = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
                f.write(f"{rank}. {status} **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # 逻辑连贯性排名
        if 'coherence_score' in df.columns:
            f.write("### 2.3 逻辑连贯性排名\n\n")
            f.write("逻辑连贯性衡量推理步骤之间的连贯性。\n\n")
            coherence_ranking = df.groupby('model')['coherence_score'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(coherence_ranking.items(), 1):
                f.write(f"{rank}. **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # 按推理类型分析
        if 'reasoning_type' in df.columns and 'conclusion_correct' in df.columns:
            f.write("### 2.4 按推理类型分析\n\n")
            type_analysis = df.groupby(['reasoning_type', 'model'])['conclusion_correct'].mean().unstack()
            f.write("各模型在不同推理类型上的正确率：\n\n")
            f.write(type_analysis.to_markdown())
            f.write("\n\n")
        
        f.write("## 3. 指标说明\n\n")
        f.write("### 3.1 结论正确性\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 最终结论是否正确\n")
        f.write("- **解释**: 1.0 完全正确，0.0 完全错误\n\n")
        
        f.write("### 3.2 推理完整性\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 推理过程是否包含前提、步骤和结论\n")
        f.write("- **解释**: 0.8+ 优秀，0.6-0.8 良好，<0.6 需改进\n\n")
        
        f.write("### 3.3 逻辑连贯性\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 推理步骤之间的逻辑连贯性\n")
        f.write("- **解释**: 基于逻辑连接词密度评估\n\n")
        
        f.write("## 4. 详细数据\n\n")
        f.write("详细评分数据请参考:\n")
        f.write("- `reasoning_quality_scores.csv` - 每个模型每个问题的详细评分\n")
        f.write("- `reasoning_quality_summary.csv` - 按模型汇总的统计数据\n")
    
    print(f"📄 Report generated: {report_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估逻辑推理质量')
    parser.add_argument('--data-dir', type=str,
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/reasoning_quality',
                       help='输出目录')
    parser.add_argument('--use-llm-judge', action='store_true',
                       help='启用LLM-as-Judge（需要API，评估较慢）')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_reasoning_quality(
        data_dir,
        output_dir,
        use_llm_judge=args.use_llm_judge
    )
```

## 8. 依赖安装

### 8.1 必需依赖

```bash
# 激活环境
conda activate bartscore

# 基础依赖（已安装）
pip install pandas numpy tqdm
```

### 8.2 可选依赖（LLM-as-Judge）

```bash
# 如果需要使用LLM-as-Judge
pip install openai
# 或使用其他LLM API
```

## 9. 运行指南

### 9.1 快速开始

```bash
# 1. 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 2. 运行评估（基础指标）
cd data/analize/scripts
python evaluate_reasoning_quality.py

# 3. 运行评估（包含LLM-as-Judge）
python evaluate_reasoning_quality.py --use-llm-judge

# 4. 查看结果
type ..\results\reasoning_quality\reasoning_quality_report.md
```

### 9.2 预期输出

```
data/analize/results/reasoning_quality/
├── reasoning_quality_scores.csv       # 详细评分
│   ├── model
│   ├── question_id
│   ├── reasoning_type
│   ├── conclusion_correct
│   ├── completeness_score
│   ├── coherence_score
│   ├── depth_score
│   └── keyword_coverage
├── reasoning_quality_summary.csv      # 汇总统计
└── reasoning_quality_report.md        # 评估报告
```

### 9.3 性能估算

基于当前硬件配置（RTX 4060 8GB）：

**不使用LLM-as-Judge（推荐）**：
- 每个响应评估时间：~0.1-0.5秒
- 总评估时间：~30秒-1分钟（12个模型 × 5个问题）
- 无需GPU

**使用LLM-as-Judge（可选）**：
- 每个响应评估时间：~5-10秒
- 总评估时间：~5-10分钟
- 需要API调用（成本约$0.01-0.05/评估）

## 10. 指标解释与应用

### 10.1 指标含义

#### 结论正确性
- **含义**: 最终答案是否正确
- **范围**: [0, 1]
- **解释**:
  - 1.0: 完全正确
  - 0.0: 完全错误
- **应用**: 评估推理的最终效果

#### 推理完整性
- **含义**: 推理过程是否包含前提、步骤和结论
- **范围**: [0, 1]
- **解释**:
  - 0.8-1.0: 推理完整，结构清晰
  - 0.6-0.8: 推理较完整
  - 0.0-0.6: 推理不完整，缺少关键步骤
- **应用**: 评估推理过程的质量

#### 逻辑连贯性
- **含义**: 推理步骤之间的逻辑连贯性
- **范围**: [0, 1]
- **解释**: 基于逻辑连接词密度评估
- **应用**: 评估推理的流畅性

### 10.2 综合评分建议

#### 方案1：加权平均
```python
def calculate_reasoning_score(metrics):
    """计算推理综合分数"""
    score = (
        0.40 * metrics['conclusion_correct'] +
        0.25 * metrics['completeness_score'] +
        0.20 * metrics['coherence_score'] +
        0.10 * metrics['depth_score'] +
        0.05 * metrics['keyword_coverage']
    )
    return score
```

#### 方案2：多维度呈现（推荐）
保留所有原始指标，支持不同应用场景的灵活分析

## 11. 总结

### 11.1 方法可行性总结

| 方法 | 可行性 | 推荐度 | 理由 |
|------|--------|--------|------|
| **结论正确性** | ✅ 高 | ⭐⭐⭐ | 核心指标、计算快、效果好 |
| **推理完整性** | ✅ 高 | ⭐⭐⭐ | 评估过程质量、无需外部模型 |
| **逻辑连贯性** | ✅ 高 | ⭐⭐ | 量化连贯性、简单有效 |
| **推理深度** | ✅ 高 | ⭐⭐ | 评估复杂度、辅助指标 |
| **关键词覆盖** | ✅ 高 | ⭐⭐ | 检测相关性、防止答非所问 |
| **LLM-as-Judge** | ⚠️ 中 | ⭐ | 效果最好但成本极高 |

### 11.2 最终推荐方案

#### 核心指标组合（必须实现）
- 结论正确性（最重要）
- 推理完整性（评估过程）
- 逻辑连贯性（评估流畅性）
- 推理深度（评估复杂度）
- 关键词覆盖（评估相关性）

#### 可选扩展（资源充足时）
- LLM-as-Judge（最高质量评估）
- Self-Consistency（鲁棒性评估）

### 11.3 实施建议

#### 阶段1：基础实现（1-2天）
1. ✅ 实现结论正确性计算
2. ✅ 实现推理完整性评估
3. ✅ 批量评估脚本
4. ✅ 结果保存和汇总

#### 阶段2：辅助指标（1天）
1. ⏳ 实现逻辑连贯性评估
2. ⏳ 实现推理深度评估
3. ⏳ 实现关键词覆盖
4. ⏳ 错误处理和日志

#### 阶段3：高级评估（可选，2-3天）
1. ⏳ 集成LLM-as-Judge
2. ⏳ 实现Self-Consistency
3. ⏳ 可视化分析

### 11.4 预期成果

- 识别推理能力最强的模型
- 分析不同推理类型的难度
- 评估推理过程的质量
- 为模型改进提供方向

---

**文档版本**: v1.0  
**创建日期**: 2026-03-05  
**作者**: Kiro AI Assistant  
**状态**: 设计完成，待实施
