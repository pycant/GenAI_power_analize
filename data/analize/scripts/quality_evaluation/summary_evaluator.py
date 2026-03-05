# -*- coding: utf-8 -*-
"""
文本摘要任务质量评估器

评估指标：
- ROUGE-1/2/L: 内容覆盖和结构完整性
- BERTScore: 语义相似度
- 压缩比: 简洁性
- 字数符合度: 任务完成度
- 信息密度: 信息效率
"""

from typing import Dict, Optional


class SummaryEvaluator:
    """文本摘要任务评估器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.use_bertscore = self.config.get('use_bertscore', True)
        self.device = self.config.get('device', 'cuda')
        self.lang = self.config.get('lang', 'zh')
    
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict = None) -> Dict[str, float]:
        """
        评估摘要质量
        
        Args:
            generated: 生成的摘要
            reference: 原文（必需）
            context: 额外上下文（可包含字数要求）
        
        Returns:
            Dict[str, float]: 多维度指标
        """
        scores = {}
        
        # 基础检查
        if not generated or not reference:
            return self._get_zero_scores()
        
        # 1. ROUGE 分数
        rouge_scores = self._calculate_rouge(generated, reference)
        scores.update(rouge_scores)
        
        # 2. BERTScore（可选）
        if self.use_bertscore:
            bertscore_results = self._calculate_bertscore(generated, reference)
            scores.update(bertscore_results)
        else:
            scores['bertscore_precision'] = None
            scores['bertscore_recall'] = None
            scores['bertscore_f1'] = None
        
        # 3. 压缩比
        scores['compression_ratio'] = self._calculate_compression_ratio(
            generated, reference
        )
        
        # 4. 字数符合度
        if context and 'min_length' in context and 'max_length' in context:
            length_scores = self._calculate_length_compliance(
                generated, 
                context['min_length'], 
                context['max_length']
            )
            scores.update(length_scores)
        else:
            scores['length'] = len(generated)
            scores['in_range'] = None
            scores['compliance_score'] = None
            scores['deviation'] = None
        
        # 5. 信息密度
        if 'rouge_l_recall' in scores and scores['compression_ratio'] > 0:
            scores['information_density'] = (
                scores['rouge_l_recall'] / scores['compression_ratio']
            )
        else:
            scores['information_density'] = None
        
        return scores
    
    def _calculate_rouge(self, summary: str, source: str) -> Dict[str, float]:
        """计算ROUGE分数"""
        try:
            from rouge import Rouge
            
            rouge = Rouge()
            scores = rouge.get_scores(summary, source)[0]
            
            return {
                'rouge_1_precision': scores['rouge-1']['p'],
                'rouge_1_recall': scores['rouge-1']['r'],
                'rouge_1_f1': scores['rouge-1']['f'],
                'rouge_2_precision': scores['rouge-2']['p'],
                'rouge_2_recall': scores['rouge-2']['r'],
                'rouge_2_f1': scores['rouge-2']['f'],
                'rouge_l_precision': scores['rouge-l']['p'],
                'rouge_l_recall': scores['rouge-l']['r'],
                'rouge_l_f1': scores['rouge-l']['f']
            }
        except Exception as e:
            print(f"⚠️  ROUGE calculation failed: {e}")
            return {
                'rouge_1_precision': None,
                'rouge_1_recall': None,
                'rouge_1_f1': None,
                'rouge_2_precision': None,
                'rouge_2_recall': None,
                'rouge_2_f1': None,
                'rouge_l_precision': None,
                'rouge_l_recall': None,
                'rouge_l_f1': None
            }
    
    def _calculate_bertscore(self, summary: str, source: str) -> Dict[str, float]:
        """计算BERTScore"""
        try:
            import bert_score
            from bert_score import score
            
            P, R, F1 = score(
                [summary], 
                [source], 
                lang=self.lang,
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
    
    def _calculate_compression_ratio(self, summary: str, source: str) -> float:
        """计算压缩比"""
        if len(source) == 0:
            return 0.0
        return len(summary) / len(source)
    
    def _calculate_length_compliance(self, summary: str, 
                                    min_length: int, 
                                    max_length: int) -> Dict[str, float]:
        """计算字数符合度"""
        length = len(summary)
        in_range = 1.0 if min_length <= length <= max_length else 0.0
        
        if length < min_length:
            deviation = (min_length - length) / min_length
        elif length > max_length:
            deviation = (length - max_length) / max_length
        else:
            deviation = 0.0
        
        return {
            'length': length,
            'in_range': in_range,
            'deviation': deviation,
            'compliance_score': max(0.0, 1.0 - deviation)
        }
    
    def _get_zero_scores(self) -> Dict[str, float]:
        """返回零分数"""
        return {
            'rouge_1_f1': 0.0,
            'rouge_2_f1': 0.0,
            'rouge_l_f1': 0.0,
            'bertscore_f1': 0.0,
            'compression_ratio': 0.0,
            'length': 0,
            'in_range': 0.0,
            'information_density': 0.0
        }
    
    def get_metric_categories(self) -> Dict[str, list]:
        """返回指标分类"""
        return {
            'content': ['rouge_1_f1', 'rouge_2_f1', 'rouge_l_f1'],
            'semantic': ['bertscore_precision', 'bertscore_recall', 'bertscore_f1'],
            'conciseness': ['compression_ratio', 'length', 'in_range', 'information_density']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向(True=越大越好)"""
        return {
            'rouge_1_f1': True,
            'rouge_2_f1': True,
            'rouge_l_f1': True,
            'bertscore_precision': True,
            'bertscore_recall': True,
            'bertscore_f1': True,
            'compression_ratio': False,  # 适中为好，但简化为越小越好
            'in_range': True,
            'compliance_score': True,
            'information_density': True
        }
