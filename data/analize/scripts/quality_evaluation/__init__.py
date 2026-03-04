"""
质量评估模块

提供针对不同任务类型的质量评估器
"""

from .base_evaluator import BaseEvaluator
from .code_evaluator import CodeEvaluator

__all__ = [
    'BaseEvaluator',
    'CodeEvaluator',
]

__version__ = '1.0.0'
