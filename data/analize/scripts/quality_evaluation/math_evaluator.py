"""
数学推理任务质量评估器

评估维度：
1. 准确性 (Accuracy): Exact Match, Numerical Match
2. 推理完整性 (Reasoning Completeness): 推理关键词、步骤数、计算式
3. 置信度 (Confidence): 答案提取可靠性
"""

import re
from typing import Dict, Optional, List
import warnings
warnings.filterwarnings('ignore')


class MathEvaluator:
    """数学推理任务评估器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.tolerance = self.config.get('tolerance', 0.01)  # 默认1%误差
    
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict = None) -> Dict[str, float]:
        """
        评估数学推理质量
        
        Args:
            generated: 生成的答案文本
            reference: 标准答案
            context: 额外上下文
        
        Returns:
            Dict[str, float]: 多维度指标
        """
        scores = {}
        
        # 基础检查
        if not generated or len(str(generated).strip()) == 0:
            return self._get_zero_scores()
        
        generated = str(generated)
        
        # 1. 答案提取
        extracted_answer = self._extract_answer(generated)
        scores['extraction_confidence'] = self._calculate_extraction_confidence(generated)
        scores['has_answer'] = 1.0 if extracted_answer else 0.0
        
        # 2. 准确性评估（需要标准答案）
        if reference:
            scores['exact_match'] = self._calculate_exact_match(generated, reference)
            scores['numerical_match'] = self._calculate_numerical_match(generated, reference)
        else:
            scores['exact_match'] = None
            scores['numerical_match'] = None
        
        # 3. 推理完整性评估
        reasoning_scores = self._calculate_reasoning_completeness(generated)
        scores.update(reasoning_scores)
        
        # 4. 基础指标
        scores['text_length'] = len(generated)
        scores['extracted_answer'] = extracted_answer
        
        return scores
    
    def _extract_answer(self, text: str) -> Optional[str]:
        """
        从文本中提取答案
        
        策略优先级：
        1. 明确的答案标记
        2. 等号后的数值
        3. 最后一个数值
        """
        # 策略1: 明确的答案标记
        answer_patterns = [
            r'(?:answer|result|total|solution|profit)\s*(?:is|=|:)?\s*\$?\s*(\d+\.?\d*)',
            r'(?:答案|结果|总计|共|利润)\s*(?:是|为|：)?\s*\$?\s*(\d+\.?\d*)',
            r'=\s*\$?\s*(\d+\.?\d*)(?:\s|$|\.|,)',
            r'(?:raise|make|spend|get|sold)\s+\$?\s*(\d+\.?\d*)',
        ]
        
        for pattern in answer_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # 返回最后一个匹配（通常是最终答案）
                return matches[-1]
        
        # 策略2: 最后一个数值
        numbers = re.findall(r'\$?\s*(\d+\.?\d*)', text)
        if numbers:
            # 过滤掉太小的数字（可能是中间步骤）
            valid_numbers = [n for n in numbers if float(n) >= 0.1]
            if valid_numbers:
                return valid_numbers[-1]
        
        return None
    
    def _extract_number(self, text: str) -> Optional[float]:
        """从文本中提取数值（浮点数）"""
        answer_str = self._extract_answer(text)
        if answer_str is None:
            return None
        
        try:
            # 移除货币符号和逗号
            cleaned = answer_str.replace('$', '').replace(',', '').strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _normalize_answer(self, answer: str) -> str:
        """
        归一化答案字符串
        
        处理：
        - 移除空格
        - 统一大小写
        - 移除货币符号
        - 移除单位
        """
        if answer is None:
            return ""
        
        # 转小写
        normalized = str(answer).lower().strip()
        
        # 移除常见符号
        normalized = normalized.replace('$', '').replace(',', '').replace(' ', '')
        
        # 移除常见单位
        units = ['dollars', 'dollar', 'students', 'student', 'books', 'book',
                 '美元', '学生', '本', '个']
        for unit in units:
            normalized = normalized.replace(unit, '')
        
        return normalized.strip()
    
    def _calculate_exact_match(self, generated: str, reference: str) -> float:
        """计算精确匹配"""
        gen_answer = self._extract_answer(generated)
        
        if gen_answer is None:
            return 0.0
        
        # 归一化比较
        gen_norm = self._normalize_answer(gen_answer)
        ref_norm = self._normalize_answer(reference)
        
        # 尝试数值比较
        try:
            gen_num = float(gen_norm)
            ref_num = float(ref_norm)
            return 1.0 if abs(gen_num - ref_num) < 0.001 else 0.0
        except (ValueError, TypeError):
            # 字符串比较
            return 1.0 if gen_norm == ref_norm else 0.0
    
    def _calculate_numerical_match(self, generated: str, reference: str) -> float:
        """
        计算数值匹配（允许误差）
        
        Args:
            generated: 生成的文本
            reference: 标准答案
        
        Returns:
            float: 1.0 (匹配) 或 0.0 (不匹配)
        """
        gen_num = self._extract_number(generated)
        
        # 从reference提取数值
        try:
            ref_num = float(self._normalize_answer(reference))
        except (ValueError, TypeError):
            ref_num = self._extract_number(reference)
        
        if gen_num is None or ref_num is None:
            return 0.0
        
        # 处理零值情况
        if ref_num == 0:
            return 1.0 if abs(gen_num) < self.tolerance else 0.0
        
        # 计算相对误差
        relative_error = abs(gen_num - ref_num) / abs(ref_num)
        
        return 1.0 if relative_error < self.tolerance else 0.0
    
    def _calculate_reasoning_completeness(self, text: str) -> Dict[str, float]:
        """
        计算推理完整性
        
        Returns:
            Dict with:
            - has_reasoning: 是否包含推理关键词
            - step_count: 推理步骤数量
            - has_calculation: 是否包含计算式
        """
        scores = {}
        
        # 1. 检测推理关键词
        reasoning_keywords = [
            'first', 'then', 'next', 'finally', 'so', 'therefore',
            'now', 'let', 'need', 'should', 'calculate',
            '首先', '然后', '接下来', '最后', '所以', '因此',
            '现在', '需要', '应该', '计算'
        ]
        
        text_lower = text.lower()
        has_reasoning = any(kw in text_lower for kw in reasoning_keywords)
        scores['has_reasoning'] = 1.0 if has_reasoning else 0.0
        
        # 2. 计算步骤数量（基于句子分割）
        # 使用多种分隔符
        sentences = re.split(r'[.。\n]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        scores['step_count'] = len(sentences)
        
        # 3. 检测计算式
        calculation_patterns = [
            r'\d+\s*[\+\-\*\/×÷]\s*\d+',  # 基本运算
            r'\d+\s*=\s*\d+',              # 等式
            r'\(\d+.*?\)',                 # 括号表达式
            r'\d+\s*[×x]\s*\d+',          # 乘法
            r'\d+\s*÷\s*\d+',             # 除法
        ]
        
        has_calculation = any(
            re.search(pattern, text) 
            for pattern in calculation_patterns
        )
        scores['has_calculation'] = 1.0 if has_calculation else 0.0
        
        return scores
    
    def _calculate_extraction_confidence(self, text: str) -> float:
        """
        计算答案提取置信度
        
        Returns:
            float: [0, 1]，越高表示答案越明确
        """
        confidence = 0.0
        
        # 1. 检测明确的答案标记
        answer_markers = [
            r'answer is (\d+)',
            r'result is (\d+)',
            r'= (\d+)$',
            r'total.*?(\d+)',
            r'答案是?\s*(\d+)',
            r'结果是?\s*(\d+)',
        ]
        
        for pattern in answer_markers:
            if re.search(pattern, text, re.IGNORECASE):
                confidence += 0.3
                break
        
        # 2. 检测数值的唯一性
        numbers = re.findall(r'\$?\d+\.?\d*', text)
        if len(numbers) == 1:
            confidence += 0.4  # 唯一数值，高置信度
        elif len(numbers) == 2:
            confidence += 0.3  # 少量数值，较高置信度
        elif len(numbers) <= 5:
            confidence += 0.2  # 中等数量，中等置信度
        else:
            confidence += 0.1  # 数值较多，低置信度
        
        # 3. 检测答案位置（末尾更可靠）
        last_sentence = text.split('.')[-1]
        if re.search(r'\d+', last_sentence):
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _get_zero_scores(self) -> Dict[str, float]:
        """返回零分数（用于空文本）"""
        return {
            'exact_match': 0.0,
            'numerical_match': 0.0,
            'has_reasoning': 0.0,
            'step_count': 0,
            'has_calculation': 0.0,
            'extraction_confidence': 0.0,
            'text_length': 0,
            'has_answer': 0.0,
            'extracted_answer': None
        }
    
    def get_metric_categories(self) -> Dict[str, List[str]]:
        """返回指标分类"""
        return {
            'accuracy': ['exact_match', 'numerical_match'],
            'reasoning': ['has_reasoning', 'step_count', 'has_calculation'],
            'confidence': ['extraction_confidence', 'has_answer']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向（True=越大越好，False=越小越好）"""
        return {
            'exact_match': True,
            'numerical_match': True,
            'has_reasoning': True,
            'step_count': True,
            'has_calculation': True,
            'extraction_confidence': True,
            'has_answer': True
        }


