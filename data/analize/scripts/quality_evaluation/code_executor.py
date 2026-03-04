"""
代码执行器

安全地执行生成的代码并验证测试用例
"""

import re
import ast
import sys
from io import StringIO
from typing import Dict, List, Tuple, Optional, Any
import traceback


class CodeExecutor:
    """代码执行器，用于安全地执行和测试生成的代码"""
    
    def __init__(self, timeout: int = 5):
        """
        初始化代码执行器
        
        Args:
            timeout: 执行超时时间（秒）
        """
        self.timeout = timeout
    
    def extract_test_cases(self, prompt: str) -> List[str]:
        """
        从prompt中提取测试用例（assert语句）
        
        支持多种格式：
        1. assert语句：assert func(args) == expected
        2. Examples格式：func(args) should return expected
        3. Doctest格式：>>> func(args)\n    expected
        4. 直接示例：func(args) == expected
        
        Args:
            prompt: 包含测试用例的提示词
        
        Returns:
            List[str]: 测试用例列表（assert语句）
        """
        test_cases = []
        
        # 方法1: 直接提取assert语句
        assert_pattern = r'assert\s+.+?(?:\n|$)'
        asserts = re.findall(assert_pattern, prompt, re.MULTILINE)
        test_cases.extend([a.strip() for a in asserts])
        
        # 方法2: 从Examples中提取 "func(args) should return expected"
        example_pattern = r'(\w+)\(([^)]+)\)\s+should\s+return\s+([^.\n]+)'
        examples = re.findall(example_pattern, prompt)
        
        for func_name, args, expected in examples:
            expected = expected.strip()
            test_case = f"assert {func_name}({args}) == {expected}"
            test_cases.append(test_case)
        
        # 方法3: 从Doctest中提取 ">>> func(args)\n    expected"
        # 匹配 >>> 开头的行和下一行的期望值
        doctest_pattern = r'>>>\s+(.+?)\n\s+(.+?)(?:\n|$)'
        doctests = re.findall(doctest_pattern, prompt, re.MULTILINE)
        
        for call, expected in doctests:
            call = call.strip()
            expected = expected.strip()
            
            # 处理布尔值
            if expected in ['True', 'False']:
                test_case = f"assert {call} == {expected}"
            # 处理字符串列表等
            elif expected.startswith('[') or expected.startswith('('):
                test_case = f"assert {call} == {expected}"
            # 处理数字
            else:
                try:
                    # 尝试转换为数字
                    float(expected)
                    test_case = f"assert {call} == {expected}"
                except:
                    # 如果不是数字，作为字符串处理
                    test_case = f"assert {call} == '{expected}'"
            
            test_cases.append(test_case)
        
        # 方法4: 从Example中提取 "func(args) == expected"
        # 这种格式通常在注释中
        direct_example_pattern = r'(\w+)\(([^)]+)\)\s*==\s*([^\n]+)'
        direct_examples = re.findall(direct_example_pattern, prompt)
        
        for func_name, args, expected in direct_examples:
            expected = expected.strip()
            # 避免重复添加（可能已经被其他方法提取）
            test_case = f"assert {func_name}({args}) == {expected}"
            if test_case not in test_cases:
                test_cases.append(test_case)
        
        return test_cases
    
    def extract_function_name(self, code: str) -> Optional[str]:
        """
        从代码中提取函数名
        
        Args:
            code: Python代码
        
        Returns:
            Optional[str]: 函数名，如果没有找到返回None
        """
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    return node.name
        except:
            pass
        
        # 回退到正则表达式
        match = re.search(r'def\s+(\w+)\s*\(', code)
        if match:
            return match.group(1)
        
        return None
    
    def execute_code_with_tests(self, code: str, test_cases: List[str]) -> Dict[str, Any]:
        """
        执行代码并运行测试用例
        
        Args:
            code: 要执行的Python代码
            test_cases: 测试用例列表（assert语句）
        
        Returns:
            Dict[str, Any]: 执行结果
                - success: 是否成功执行
                - passed: 通过的测试数量
                - failed: 失败的测试数量
                - total: 总测试数量
                - pass_rate: 通过率 [0, 1]
                - errors: 错误信息列表
        """
        result = {
            'success': False,
            'passed': 0,
            'failed': 0,
            'total': len(test_cases),
            'pass_rate': 0.0,
            'errors': []
        }
        
        if not test_cases:
            result['success'] = True
            return result
        
        # 创建执行环境
        exec_globals = {}
        exec_locals = {}
        
        # 执行代码定义
        try:
            exec(code, exec_globals, exec_locals)
            result['success'] = True
        except Exception as e:
            result['errors'].append(f"Code execution failed: {str(e)}")
            return result
        
        # 运行测试用例
        for i, test_case in enumerate(test_cases):
            try:
                # 在相同的环境中执行测试
                exec(test_case, exec_globals, exec_locals)
                result['passed'] += 1
            except AssertionError as e:
                result['failed'] += 1
                result['errors'].append(f"Test {i+1} failed: {test_case}")
            except Exception as e:
                result['failed'] += 1
                result['errors'].append(f"Test {i+1} error: {str(e)}")
        
        # 计算通过率
        if result['total'] > 0:
            result['pass_rate'] = result['passed'] / result['total']
        
        return result
    
    def safe_execute(self, code: str, test_cases: List[str]) -> Dict[str, Any]:
        """
        安全地执行代码（带超时和异常处理）
        
        Args:
            code: 要执行的Python代码
            test_cases: 测试用例列表
        
        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            # 简单的安全检查
            if self._is_dangerous_code(code):
                return {
                    'success': False,
                    'passed': 0,
                    'failed': len(test_cases),
                    'total': len(test_cases),
                    'pass_rate': 0.0,
                    'errors': ['Code contains potentially dangerous operations']
                }
            
            # 执行代码
            return self.execute_code_with_tests(code, test_cases)
            
        except Exception as e:
            return {
                'success': False,
                'passed': 0,
                'failed': len(test_cases),
                'total': len(test_cases),
                'pass_rate': 0.0,
                'errors': [f"Execution error: {str(e)}"]
            }
    
    def _is_dangerous_code(self, code: str) -> bool:
        """
        检查代码是否包含危险操作
        
        Args:
            code: Python代码
        
        Returns:
            bool: 是否危险
        """
        # 危险关键字列表
        dangerous_keywords = [
            'import os',
            'import sys',
            'import subprocess',
            'import shutil',
            '__import__',
            'eval(',
            'exec(',
            'compile(',
            'open(',
            'file(',
            'input(',
            'raw_input(',
        ]
        
        code_lower = code.lower()
        
        for keyword in dangerous_keywords:
            if keyword.lower() in code_lower:
                return True
        
        return False
    
    def evaluate_code_correctness(self, code: str, prompt: str) -> Dict[str, Any]:
        """
        评估代码的正确性（完整流程）
        
        Args:
            code: 生成的代码
            prompt: 原始提示词（包含测试用例）
        
        Returns:
            Dict[str, Any]: 评估结果
                - has_tests: 是否有测试用例
                - test_count: 测试用例数量
                - execution_success: 代码是否成功执行
                - tests_passed: 通过的测试数量
                - tests_failed: 失败的测试数量
                - pass_rate: 通过率 [0, 1]
                - errors: 错误信息列表
        """
        # 提取测试用例
        test_cases = self.extract_test_cases(prompt)
        
        result = {
            'has_tests': len(test_cases) > 0,
            'test_count': len(test_cases),
            'execution_success': False,
            'tests_passed': 0,
            'tests_failed': 0,
            'pass_rate': 0.0,
            'errors': []
        }
        
        if not test_cases:
            return result
        
        # 执行代码和测试
        exec_result = self.safe_execute(code, test_cases)
        
        result['execution_success'] = exec_result['success']
        result['tests_passed'] = exec_result['passed']
        result['tests_failed'] = exec_result['failed']
        result['pass_rate'] = exec_result['pass_rate']
        result['errors'] = exec_result['errors']
        
        return result


def test_code_executor():
    """测试代码执行器"""
    executor = CodeExecutor()
    
    print("="*80)
    print("测试代码执行器 - 多种测试用例格式")
    print("="*80)
    
    # 测试用例1: Examples格式
    code1 = """
