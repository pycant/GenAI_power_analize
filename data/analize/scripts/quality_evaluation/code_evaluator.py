"""
代码生成任务评估器

评估生成代码的质量，包括：
- 编译成功率
- 代码长度
- 代码复杂度
- 测试用例通过率（可选）
"""

import ast
import sys
from typing import Dict, Any, Optional
from .base_evaluator import BaseEvaluator
from .utils import (
    extract_python_code,
    count_code_lines,
    calculate_cyclomatic_complexity
)
from .code_executor import CodeExecutor


class CodeEvaluator(BaseEvaluator):
    """代码生成任务评估器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化代码评估器
        
        Args:
            config: 配置字典
                - enable_execution: 是否启用代码执行测试（默认False）
                - execution_timeout: 执行超时时间（秒，默认5）
        """
        super().__init__(config)
        self.enable_execution = self.config.get('enable_execution', False)
        self.executor = CodeExecutor(timeout=self.config.get('execution_timeout', 5)) if self.enable_execution else None
        self._log(f"Code evaluator initialized (execution: {self.enable_execution})")
    
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict[str, Any] = None) -> Dict[str, float]:
        """
        评估生成代码的质量（多维度独立评分）
        
        Args:
            generated: 生成的代码文本
            reference: 参考代码（可选，用于相对评估）
            context: 额外上下文（可选）
                - test_cases: 测试用例列表（未实现）
                - language: 编程语言（默认 Python）
                - prompt: 原始提示词（用于提取测试用例）
        
        Returns:
            Dict[str, float]: 多维度质量指标字典
            
            功能维度:
                - functional_correctness: 功能正确性 [0, 1]（基于测试通过率）
                - compilation_success: 编译成功 [0, 1]
                - has_code: 是否包含代码 [0, 1]
                - test_pass_rate: 测试通过率 [0, 1]
                - tests_passed: 通过的测试数量
                - tests_total: 总测试数量
            
            效率维度:
                - time_complexity_score: 时间复杂度评分 [0, 1]
                - space_complexity_score: 空间复杂度评分 [0, 1]
            
            质量维度:
                - code_simplicity: 代码简洁性 [0, 1]
                - code_length: 代码行数（原始值）
                - cyclomatic_complexity: 圈复杂度（原始值）
                - nesting_depth: 最大嵌套深度
            
            可读性维度:
                - readability_score: 可读性评分 [0, 1]
                - has_docstring: 是否有文档字符串 [0, 1]
                - has_type_hints: 是否有类型注解 [0, 1]
        """
        context = context or {}
        language = context.get('language', 'python')
        prompt = context.get('prompt', '')
        
        # 初始化结果（多维度）
        scores = {
            # 功能维度
            'functional_correctness': 0.0,
            'compilation_success': 0.0,
            'has_code': 0.0,
            'test_pass_rate': None,
            'tests_passed': None,
            'tests_total': 0,
            
            # 效率维度
            'time_complexity_score': None,
            'space_complexity_score': None,
            
            # 质量维度（原始值）
            'code_simplicity': None,
            'code_length': 0,
            'cyclomatic_complexity': 1,
            'nesting_depth': 0,
            
            # 可读性维度
            'readability_score': None,
            'has_docstring': 0.0,
            'has_type_hints': 0.0,
        }
        
        # 提取代码
        if language.lower() == 'python':
            code = extract_python_code(generated)
        else:
            # 其他语言暂不支持，直接使用原文本
            code = generated
        
        if not code:
            self._log("No code found in generated text")
            return scores
        
        scores['has_code'] = 1.0
        
        # === 功能维度评估 ===
        
        # 编译检查
        if language.lower() == 'python':
            scores['compilation_success'] = self._check_python_compilation(code)
        
        # 代码执行测试
        if self.enable_execution and scores['compilation_success'] > 0 and prompt:
            exec_result = self.executor.evaluate_code_correctness(code, prompt)
            
            if exec_result['has_tests']:
                scores['test_pass_rate'] = exec_result['pass_rate']
                scores['tests_passed'] = exec_result['tests_passed']
                scores['tests_total'] = exec_result['test_count']
                
                # 功能正确性 = 测试通过率
                scores['functional_correctness'] = exec_result['pass_rate']
                
                self._log(f"Tests: {exec_result['tests_passed']}/{exec_result['test_count']} passed ({exec_result['pass_rate']:.1%})")
            else:
                # 没有测试用例，只能基于编译成功率
                scores['functional_correctness'] = scores['compilation_success'] * 0.5
        else:
            # 未启用执行，只能基于编译成功率
            scores['functional_correctness'] = scores['compilation_success'] * 0.5
        
        # === 质量维度评估 ===
        
        # 代码长度
        scores['code_length'] = count_code_lines(code)
        
        # 圈复杂度
        scores['cyclomatic_complexity'] = calculate_cyclomatic_complexity(code)
        
        # 嵌套深度
        scores['nesting_depth'] = self._calculate_nesting_depth(code)
        
        # 代码简洁性评分
        scores['code_simplicity'] = self._calculate_simplicity_score(
            scores['code_length'],
            scores['cyclomatic_complexity'],
            scores['nesting_depth']
        )
        
        # === 效率维度评估 ===
        
        # 时间复杂度评估
        scores['time_complexity_score'] = self._estimate_time_complexity(code)
        
        # 空间复杂度评估
        scores['space_complexity_score'] = self._estimate_space_complexity(code)
        
        # === 可读性维度评估 ===
        
        # 文档字符串检查
        scores['has_docstring'] = 1.0 if ('"""' in code or "'''" in code) else 0.0
        
        # 类型注解检查
        scores['has_type_hints'] = 1.0 if ('->' in code or ': ' in code) else 0.0
        
        # 可读性综合评分
        scores['readability_score'] = self._calculate_readability_score(
            scores['has_docstring'],
            scores['has_type_hints'],
            code
        )
        
        self._log(f"Multi-dimensional evaluation complete")
        
        return scores
    
    def _calculate_nesting_depth(self, code: str) -> int:
        """
        计算代码的最大嵌套深度
        
        Args:
            code: Python代码字符串
        
        Returns:
            int: 最大嵌套深度
        """
        try:
            tree = ast.parse(code)
            max_depth = 0
            
            def get_depth(node, current_depth=0):
                nonlocal max_depth
                max_depth = max(max_depth, current_depth)
                
                # 检查会增加嵌套深度的节点
                if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    current_depth += 1
                
                for child in ast.iter_child_nodes(node):
                    get_depth(child, current_depth)
            
            get_depth(tree)
            return max_depth
        except:
            return 0
    
    def _calculate_simplicity_score(self, length: int, complexity: int, nesting: int) -> float:
        """
        计算代码简洁性评分
        
        基于代码长度、圈复杂度和嵌套深度的综合评估
        使用数据驱动的归一化，而非固定阈值
        
        Args:
            length: 代码行数
            complexity: 圈复杂度
            nesting: 嵌套深度
        
        Returns:
            float: 简洁性评分 [0, 1]，越高越简洁
        """
        # 使用逆函数进行归一化，避免固定阈值
        # 较短的代码、较低的复杂度、较浅的嵌套 → 更高的分数
        
        # 长度评分：使用对数函数，避免过度惩罚长代码
        length_score = 1.0 / (1.0 + length / 15.0)
        
        # 复杂度评分
        complexity_score = 1.0 / (1.0 + complexity / 5.0)
        
        # 嵌套深度评分
        nesting_score = 1.0 / (1.0 + nesting / 3.0)
        
        # 加权平均
        simplicity = (
            0.4 * length_score +
            0.4 * complexity_score +
            0.2 * nesting_score
        )
        
        return simplicity
    
    def _estimate_time_complexity(self, code: str) -> float:
        """
        估算时间复杂度评分
        
        基于静态分析（嵌套循环层数）估算时间复杂度
        
        Args:
            code: Python代码字符串
        
        Returns:
            float: 时间复杂度评分 [0, 1]，越高越好
                1.0 - O(1) or O(log n)
                0.8 - O(n)
                0.5 - O(n²)
                0.3 - O(n³)
                0.1 - O(2ⁿ) or worse
        """
        try:
            tree = ast.parse(code)
            max_nested_loops = 0
            has_recursion = False
            
            def count_nested_loops(node, loop_depth=0):
                nonlocal max_nested_loops, has_recursion
                
                # 检测循环
                if isinstance(node, (ast.For, ast.While)):
                    loop_depth += 1
                    max_nested_loops = max(max_nested_loops, loop_depth)
                
                # 检测递归（简单检测：函数内调用自己）
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name) and child.func.id == func_name:
                                has_recursion = True
                
                for child in ast.iter_child_nodes(node):
                    count_nested_loops(child, loop_depth)
            
            count_nested_loops(tree)
            
            # 根据嵌套层数和递归情况评分
            if has_recursion:
                return 0.6  # 递归通常是 O(n) 或更差
            elif max_nested_loops == 0:
                return 1.0  # O(1)
            elif max_nested_loops == 1:
                return 0.8  # O(n)
            elif max_nested_loops == 2:
                return 0.5  # O(n²)
            elif max_nested_loops == 3:
                return 0.3  # O(n³)
            else:
                return 0.1  # O(n⁴) or worse
        except:
            return 0.5  # 解析失败，返回中等分数
    
    def _estimate_space_complexity(self, code: str) -> float:
        """
        估算空间复杂度评分
        
        基于数据结构创建和递归深度估算空间复杂度
        
        Args:
            code: Python代码字符串
        
        Returns:
            float: 空间复杂度评分 [0, 1]，越高越好
                1.0 - O(1)
                0.7 - O(n)
                0.5 - O(n²) or worse
        """
        try:
            tree = ast.parse(code)
            creates_list = False
            creates_dict = False
            creates_set = False
            has_recursion = False
            nested_structures = 0
            
            def analyze_space(node):
                nonlocal creates_list, creates_dict, creates_set, has_recursion, nested_structures
                
                # 检测列表创建
                if isinstance(node, (ast.List, ast.ListComp)):
                    creates_list = True
                    # 检测嵌套列表推导
                    if isinstance(node, ast.ListComp):
                        if len(node.generators) > 1:
                            nested_structures += 1
                
                # 检测字典创建
                if isinstance(node, (ast.Dict, ast.DictComp)):
                    creates_dict = True
                
                # 检测集合创建
                if isinstance(node, (ast.Set, ast.SetComp)):
                    creates_set = True
                
                # 检测递归
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name) and child.func.id == func_name:
                                has_recursion = True
                
                for child in ast.iter_child_nodes(node):
                    analyze_space(child)
            
            analyze_space(tree)
            
            # 评分逻辑
            if has_recursion:
                return 0.6  # 递归通常需要 O(n) 空间
            elif nested_structures > 0:
                return 0.5  # 嵌套结构通常是 O(n²)
            elif creates_list or creates_dict or creates_set:
                return 0.7  # 创建数据结构通常是 O(n)
            else:
                return 1.0  # O(1)
        except:
            return 0.7  # 解析失败，返回中等分数
    
    def _calculate_readability_score(self, has_docstring: float, 
                                     has_type_hints: float, code: str) -> float:
        """
        计算代码可读性评分
        
        综合考虑文档字符串、类型注解、变量命名等因素
        
        Args:
            has_docstring: 是否有文档字符串 [0, 1]
            has_type_hints: 是否有类型注解 [0, 1]
            code: Python代码字符串
        
        Returns:
            float: 可读性评分 [0, 1]
        """
        # 基础分数
        base_score = 0.3 * has_docstring + 0.2 * has_type_hints
        
        # 变量命名质量（简单检测：避免单字母变量）
        try:
            tree = ast.parse(code)
            total_vars = 0
            single_char_vars = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    var_name = node.id
                    # 排除常见的单字母变量（i, j, k 用于循环）
                    if var_name not in ['i', 'j', 'k', 'x', 'y', 'z', '_']:
                        total_vars += 1
                        if len(var_name) == 1:
                            single_char_vars += 1
            
            if total_vars > 0:
                naming_score = 1.0 - (single_char_vars / total_vars)
            else:
                naming_score = 0.8  # 没有变量，给个中等分
            
            # 注释比例
            lines = code.split('\n')
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            if code_lines > 0:
                comment_ratio = comment_lines / code_lines
                comment_score = min(1.0, comment_ratio * 3)  # 33%注释为满分
            else:
                comment_score = 0.0
            
            # 综合评分
            readability = (
                base_score +
                0.3 * naming_score +
                0.2 * comment_score
            )
            
            return min(1.0, readability)
        except:
            return base_score  # 解析失败，只返回基础分数
    
    def _check_python_compilation(self, code: str) -> float:
        """
        检查 Python 代码是否能成功编译
        
        Args:
            code: Python 代码字符串
        
        Returns:
            float: 1.0 表示编译成功，0.0 表示编译失败
        """
        if not code:
            return 0.0
        
        try:
            # 方法1：使用 compile() 函数
            compile(code, '<string>', 'exec')
            self._log("✓ Code compiles successfully (compile)")
            return 1.0
        except SyntaxError as e:
            self._log(f"✗ Syntax error: {e}")
        except Exception as e:
            self._log(f"✗ Compilation error: {e}")
        
        # 方法2：使用 ast.parse()（更宽松）
        try:
            ast.parse(code)
            self._log("✓ Code parses successfully (ast.parse)")
            return 1.0
        except SyntaxError as e:
            self._log(f"✗ AST parse error: {e}")
        except Exception as e:
            self._log(f"✗ AST error: {e}")
        
        return 0.0
    
    def get_metric_categories(self) -> Dict[str, list]:
        """
        返回多维度指标分类
        
        Returns:
            Dict[str, list]: 指标分类
        """
        return {
            'functional': [
                'functional_correctness',
                'compilation_success',
                'has_code',
                'test_pass_rate',
                'tests_passed',
                'tests_total'
            ],
            'efficiency': [
                'time_complexity_score',
                'space_complexity_score'
            ],
            'quality': [
                'code_simplicity',
                'code_length',
                'cyclomatic_complexity',
                'nesting_depth'
            ],
            'readability': [
                'readability_score',
                'has_docstring',
                'has_type_hints'
            ]
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """
        返回指标方向（用于排序和可视化）
        
        Returns:
            Dict[str, bool]: True 表示越大越好，False 表示越小越好
        """
        return {
            # 功能维度
            'functional_correctness': True,
            'compilation_success': True,
            'has_code': True,
            'test_pass_rate': True,
            'tests_passed': True,
            'tests_total': None,  # 中性指标
            
            # 效率维度
            'time_complexity_score': True,
            'space_complexity_score': True,
            
            # 质量维度
            'code_simplicity': True,
            'code_length': False,  # 越短越好
            'cyclomatic_complexity': False,  # 越低越好
            'nesting_depth': False,  # 越浅越好
            
            # 可读性维度
            'readability_score': True,
            'has_docstring': True,
            'has_type_hints': True,
        }
    
    def aggregate_scores(self, scores: Dict[str, float], 
                        method: Optional[str] = None) -> Optional[float]:
        """
        聚合代码质量指标（多种方案可选）
        
        方案B的核心理念：保留多维度独立评分，但提供可选的聚合方法
        
        Args:
            scores: 原始指标字典
            method: 聚合方法
                - 'none': 不聚合，返回 None（推荐）
                - 'functional_priority': 功能优先（测试通过率为主）
                - 'balanced': 平衡各维度
                - 'efficiency_priority': 效率优先
                - 'quality_priority': 质量优先
        
        Returns:
            Optional[float]: 聚合分数 [0, 1]，如果 method='none' 则返回 None
        """
        method = method or self.aggregation_method
        
        if method == 'none':
            return None
        
        # 如果没有代码，返回 0
        if scores.get('has_code', 0.0) < 0.5:
            return 0.0
        
        # 提取各维度分数
        functional = scores.get('functional_correctness', 0.0)
        compilation = scores.get('compilation_success', 0.0)
        
        # 效率维度（可能为 None）
        time_eff = scores.get('time_complexity_score')
        space_eff = scores.get('space_complexity_score')
        efficiency = 0.5  # 默认值
        if time_eff is not None and space_eff is not None:
            efficiency = 0.6 * time_eff + 0.4 * space_eff
        
        # 质量维度
        simplicity = scores.get('code_simplicity', 0.5)
        
        # 可读性维度
        readability = scores.get('readability_score', 0.5)
        
        # 根据不同方法聚合
        if method == 'functional_priority':
            # 功能优先：测试通过率70% + 编译30%
            # 质量和效率作为微调（最多±10%）
            base_score = 0.7 * functional + 0.3 * compilation
            quality_bonus = 0.05 * (simplicity + readability + efficiency) / 3
            return min(1.0, base_score + quality_bonus)
        
        elif method == 'balanced':
            # 平衡：功能50% + 效率25% + 质量15% + 可读性10%
            return (
                0.5 * functional +
                0.25 * efficiency +
                0.15 * simplicity +
                0.1 * readability
            )
        
        elif method == 'efficiency_priority':
            # 效率优先：效率50% + 功能30% + 质量20%
            return (
                0.5 * efficiency +
                0.3 * functional +
                0.2 * simplicity
            )
        
        elif method == 'quality_priority':
            # 质量优先：质量40% + 可读性30% + 功能30%
            return (
                0.4 * simplicity +
                0.3 * readability +
                0.3 * functional
            )
        
        else:
            # 默认：不聚合
            return None
    
    def get_dimension_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """
        获取各维度的综合评分
        
        这是方案B的核心：提供维度级别的聚合，而非单一总分
        
        Args:
            scores: 原始指标字典
        
        Returns:
            Dict[str, float]: 各维度评分
                - functional_dimension: 功能维度综合分
                - efficiency_dimension: 效率维度综合分
                - quality_dimension: 质量维度综合分
                - readability_dimension: 可读性维度综合分
        """
        dimension_scores = {}
        
        # 功能维度
        functional = scores.get('functional_correctness', 0.0)
        compilation = scores.get('compilation_success', 0.0)
        dimension_scores['functional_dimension'] = 0.7 * functional + 0.3 * compilation
        
        # 效率维度
        time_eff = scores.get('time_complexity_score')
        space_eff = scores.get('space_complexity_score')
        if time_eff is not None and space_eff is not None:
            dimension_scores['efficiency_dimension'] = 0.6 * time_eff + 0.4 * space_eff
        else:
            dimension_scores['efficiency_dimension'] = None
        
        # 质量维度
        simplicity = scores.get('code_simplicity')
        if simplicity is not None:
            dimension_scores['quality_dimension'] = simplicity
        else:
            dimension_scores['quality_dimension'] = None
        
        # 可读性维度
        readability = scores.get('readability_score')
        if readability is not None:
            dimension_scores['readability_dimension'] = readability
        else:
            dimension_scores['readability_dimension'] = None
        
        return dimension_scores