if __name__ == '__main__':
    # 测试
    evaluator = MathEvaluator(config={'tolerance': 0.01})
    
    test_cases = [
        {
            'text': 'First, find the profit per lollipop: 0.8 - 0.5 = 0.3. Then multiply by 10 and 30: 0.3 × 10 × 30 = 90. The answer is $90.',
            'reference': '90',
            'expected': 'Should match'
        },
        {
            'text': 'Last year 50, this year 20% increase. 50 × 1.2 = 60 students.',
            'reference': '60',
            'expected': 'Should match'
        },
        {
            'text': 'Total spent: 3 × 16 + 3 × 6 = 48 + 18 = 66 dollars',
            'reference': '66',
            'expected': 'Should match'
        }
    ]
    
    print("\n📊 Math Evaluator Test Cases:\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['expected']}")
        print(f"Text: {test['text'][:80]}...")
        
        scores = evaluator.evaluate(test['text'], reference=test['reference'])
        
        print(f"Results:")
        print(f"  - Extracted Answer: {scores.get('extracted_answer')}")
        print(f"  - Numerical Match: {scores['numerical_match']:.0%}")
        print(f"  - Has Reasoning: {scores['has_reasoning']:.0%}")
        print(f"  - Step Count: {scores['step_count']}")
        print(f"  - Has Calculation: {scores['has_calculation']:.0%}")
        print(f"  - Extraction Confidence: {scores['extraction_confidence']:.2f}")
        print()
