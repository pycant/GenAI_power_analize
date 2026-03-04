"""
工具函数

提供评估过程中常用的辅助函数
"""

import re
from typing import Optional, List


def normalize_text(text: str) -> str:
    """
    文本归一化
    
    Args:
        text: 原始文本
    
    Returns:
        str: 归一化后的文本（小写、去除多余空格）
    """
    if not text:
        return ""
    
    # 转小写
    text = text.lower()
    
    # 去除多余空格
    text = ' '.join(text.split())
    
    return text.strip()


def extract_code_blocks(text: str, language: Optional[str] = None) -> List[str]:
    """
    从文本中提取代码块
    
    Args:
        text: 包含代码块的文本
        language: 指定语言（如 'python'），None 表示提取所有代码块
    
    Returns:
        List[str]: 提取的代码块列表
    """
    if not text:
        return []
    
    # 匹配 Markdown 代码块格式：```language\ncode\n```
    if language:
        pattern = rf'```{language}\s*\n(.*?)\n```'
    else:
        pattern = r'```(?:\w+)?\s*\n(.*?)\n```'
    
    code_blocks = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    # 如果没有找到代码块，尝试查找缩进的代码（4个空格或1个tab）
    if not code_blocks:
        lines = text.split('\n')
        current_block = []
        in_code_block = False
        
        for line in lines:
            # 检查是否是代码行（以4个空格或tab开头）
            if line.startswith('    ') or line.startswith('\t'):
                in_code_block = True
                current_block.append(line.lstrip())
            else:
                if in_code_block and current_block:
                    code_blocks.append('\n'.join(current_block))
                    current_block = []
                    in_code_block = False
        
        # 添加最后一个代码块
        if current_block:
            code_blocks.append('\n'.join(current_block))
    
    # 如果还是没有找到，将整个文本作为代码
    if not code_blocks and text.strip():
        code_blocks = [text.strip()]
    
    return code_blocks


def extract_python_code(text: str) -> Optional[str]:
    """
    从文本中提取 Python 代码
    
    Args:
        text: 包含代码的文本
    
    Returns:
        Optional[str]: 提取的 Python 代码，如果没有找到返回 None
    """
    # 首先尝试提取 Python 代码块
    code_blocks = extract_code_blocks(text, 'python')
    
    if code_blocks:
        return code_blocks[0]  # 返回第一个代码块
    
    # 尝试提取通用代码块
    code_blocks = extract_code_blocks(text)
    
    if code_blocks:
        # 检查是否看起来像 Python 代码
        code = code_blocks[0]
        if is_likely_python(code):
            return code
    
    return None


def is_likely_python(code: str) -> bool:
    """
    判断代码是否可能是 Python 代码
    
    Args:
        code: 代码字符串
    
    Returns:
        bool: 是否可能是 Python 代码
    """
    if not code:
        return False
    
    # Python 关键字和常见模式
    python_indicators = [
        r'\bdef\s+\w+\s*\(',  # 函数定义
        r'\bclass\s+\w+',     # 类定义
        r'\bimport\s+\w+',    # import 语句
        r'\bfrom\s+\w+\s+import',  # from...import 语句
        r'\bif\s+.*:',        # if 语句
        r'\bfor\s+\w+\s+in\s+',  # for 循环
        r'\bwhile\s+.*:',     # while 循环
        r'\breturn\s+',       # return 语句
        r'\bprint\s*\(',      # print 函数
    ]
    
    for pattern in python_indicators:
        if re.search(pattern, code):
            return True
    
    return False


def count_code_lines(code: str) -> int:
    """
    计算代码行数（不包括空行和注释）
    
    Args:
        code: 代码字符串
    
    Returns:
        int: 有效代码行数
    """
    if not code:
        return 0
    
    lines = code.split('\n')
    count = 0
    
    for line in lines:
        line = line.strip()
        # 跳过空行和注释行
        if line and not line.startswith('#'):
            count += 1
    
    return count


def calculate_cyclomatic_complexity(code: str) -> int:
    """
    计算圈复杂度（简化版本）
    
    圈复杂度 = 决策点数量 + 1
    决策点包括：if, elif, for, while, and, or, except 等
    
    Args:
        code: 代码字符串
    
    Returns:
        int: 圈复杂度
    """
    if not code:
        return 1
    
    # 决策关键字
    decision_keywords = [
        r'\bif\b',
        r'\belif\b',
        r'\bfor\b',
        r'\bwhile\b',
        r'\band\b',
        r'\bor\b',
        r'\bexcept\b',
        r'\bwith\b',
    ]
    
    complexity = 1  # 基础复杂度
    
    for keyword in decision_keywords:
        complexity += len(re.findall(keyword, code))
    
    return complexity


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 除零时的默认值
    
    Returns:
        float: 除法结果或默认值
    """
    if denominator == 0:
        return default
    return numerator / denominator