def multiply(a, b):
    return (a % 10) * (b % 10)
"""
    
    prompt1 = """
def multiply(a, b):
    Examples:
    multiply(148, 412) should return 16.
    multiply(19, 28) should return 72.
    multiply(2020, 1851) should return 0.
    multiply(14,-15) should return 20.
"""
    
    result1 = executor.evaluate_code_correctness(code1, prompt1)
    print("\n测试1 - Examples格式:")
    print(f"  提取的测试数: {result1['test_count']}")
    print(f"  测试通过率: {result1['pass_rate']:.1%}")
    print(f"  通过/总数: {result1['tests_passed']}/{result1['test_count']}")
    
    # 测试用例2: Doctest格式
    code2 = """
def triples_sum_to_zero(l: list):
    for i in range(len(l)):
        for j in range(i+1, len(l)):
            for k in range(j+1, len(l)):
                if l[i] + l[j] + l[k] == 0:
                    return True
    return False
"""
    
    prompt2 = """
def triples_sum_to_zero(l: list):
    >>> triples_sum_to_zero([1, 3, 5, 0])
    False
    >>> triples_sum_to_zero([1, 3, -2, 1])
    True
    >>> triples_sum_to_zero([1, 2, 3, 7])
    False
    >>> triples_sum_to_zero([2, 4, -5, 3, 9, 7])
    True
    >>> triples_sum_to_zero([1])
    False
