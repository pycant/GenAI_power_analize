"""
基础评估器接口

定义所有任务评估器的基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseEvaluator(ABC):
    """质量评估器基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化评估器
        
        Args:
            config: 配置字典，可包含：
                - aggregation: 聚合方法 ('none', 'entropy', 'pca', 'topsis')
                - device: 计算设备 ('cpu', 'cuda')
                - verbose: 是否输出详细信息
        """
        self.config = config or {}
        self.aggregation_method = self.config.get('aggregation', 'none')
        self.device = self.config.get('device', 'cpu')
        self.verbose = self.config.get('verbose', False)
    
    @abstractmethod
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict[str, Any] = None) -> Dict[str, float]:
        """
        评估生成文本质量，返回多维度指标
        
        Args:
            generated: 生成的文本
            reference: 参考答案（可选）
            context: 额外上下文信息（如原始问题、测试用例等）
        
        Returns:
            Dict[str, float]: 多维度指标字典
                - 所有指标值为 float 或 None
                - None 表示该指标不适用或计算失败
        """
        pass
    
    def get_metric_categories(self) -> Dict[str, List[str]]:
        """
        返回指标分类
        
        Returns:
            Dict[str, List[str]]: 指标分类字典
                如 {'accuracy': ['exact_match', 'f1'], 'semantic': ['bertscore']}
        """
        return {}
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """
        返回指标方向（True=越大越好，False=越小越好）
        
        Returns:
            Dict[str, bool]: 指标方向字典
                如 {'exact_match': True, 'perplexity': False}
        """
        return {}
    
    def aggregate_scores(self, scores: Dict[str, float], 
                        method: Optional[str] = None) -> Optional[float]:
        """
        聚合多个指标为单一分数（可选）
        
        Args:
            scores: 原始指标字典
            method: 聚合方法，None 表示不聚合
        
        Returns:
            Optional[float]: 聚合分数，或 None（不聚合）
        """
        method = method or self.aggregation_method
        
        if method == 'none':
            return None
        
        # 过滤有效指标（非 None 值）
        valid_scores = {k: v for k, v in scores.items() if v is not None}
        
        if not valid_scores:
            return None
        
        # 简单平均（基础实现）
        if method == 'mean':
            return sum(valid_scores.values()) / len(valid_scores)
        
        # 其他聚合方法需要在子类中实现或使用专门的聚合模块
        return None
    
    def _log(self, message: str):
        """输出日志信息"""
        if self.verbose:
            print(f"[{self.__class__.__name__}] {message}")
