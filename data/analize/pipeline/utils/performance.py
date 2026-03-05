"""
性能优化工具
"""
import time
import functools
import pandas as pd
import numpy as np
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


def measure_time(func: Callable) -> Callable:
    """
    装饰器：测量函数执行时间
    
    Usage:
        @measure_time
        def my_function():
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        logger.info(f"函数 '{func.__name__}' 执行时间: {elapsed:.2f}秒")
        return result
    
    return wrapper


def optimize_dataframe(df: pd.DataFrame, aggressive: bool = False) -> pd.DataFrame:
    """
    优化DataFrame内存使用
    
    Args:
        df: 输入DataFrame
        aggressive: 是否使用激进优化（可能损失精度）
        
    Returns:
        优化后的DataFrame
    """
    df = df.copy()
    
    original_size = df.memory_usage(deep=True).sum() / 1024 / 1024
    
    # 1. 优化整数类型
    for col in df.select_dtypes(include=['int']).columns:
        col_min = df[col].min()
        col_max = df[col].max()
        
        if col_min >= 0:
            # 无符号整数
            if col_max < 255:
                df[col] = df[col].astype('uint8')
            elif col_max < 65535:
                df[col] = df[col].astype('uint16')
            elif col_max < 4294967295:
                df[col] = df[col].astype('uint32')
        else:
            # 有符号整数
            if col_min > -128 and col_max < 127:
                df[col] = df[col].astype('int8')
            elif col_min > -32768 and col_max < 32767:
                df[col] = df[col].astype('int16')
            elif col_min > -2147483648 and col_max < 2147483647:
                df[col] = df[col].astype('int32')
    
    # 2. 优化浮点类型
    for col in df.select_dtypes(include=['float']).columns:
        if aggressive:
            # 激进模式：使用float16（可能损失精度）
            df[col] = df[col].astype('float16')
        else:
            # 保守模式：使用float32
            df[col] = df[col].astype('float32')
    
    # 3. 优化对象类型为category
    for col in df.select_dtypes(include=['object']).columns:
        num_unique = df[col].nunique()
        num_total = len(df[col])
        
        # 如果唯一值少于50%，转换为category
        if num_unique / num_total < 0.5:
            df[col] = df[col].astype('category')
    
    optimized_size = df.memory_usage(deep=True).sum() / 1024 / 1024
    reduction = (1 - optimized_size / original_size) * 100
    
    logger.info(f"DataFrame优化: {original_size:.2f}MB -> {optimized_size:.2f}MB "
                f"(减少 {reduction:.1f}%)")
    
    return df


def batch_process(data: pd.DataFrame, func: Callable, batch_size: int = 1000) -> pd.DataFrame:
    """
    分批处理大型DataFrame
    
    Args:
        data: 输入DataFrame
        func: 处理函数，接受DataFrame返回DataFrame
        batch_size: 批次大小
        
    Returns:
        处理后的DataFrame
    """
    results = []
    total_batches = (len(data) + batch_size - 1) // batch_size
    
    logger.info(f"开始分批处理: {len(data)} 行, {total_batches} 批次")
    
    for i in range(0, len(data), batch_size):
        batch = data.iloc[i:i+batch_size]
        result = func(batch)
        results.append(result)
        
        if (i // batch_size + 1) % 10 == 0:
            logger.info(f"  处理进度: {i // batch_size + 1}/{total_batches}")
    
    return pd.concat(results, ignore_index=True)


def profile_memory(df: pd.DataFrame, detailed: bool = False) -> dict:
    """
    分析DataFrame内存使用
    
    Args:
        df: 输入DataFrame
        detailed: 是否显示详细信息
        
    Returns:
        内存使用统计
    """
    memory_usage = df.memory_usage(deep=True)
    total_mb = memory_usage.sum() / 1024 / 1024
    
    stats = {
        'total_mb': total_mb,
        'rows': len(df),
        'columns': len(df.columns),
        'mb_per_row': total_mb / len(df) if len(df) > 0 else 0,
    }
    
    if detailed:
        # 按列统计
        col_stats = []
        for col in df.columns:
            col_memory = memory_usage[col] / 1024 / 1024
            col_stats.append({
                'column': col,
                'dtype': str(df[col].dtype),
                'memory_mb': col_memory,
                'percent': col_memory / total_mb * 100,
            })
        
        # 按内存使用排序
        col_stats.sort(key=lambda x: x['memory_mb'], reverse=True)
        stats['columns_detail'] = col_stats
    
    return stats


def suggest_optimizations(df: pd.DataFrame) -> list:
    """
    建议DataFrame优化方案
    
    Args:
        df: 输入DataFrame
        
    Returns:
        优化建议列表
    """
    suggestions = []
    
    # 1. 检查整数类型
    for col in df.select_dtypes(include=['int64']).columns:
        col_max = df[col].max()
        if col_max < 2147483647:
            suggestions.append(f"列 '{col}' 可以从 int64 降级为 int32")
    
    # 2. 检查浮点类型
    for col in df.select_dtypes(include=['float64']).columns:
        suggestions.append(f"列 '{col}' 可以从 float64 降级为 float32")
    
    # 3. 检查对象类型
    for col in df.select_dtypes(include=['object']).columns:
        num_unique = df[col].nunique()
        num_total = len(df[col])
        
        if num_unique / num_total < 0.5:
            suggestions.append(
                f"列 '{col}' 有 {num_unique} 个唯一值 ({num_unique/num_total*100:.1f}%)，"
                f"可以转换为 category 类型"
            )
    
    # 4. 检查重复行
    num_duplicates = df.duplicated().sum()
    if num_duplicates > 0:
        suggestions.append(f"发现 {num_duplicates} 行重复数据，可以去重")
    
    return suggestions


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.timings = {}
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start_time
    
    def checkpoint(self, name: str):
        """记录检查点"""
        if not hasattr(self, 'start_time'):
            self.start_time = time.time()
        
        elapsed = time.time() - self.start_time
        self.timings[name] = elapsed
        logger.info(f"检查点 '{name}': {elapsed:.2f}秒")
    
    def report(self):
        """生成性能报告"""
        if not self.timings:
            logger.info("无性能数据")
            return
        
        logger.info("\n" + "="*60)
        logger.info("性能报告")
        logger.info("="*60)
        
        for name, elapsed in self.timings.items():
            logger.info(f"  {name}: {elapsed:.2f}秒")
        
        total = max(self.timings.values()) if self.timings else 0
        logger.info(f"\n  总计: {total:.2f}秒")
        logger.info("="*60)


if __name__ == '__main__':
    # 测试性能工具
    logging.basicConfig(level=logging.INFO)
    
    # 创建测试数据
    df = pd.DataFrame({
        'id': range(10000),
        'category': np.random.choice(['A', 'B', 'C'], 10000),
        'value': np.random.randn(10000),
        'score': np.random.randint(0, 100, 10000),
    })
    
    print("\n原始DataFrame:")
    print(profile_memory(df, detailed=True))
    
    print("\n优化建议:")
    for suggestion in suggest_optimizations(df):
        print(f"  - {suggestion}")
    
    print("\n优化后:")
    df_optimized = optimize_dataframe(df)
    print(profile_memory(df_optimized, detailed=True))
