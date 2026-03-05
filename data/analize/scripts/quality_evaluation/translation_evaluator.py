# -*- coding: utf-8 -*-
"""
翻译任务质量评估器

评估指标：
- BLEU-1/2/4: 词汇级别匹配度
- chrF: 字符级别F分数
- BERTScore: 语义相似度
- 长度比: 完整性检查
- 编辑距离: 相似度辅助指标
"""

from typing import Dict, Optional


class TranslationEvaluator:
    """翻译任务评估器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.use_bertscore = self.config.get('use_bertscore', True)
        self.device = self.config.get('device', 'cuda')
    
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
        else:
            scores['bertscore_precision'] = None
            scores['bertscore_recall'] = None
            scores['bertscore_f1'] = None
        
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
            
            # 语言代码映射
            lang_code = 'zh' if lang in ['zh', 'zho_Hans'] else 'en'
            
            P, R, F1 = score(
                [generated], [reference],
                model_type=model_type,
                lang=lang_code,
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
    
    def _get_zero_scores(self) -> Dict[str, float]:
        """返回零分数"""
        return {
            'bleu_1': 0.0,
            'bleu_2': 0.0,
            'bleu_4': 0.0,
            'chrf': 0.0,
            'bertscore_precision': 0.0,
            'bertscore_recall': 0.0,
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
            'fluency': ['length_ratio', 'edit_similarity']
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
            'length_ratio': True,
            'edit_similarity': True
        }
