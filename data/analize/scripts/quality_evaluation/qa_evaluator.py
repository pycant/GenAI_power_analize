# -*- coding: utf-8 -*-
"""
问答任务质量评估器

评估维度:
- 响应完整性: 是否包含答案、结论
- 专业性: 技术术语密度
- 置信度: 确定性程度
- 结构质量: 段落组织、列举
- 推理深度: 推理过程、例子
"""

import re
from typing import Dict, Set


class QAEvaluator:
    """问答任务评估器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.domain = self.config.get('domain', 'cs')
        self._load_technical_terms()
    
    def _load_technical_terms(self):
        """加载技术术语库"""
        # 计算机科学术语
        self.cs_terms = {
            'algorithm', 'complexity', 'runtime', 'worst-case', 'average-case',
            'hash', 'table', 'array', 'linked', 'list', 'tree', 'graph',
            'sort', 'search', 'binary', 'quicksort', 'mergesort', 'heapsort',
            'network', 'protocol', 'packet', 'encryption', 'authentication',
            'security', 'vulnerability', 'firewall', 'port', 'scan', 'nmap',
            'boolean', 'operator', 'logic', 'gate', 'circuit',
            'nand', 'nor', 'xor', 'and', 'or', 'not',
            'ipsec', 'vpn', 'ssl', 'tls', 'tcp', 'udp', 'ip', 'http',
            'data', 'structure', 'pointer', 'memory', 'stack', 'queue',
            'recursion', 'iteration', 'loop', 'function', 'class', 'object',
            'insertion', 'deletion', 'traversal', 'pivot', 'partition',
            'confidentiality', 'integrity', 'availability', 'cipher'
        }
    
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict = None) -> Dict[str, float]:
        """
        评估问答质量
        
        Args:
            generated: 生成的答案文本
            reference: 标准答案(可选,QA任务通常没有)
            context: 额外上下文
        
        Returns:
            Dict[str, float]: 多维度指标
        """
        scores = {}
        
        # 基础检查
        if not generated or len(generated.strip()) == 0:
            return self._get_zero_scores()
        
        # 1. 响应完整性
        completeness_scores = self._calculate_completeness(generated)
        scores.update(completeness_scores)
        
        # 2. 技术术语密度
        scores['technical_term_density'] = self._calculate_technical_density(generated)
        scores['technical_term_count'] = self._count_technical_terms(generated)
        
        # 3. 置信度
        scores['confidence_score'] = self._calculate_confidence(generated)
        scores['uncertainty_count'] = self._count_uncertainty(generated)
        scores['certainty_count'] = self._count_certainty(generated)
        
        # 4. 结构质量
        structure_scores = self._calculate_structure(generated)
        scores.update(structure_scores)
        
        # 5. 推理深度
        reasoning_scores = self._calculate_reasoning(generated)
        scores.update(reasoning_scores)
        
        return scores

    
    def _calculate_completeness(self, text: str) -> Dict[str, float]:
        """计算响应完整性"""
        scores = {}
        
        # 是否有答案
        scores['has_answer'] = 1.0 if len(text.strip()) > 50 else 0.0
        scores['answer_length'] = len(text)
        
        # 检测结论
        conclusion_patterns = [
            r'(?:answer|result|conclusion|therefore|thus|so)\s+is',
            r'(?:答案|结论|因此|所以)\s*(?:是|为)',
            r'the correct answer',
            r'in summary',
            r'to summarize'
        ]
        
        has_conclusion = any(
            re.search(pattern, text, re.IGNORECASE) 
            for pattern in conclusion_patterns
        )
        scores['has_conclusion'] = 1.0 if has_conclusion else 0.0
        
        return scores
    
    def _calculate_technical_density(self, text: str) -> float:
        """计算技术术语密度"""
        words = text.lower().split()
        
        if len(words) == 0:
            return 0.0
        
        term_count = sum(1 for word in words if word in self.cs_terms)
        density = term_count / len(words)
        
        # 归一化 (0-0.3为正常范围)
        normalized_density = min(density / 0.3, 1.0)
        
        return normalized_density
    
    def _count_technical_terms(self, text: str) -> int:
        """统计技术术语数量"""
        words = text.lower().split()
        return sum(1 for word in words if word in self.cs_terms)
    
    def _calculate_confidence(self, text: str) -> float:
        """计算置信度"""
        text_lower = text.lower()
        
        uncertainty_count = self._count_uncertainty(text_lower)
        certainty_count = self._count_certainty(text_lower)
        
        # 基础分数0.5 + 确定性0.1 - 不确定性0.1
        confidence = 0.5 + (certainty_count * 0.1) - (uncertainty_count * 0.1)
        
        return max(0.0, min(1.0, confidence))
    
    def _count_uncertainty(self, text: str) -> int:
        """统计不确定性表达"""
        uncertainty_keywords = [
            'i think', 'probably', 'maybe', 'perhaps', 'might',
            'could be', 'not sure', 'unclear', 'uncertain',
            'i believe', 'seems like', 'appears to'
        ]
        
        return sum(1 for keyword in uncertainty_keywords if keyword in text)
    
    def _count_certainty(self, text: str) -> int:
        """统计确定性表达"""
        certainty_keywords = [
            'definitely', 'certainly', 'clearly', 'obviously',
            'the answer is', 'the correct answer', 'must be',
            'always', 'never', 'exactly'
        ]
        
        return sum(1 for keyword in certainty_keywords if keyword in text)
    
    def _calculate_structure(self, text: str) -> Dict[str, float]:
        """计算结构质量"""
        scores = {}
        
        # 段落分析
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
        scores['paragraph_count'] = len(paragraphs)
        
        if paragraphs:
            avg_length = sum(len(p) for p in paragraphs) / len(paragraphs)
            scores['avg_paragraph_length'] = avg_length
        else:
            scores['avg_paragraph_length'] = 0
        
        # 检测列举
        enumeration_patterns = [
            r'(?:first|second|third|finally)',
            r'(?:1\.|2\.|3\.)',
            r'(?:a\)|b\)|c\))',
            r'(?:首先|其次|最后)'
        ]
        
        has_enumeration = any(
            re.search(pattern, text, re.IGNORECASE) 
            for pattern in enumeration_patterns
        )
        scores['has_enumeration'] = 1.0 if has_enumeration else 0.0
        
        return scores
    
    def _calculate_reasoning(self, text: str) -> Dict[str, float]:
        """计算推理深度"""
        scores = {}
        
        # 推理关键词
        reasoning_keywords = [
            'because', 'since', 'therefore', 'thus', 'so',
            'if', 'then', 'when', 'however', 'but',
            '因为', '所以', '因此', '如果', '那么'
        ]
        
        has_reasoning = any(
            keyword in text.lower() 
            for keyword in reasoning_keywords
        )
        scores['has_reasoning'] = 1.0 if has_reasoning else 0.0
        
        # 推理步骤数
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        scores['reasoning_steps'] = len(sentences)
        
        # 检测例子
        example_patterns = [
            r'for example', r'for instance', r'such as',
            r'例如', r'比如', r'举例'
        ]
        
        has_examples = any(
            re.search(pattern, text, re.IGNORECASE) 
            for pattern in example_patterns
        )
        scores['has_examples'] = 1.0 if has_examples else 0.0
        
        return scores
    
    def _get_zero_scores(self) -> Dict[str, float]:
        """返回零分数"""
        return {
            'has_answer': 0.0,
            'answer_length': 0,
            'has_conclusion': 0.0,
            'technical_term_density': 0.0,
            'technical_term_count': 0,
            'confidence_score': 0.0,
            'uncertainty_count': 0,
            'certainty_count': 0,
            'paragraph_count': 0,
            'avg_paragraph_length': 0,
            'has_enumeration': 0.0,
            'has_reasoning': 0.0,
            'reasoning_steps': 0,
            'has_examples': 0.0
        }
    
    def get_metric_categories(self) -> Dict[str, list]:
        """返回指标分类"""
        return {
            'completeness': ['has_answer', 'answer_length', 'has_conclusion'],
            'professionalism': ['technical_term_density', 'technical_term_count'],
            'confidence': ['confidence_score', 'uncertainty_count', 'certainty_count'],
            'structure': ['paragraph_count', 'avg_paragraph_length', 'has_enumeration'],
            'reasoning': ['has_reasoning', 'reasoning_steps', 'has_examples']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向"""
        return {
            'has_answer': True,
            'answer_length': True,
            'has_conclusion': True,
            'technical_term_density': True,
            'technical_term_count': True,
            'confidence_score': True,
            'uncertainty_count': False,  # 越少越好
            'certainty_count': True,
            'paragraph_count': True,
            'has_enumeration': True,
            'has_reasoning': True,
            'reasoning_steps': True,
            'has_examples': True
        }
