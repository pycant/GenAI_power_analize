# -*- coding: utf-8 -*-
"""
问答任务质量评估器 - 学术标准版

基于传统NLP评估指标:
- Exact Match (EM)
- F1 Score
- BERTScore (可选)
- ROUGE-L
- BLEU
"""

import re
import string
from typing import Dict, Optional, List


class QAEvaluator:
    """问答任务评估器 - 基于学术标准指标"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.use_bertscore = self.config.get('use_bertscore', False)
        self.device = self.config.get('device', 'cuda')
        self.lang = self.config.get('lang', 'en')
        self.extract_answer = self.config.get('extract_answer', True)
    
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
        
        # 答案提取(如果启用)
        if self.extract_answer:
            extracted = self._extract_final_answer(generated)
            scores['extracted_answer'] = extracted
        else:
            extracted = generated
            scores['extracted_answer'] = None
        
        # 1. Exact Match
        scores['exact_match'] = self._calculate_exact_match(extracted, reference)
        
        # 2. F1 Score
        scores['f1_score'] = self._calculate_f1_score(extracted, reference)
        
        # 3. BERTScore (可选)
        if self.use_bertscore:
            bertscore_results = self._calculate_bertscore(extracted, reference)
            scores.update(bertscore_results)
        else:
            scores['bertscore_precision'] = None
            scores['bertscore_recall'] = None
            scores['bertscore_f1'] = None
        
        # 4. ROUGE-L
        scores['rouge_l'] = self._calculate_rouge_l(extracted, reference)
        
        # 5. BLEU
        scores['bleu'] = self._calculate_bleu(extracted, reference)
        
        return scores
    
    def _extract_final_answer(self, text: str) -> str:
        """
        从模型输出中提取最终答案
        
        策略:
        1. 查找明确的答案标记("answer is", "the answer is", "correct answer")
        2. 查找结论性语句("therefore", "thus", "in conclusion")
        3. 提取最后一句话
        4. 如果都失败,返回前100个字符
        """
        if not text or len(text.strip()) == 0:
            return ""
        
        text = text.strip()
        
        # 策略1: 查找明确的答案标记
        answer_patterns = [
            r'(?:the\s+)?(?:correct\s+)?answer\s+is[:\s]+([^.!?\n]+)',
            r'(?:the\s+)?(?:final\s+)?answer[:\s]+([^.!?\n]+)',
            r'therefore[,\s]+(?:the\s+)?answer\s+is[:\s]+([^.!?\n]+)',
            r'thus[,\s]+(?:the\s+)?answer\s+is[:\s]+([^.!?\n]+)',
            r'in\s+conclusion[,\s]+([^.!?\n]+)',
            r'so\s+(?:the\s+)?answer\s+is[:\s]+([^.!?\n]+)',
        ]
        
        for pattern in answer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                # 清理答案(去除引号、括号等)
                answer = re.sub(r'^["\'\(\[\{]+|["\'\)\]\}]+$', '', answer)
                if len(answer) > 0:
                    return answer
        
        # 策略2: 查找结论性段落(最后一段)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if paragraphs:
            last_para = paragraphs[-1]
            # 如果最后一段较短(可能是答案)
            if len(last_para) < 200:
                return last_para
        
        # 策略3: 提取最后一句话
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if sentences:
            last_sentence = sentences[-1]
            # 如果最后一句较短(可能是答案)
            if len(last_sentence) < 150:
                return last_sentence
        
        # 策略4: 返回前100个字符(作为fallback)
        return text[:100].strip()
    
    
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
            print("⚠️  bert-score not installed. Run: pip install bert-score")
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
            
            # 确保文本不为空
            if not generated.strip() or not reference.strip():
                return 0.0
            
            rouge = Rouge()
            scores = rouge.get_scores(generated, reference)[0]
            
            return scores['rouge-l']['f']
        except ImportError:
            return None
        except Exception as e:
            # 处理rouge库的异常(如空文本、特殊字符等)
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
            'bertscore_precision': None,
            'bertscore_recall': None,
            'bertscore_f1': None,
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
