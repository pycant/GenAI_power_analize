# -*- coding: utf-8 -*-
"""
文本摘要任务质量评估器

基于多维度评估指标:
- ROUGE-L (结构完整性)
- ROUGE-1/2 (词汇覆盖)
- BERTScore (语义相似度，可选)
- 压缩比 (简洁性)
- 字数符合度 (任务完成度)
- 信息密度 (效率)
- BARTScore (高级评估，可选)
"""

from typing import Dict, Optional
from .base_evaluator import BaseEvaluator


class SummaryEvaluator(BaseEvaluator):
    """文本摘要任务评估器"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.use_bertscore = config.get('use_bertscore', True) if config else True
        self.use_bartscore = config.get('use_bartscore', False) if config else False
        self.device = config.get('device', 'cuda') if config else 'cuda'
        self.lang = config.get('lang', 'zh') if config else 'zh'
    
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
        
        # 5. 信息密度
        if 'rouge_l_recall' in scores and scores['compression_ratio'] > 0:
            scores['information_density'] = (
                scores['rouge_l_recall'] / scores['compression_ratio']
            )
        else:
            scores['information_density'] = None
        
        # 6. BARTScore（可选，成本高）
        if self.use_bartscore:
            bartscore_results = self._calculate_bartscore(generated, reference)
            scores.update(bartscore_results)
        else:
            scores['bartscore_info'] = None
            scores['bartscore_faith'] = None
            scores['bartscore_avg'] = None
        
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
    
    def _calculate_bartscore(self, summary: str, source: str) -> Dict[str, float]:
        """计算BARTScore"""
        try:
            import sys
            from pathlib import Path
            
            # 添加BARTScore路径
            bartscore_path = Path(__file__).parent.parent.parent.parent / 'tools' / 'thesis_reproduction' / 'BARTScore'
            if str(bartscore_path) not in sys.path:
                sys.path.insert(0, str(bartscore_path))
            
            from bart_score import BARTScorer
            
            bart_scorer = BARTScorer(
                device=self.device,
                checkpoint='facebook/bart-large-cnn'
            )
            
            # 信息性：summary -> source
            info_score = bart_scorer.score([source], [summary])[0]
            
            # 忠实性：source -> summary
            faith_score = bart_scorer.score([summary], [source])[0]
            
            return {
                'bartscore_info': info_score,
                'bartscore_faith': faith_score,
                'bartscore_avg': (info_score + faith_score) / 2
            }
        except ImportError as e:
            print(f"⚠️  BARTScore not available: {e}")
            return {
                'bartscore_info': None,
                'bartscore_faith': None,
                'bartscore_avg': None
            }
        except Exception as e:
            print(f"⚠️  BARTScore calculation failed: {e}")
            return {
                'bartscore_info': None,
                'bartscore_faith': None,
                'bartscore_avg': None
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
            'rouge_1_precision': 0.0,
            'rouge_1_recall': 0.0,
            'rouge_1_f1': 0.0,
            'rouge_2_precision': 0.0,
            'rouge_2_recall': 0.0,
            'rouge_2_f1': 0.0,
            'rouge_l_precision': 0.0,
            'rouge_l_recall': 0.0,
            'rouge_l_f1': 0.0,
            'bertscore_precision': None,
            'bertscore_recall': None,
            'bertscore_f1': None,
            'compression_ratio': 0.0,
            'length': 0,
            'in_range': 0.0,
            'compliance_score': 0.0,
            'information_density': 0.0,
            'bartscore_info': None,
            'bartscore_faith': None,
            'bartscore_avg': None
        }
    
    def get_metric_categories(self) -> Dict[str, list]:
        """返回指标分类"""
        return {
            'content': ['rouge_1_f1', 'rouge_2_f1', 'rouge_l_f1'],
            'semantic': ['bertscore_precision', 'bertscore_recall', 'bertscore_f1'],
            'conciseness': ['compression_ratio', 'length', 'in_range', 'information_density'],
            'advanced': ['bartscore_info', 'bartscore_faith', 'bartscore_avg']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向(True=越大越好)"""
        return {
            'rouge_1_precision': True,
            'rouge_1_recall': True,
            'rouge_1_f1': True,
            'rouge_2_precision': True,
            'rouge_2_recall': True,
            'rouge_2_f1': True,
            'rouge_l_precision': True,
            'rouge_l_recall': True,
            'rouge_l_f1': True,
            'bertscore_precision': True,
            'bertscore_recall': True,
            'bertscore_f1': True,
            'compression_ratio': False,  # 适中为好，但简化为越小越好
            'in_range': True,
            'compliance_score': True,
            'information_density': True,
            'bartscore_info': True,
            'bartscore_faith': True,
            'bartscore_avg': True
        }