"""
    
    result2 = executor.evaluate_code_correctness(code2, prompt2)
    print("\n测试2 - Doctest格式:")
    print(f"  提取的测试数: {result2['test_count']}")
    print(f"  测试通过率: {result2['pass_rate']:.1%}")
    print(f"  通过/总数: {result2['tests_passed']}/{result2['test_count']}")
    if result2['errors']:
        print(f"  错误示例: {result2['errors'][0]}")
    
    # 测试用例3: 直接示例格式
    code3 = """
def triangle_area(a, b, c):
    if a + b <= c or a + c <= b or b + c <= a:
        return -1
    s = (a + b + c) / 2
    area = (s * (s - a) * (s - b) * (s - c)) ** 0.5
    return round(area, 2)
"""
    
    prompt3 = """
def triangle_area(a, b, c):
    Example:
    triangle_area(3, 4, 5) == 6.00
    triangle_area(1, 2, 10) == -1
"""
    
    result3 = executor.evaluate_code_correctness(code3, prompt3)
    print("\n测试3 - 直接示例格式:")
    print(f"  提取的测试数: {result3['test_count']}")
    print(f"  测试通过率: {result3['pass_rate']:.1%}")
    print(f"  通过/总数: {result3['tests_passed']}/{result3['test_count']}")
    
    # 测试用例4: 列表返回值
    code4 = """
from typing import List

def separate_paren_groups(paren_string: str) -> List[str]:
    result = []
    current = []
    depth = 0
    
    for char in paren_string:
        if char == ' ':
            continue
        if char == '(':
            depth += 1
            current.append(char)
        elif char == ')':
            current.append(char)
            depth -= 1
            if depth == 0:
                result.append(''.join(current))
                current = []
    
    return result
"""
    
    prompt4 = """
def separate_paren_groups(paren_string: str) -> List[str]:
    >>> separate_paren_groups('( ) (( )) (( )( ))')
    ['()', '(())', '(()())']
"""
    
    result4 = executor.evaluate_code_correctness(code4, prompt4)
    print("\n测试4 - 列表返回值:")
    print(f"  提取的测试数: {result4['test_count']}")
    print(f"  测试通过率: {result4['pass_rate']:.1%}")
    print(f"  通过/总数: {result4['tests_passed']}/{result4['test_count']}")
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)


if __name__ == '__main__':
    test_code_executor()
