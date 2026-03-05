# -*- coding: utf-8 -*-
"""
逻辑推理任务质量评估器

基于多维度评估指标:
- 结论正确性 (Conclusion Correctness)
- 推理完整性 (Reasoning Completeness)
- 逻辑连贯性 (Logical Coherence)
- 推理深度 (Reasoning Depth)
- 关键词覆盖 (Keyword Coverage)
- LLM-as-Judge (可选)
"""

import re
import string
import math
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
    
    def _extract_conclusion(self, text: str) -> str:
        """提取最终结论"""
        if not text or len(text.strip()) == 0:
            return ""
        
        text = text.strip()
        
        # 策略1: 查找明确的答案标记
        answer_patterns = [
            r'(?:答案|结论|因此|所以)(?:是|为)[：:]\s*([^。\n]+)',
            r'(?:the\s+)?answer\s+is[:\s]+([^.!\n]+)',
            r'(?:conclusion|therefore|thus)[:\s]+([^.!\n]+)',
        ]
        
        for pattern in answer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                if len(answer) > 0:
                    return answer
        
        # 策略2: 提取最后一段
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if paragraphs:
            last_para = paragraphs[-1]
            if len(last_para) < 200:
                return last_para
        
        # 策略3: 提取最后一句
        sentences = re.split(r'[。.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if sentences:
            last_sentence = sentences[-1]
            if len(last_sentence) < 150:
                return last_sentence
        
        # 策略4: 返回前100个字符
        return text[:100].strip()
    
    def _normalize_answer(self, text: str) -> str:
        """答案归一化"""
        # 转小写
        text = text.lower()
        
        # 去除标点
        text = text.translate(str.maketrans('', '', string.punctuation + '，。！？；：""''（）【】'))
        
        # 去除多余空格
        text = ' '.join(text.split()).strip()
        
        return text
    
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
    
    def _calculate_conclusion_correctness(self, generated: str, 
                                         reference: str) -> Dict[str, float]:
        """计算结论正确性"""
        # 提取结论
        conclusion = self._extract_conclusion(generated)
        
        # 归一化比较
        gen_normalized = self._normalize_answer(conclusion)
        ref_normalized = self._normalize_answer(reference)
        
        # 检查是否包含关键信息
        if ref_normalized in gen_normalized or gen_normalized in ref_normalized:
            conclusion_correct = 1.0
        else:
            # 使用F1分数作为软匹配
            f1 = self._calculate_f1_score(conclusion, reference)
            conclusion_correct = 1.0 if f1 > 0.7 else 0.0
        
        return {
            'conclusion_correct': conclusion_correct,
            'conclusion_f1': self._calculate_f1_score(conclusion, reference)
        }
    
    def _calculate_reasoning_completeness(self, text: str) -> Dict[str, float]:
        """评估推理完整性"""
        scores = {}
        
        # 1. 检测前提关键词
        premise_keywords = [
            'given', 'assume', 'suppose', 'if', 'premise',
            '假设', '已知', '前提', '如果', '条件', '有'
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
        sentences = [s.strip() for s in re.split(r'[。.!?]+', text) if len(s.strip()) > 10]
        scores['step_count'] = len(sentences)
        
        # 5. 综合完整性得分
        completeness = (
            scores['has_premise'] * 0.3 +
            scores['has_reasoning_steps'] * 0.4 +
            scores['has_conclusion'] * 0.3
        )
        scores['completeness_score'] = completeness
        
        return scores

    
    def _calculate_logical_coherence(self, text: str) -> Dict[str, float]:
        """评估逻辑连贯性"""
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
        coherence = math.exp(-((actual_density - ideal_density) ** 2) / (2 * 0.005 ** 2))
        scores['coherence_score'] = coherence
        
        return scores
    
    def _calculate_reasoning_depth(self, text: str) -> Dict[str, float]:
        """评估推理深度"""
        scores = {}
        
        # 1. 句子数量
        sentences = [s.strip() for s in re.split(r'[。.!?]+', text) if len(s.strip()) > 10]
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
    
    def _calculate_keyword_coverage(self, text: str, question: str) -> float:
        """计算关键词覆盖率"""
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
    
    def _calculate_extraction_confidence(self, text: str) -> float:
        """评估答案提取置信度"""
        # 检测明确的答案标记
        answer_markers = [
            'answer is', 'the answer', 'conclusion is', 'therefore',
            '答案是', '结论是', '因此', '所以'
        ]
        
        has_marker = any(marker in text.lower() for marker in answer_markers)
        
        if has_marker:
            return 1.0
        
        # 检测最后一句是否像答案
        sentences = [s.strip() for s in re.split(r'[。.!?]+', text) if len(s.strip()) > 5]
        if sentences:
            last_sentence = sentences[-1]
            # 短句子更可能是答案
            if len(last_sentence.split()) < 20:
                return 0.7
        
        return 0.3
    
    def _evaluate_with_llm_judge(self, question: str, generated: str,
                                 reference: str) -> Optional[Dict]:
        """使用LLM作为评判者（可选）"""
        try:
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
            
            response = openai.ChatCompletion.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"⚠️  LLM-as-Judge failed: {e}")
            return None
    
    def _get_zero_scores(self) -> Dict[str, float]:
        """返回零分数"""
        return {
            'conclusion_correct': 0.0,
            'conclusion_f1': 0.0,
            'has_premise': 0.0,
            'has_reasoning_steps': 0.0,
            'has_conclusion': 0.0,
            'step_count': 0,
            'reasoning_keyword_count': 0,
            'completeness_score': 0.0,
            'has_logical_connectors': 0.0,
            'connector_density': 0.0,
            'coherence_score': 0.0,
            'sentence_count': 0,
            'avg_sentence_length': 0.0,
            'depth_score': 0.0,
            'keyword_coverage': 0.0,
            'extraction_confidence': 0.0
        }
    
    def get_metric_categories(self) -> Dict[str, list]:
        """返回指标分类"""
        return {
            'correctness': ['conclusion_correct', 'conclusion_f1'],
            'completeness': ['has_premise', 'has_reasoning_steps', 'has_conclusion', 
                           'step_count', 'completeness_score'],
            'coherence': ['has_logical_connectors', 'connector_density', 'coherence_score'],
            'depth': ['sentence_count', 'avg_sentence_length', 'depth_score'],
            'relevance': ['keyword_coverage', 'extraction_confidence']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向(True=越大越好)"""
        return {
            'conclusion_correct': True,
            'conclusion_f1': True,
            'has_premise': True,
            'has_reasoning_steps': True,
            'has_conclusion': True,
            'step_count': True,
            'reasoning_keyword_count': True,
            'completeness_score': True,
            'has_logical_connectors': True,
            'connector_density': True,
            'coherence_score': True,
            'sentence_count': True,
            'avg_sentence_length': True,
            'depth_score': True,
            'keyword_coverage': True,
            'extraction_confidence': True
        }
