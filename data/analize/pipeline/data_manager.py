"""
数据管理核心模块 - 统一的数据访问接口
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union
import json
import logging
from datetime import datetime
import warnings

from .schema import DataSchema, PipelineConfig
from .data_validator import DataValidator

logger = logging.getLogger(__name__)


class ExperimentDataManager:
    """实验数据管理器 - 统一数据访问接口"""
    
    def __init__(self, base_path: str = None):
        """
        初始化数据管理器
        
        Args:
            base_path: 基础路径，默认为 'data/analize'
        """
        self.base_path = Path(base_path or PipelineConfig.BASE_PATH)
        self.processed_path = self.base_path / 'processed'
        self.cache_path = self.base_path / 'cache'
        self.schema = DataSchema()
        self.validator = DataValidator()
        
        # 内存缓存
        self._cache = {}
        self._cache_enabled = PipelineConfig.CACHE_ENABLED
        
        # 确保目录存在
        self.processed_path.mkdir(parents=True, exist_ok=True)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"数据管理器初始化完成: {self.base_path}")
    
    def initialize_pipeline(self, force: bool = False):
        """
        初始化数据管道 - 转换所有原始数据
        
        Args:
            force: 是否强制重新转换（即使已存在）
        """
        master_file = self.processed_path / PipelineConfig.MASTER_DATA_FILE
        
        if master_file.exists() and not force:
            logger.info("数据已存在，跳过初始化。使用 force=True 强制重新转换")
            return
        
        logger.info("开始初始化数据管道...")
        
        # 导入转换器（延迟导入避免循环依赖）
        from .data_pipeline import DataPipeline
        
        pipeline = DataPipeline(self.base_path)
        pipeline.run_full_pipeline()
        
        logger.info("数据管道初始化完成")
    
    def load_all_data(self, use_cache: bool = True) -> pd.DataFrame:
        """
        加载所有实验数据
        
        Args:
            use_cache: 是否使用缓存
            
        Returns:
            完整的数据DataFrame
        """
        cache_key = 'all_data'
        
        if use_cache and self._cache_enabled and cache_key in self._cache:
            logger.debug("从缓存加载数据")
            return self._cache[cache_key].copy()
        
        master_file = self.processed_path / PipelineConfig.MASTER_DATA_FILE
        
        if not master_file.exists():
            logger.warning("主数据文件不存在，尝试初始化管道...")
            self.initialize_pipeline()
        
        logger.info(f"加载数据: {master_file}")
        df = pd.read_parquet(master_file)
        
        if self._cache_enabled:
            self._cache[cache_key] = df.copy()
        
        logger.info(f"加载完成: {len(df)} 行, {len(df.columns)} 列")
        return df
    
    def get_by_task(self, task_type: str, use_cache: bool = True) -> pd.DataFrame:
        """
        按任务类型筛选数据
        
        Args:
            task_type: 任务类型 (code, qa, creative, summary, reasoning, math, translation)
            use_cache: 是否使用缓存
            
        Returns:
            筛选后的DataFrame
        """
        if task_type not in self.schema.TASK_TYPES:
            raise ValueError(f"无效的任务类型: {task_type}. 有效值: {self.schema.TASK_TYPES}")
        
        cache_key = f'task_{task_type}'
        
        if use_cache and self._cache_enabled and cache_key in self._cache:
            return self._cache[cache_key].copy()
        
        df = self.load_all_data(use_cache=use_cache)
        df_filtered = df[df['task_type'] == task_type].copy()
        
        if self._cache_enabled:
            self._cache[cache_key] = df_filtered.copy()
        
        logger.info(f"任务 '{task_type}': {len(df_filtered)} 行")
        return df_filtered
    
    def get_by_model(self, model_name: str, use_cache: bool = True) -> pd.DataFrame:
        """
        按模型名称筛选数据
        
        Args:
            model_name: 模型名称
            use_cache: 是否使用缓存
            
        Returns:
            筛选后的DataFrame
        """
        cache_key = f'model_{model_name}'
        
        if use_cache and self._cache_enabled and cache_key in self._cache:
            return self._cache[cache_key].copy()
        
        df = self.load_all_data(use_cache=use_cache)
        df_filtered = df[df['model_name'] == model_name].copy()
        
        if self._cache_enabled:
            self._cache[cache_key] = df_filtered.copy()
        
        logger.info(f"模型 '{model_name}': {len(df_filtered)} 行")
        return df_filtered
    
    def get_quality_metrics(self, task_type: str = None, normalized: bool = True) -> pd.DataFrame:
        """
        获取质量指标
        
        Args:
            task_type: 任务类型（可选，None表示所有任务）
            normalized: 是否返回归一化后的值
            
        Returns:
            质量指标DataFrame
        """
        quality_file = self.processed_path / PipelineConfig.QUALITY_METRICS_FILE
        
        if quality_file.exists():
            df = pd.read_parquet(quality_file)
        else:
            # 从主数据提取
            df = self.load_all_data()
            quality_cols = self.schema.PRIMARY_KEYS.copy()
            
            if task_type:
                df = df[df['task_type'] == task_type]
                quality_cols += self.schema.get_quality_columns(task_type)
            else:
                quality_cols += [col.name for col in self.schema.QUALITY_COLUMNS]
            
            # 只保留存在的列
            quality_cols = [col for col in quality_cols if col in df.columns]
            df = df[quality_cols]
        
        if task_type:
            df = df[df['task_type'] == task_type]
        
        if normalized:
            df = self._normalize_metrics(df, 'quality')
        
        return df
    
    def get_efficiency_metrics(self, normalized: bool = True) -> pd.DataFrame:
        """
        获取效率指标
        
        Args:
            normalized: 是否返回归一化后的值
            
        Returns:
            效率指标DataFrame
        """
        efficiency_file = self.processed_path / PipelineConfig.EFFICIENCY_METRICS_FILE
        
        if efficiency_file.exists():
            df = pd.read_parquet(efficiency_file)
        else:
            # 从主数据提取
            df = self.load_all_data()
            efficiency_cols = self.schema.PRIMARY_KEYS + self.schema.get_efficiency_columns()
            efficiency_cols = [col for col in efficiency_cols if col in df.columns]
            df = df[efficiency_cols]
        
        if normalized:
            df = self._normalize_metrics(df, 'efficiency')
        
        return df
    
    def compute_composite_score(
        self, 
        weights: Dict[str, float] = None,
        by_task: bool = True
    ) -> pd.DataFrame:
        """
        计算复合得分
        
        Args:
            weights: 权重字典 {'quality': 0.5, 'efficiency': 0.5}
            by_task: 是否按任务类型分组计算
            
        Returns:
            包含复合得分的DataFrame
        """
        weights = weights or PipelineConfig.DEFAULT_WEIGHTS
        
        # 验证权重
        if not np.isclose(sum(weights.values()), 1.0):
            logger.warning(f"权重之和不为1: {sum(weights.values())}, 将自动归一化")
            total = sum(weights.values())
            weights = {k: v/total for k, v in weights.items()}
        
        df = self.load_all_data()
        
        # 获取归一化的质量和效率指标
        quality_df = self.get_quality_metrics(normalized=True)
        efficiency_df = self.get_efficiency_metrics(normalized=True)
        
        # 合并数据
        result = df[self.schema.PRIMARY_KEYS].copy()
        
        # 计算平均质量得分
        quality_cols = [col for col in quality_df.columns 
                       if col not in self.schema.PRIMARY_KEYS and col.startswith('norm_')]
        if quality_cols:
            result['quality_score'] = quality_df[quality_cols].mean(axis=1)
        
        # 计算效率得分
        eff_weights = PipelineConfig.EFFICIENCY_WEIGHTS
        if 'norm_toks_per_s' in efficiency_df.columns:
            result['efficiency_score'] = (
                eff_weights['throughput'] * efficiency_df['norm_toks_per_s'] +
                eff_weights['latency'] * (1 - efficiency_df['norm_latency_s']) +
                eff_weights['energy'] * (1 - efficiency_df['norm_gpu_energy_j'])
            )
        
        # 计算复合得分
        if 'quality_score' in result.columns and 'efficiency_score' in result.columns:
            result['composite_score'] = (
                weights['quality'] * result['quality_score'] +
                weights['efficiency'] * result['efficiency_score']
            )
            
            # 计算质效比
            result['qe_ratio'] = (
                (result['quality_score'] + 0.01) / 
                (1.01 - result['efficiency_score'])
            )
        
        return result
    
    def _normalize_metrics(self, df: pd.DataFrame, metric_type: str) -> pd.DataFrame:
        """
        归一化指标
        
        Args:
            df: 数据DataFrame
            metric_type: 'quality' 或 'efficiency'
            
        Returns:
            归一化后的DataFrame
        """
        df = df.copy()
        
        # 确定要归一化的列
        if metric_type == 'quality':
            cols_to_norm = [col for col in df.columns 
                           if col not in self.schema.PRIMARY_KEYS 
                           and df[col].dtype in ['float32', 'float64']]
        else:  # efficiency
            cols_to_norm = self.schema.get_efficiency_columns()
            cols_to_norm = [col for col in cols_to_norm if col in df.columns]
        
        # 按任务分组归一化
        if PipelineConfig.NORMALIZATION_BY_TASK and 'task_type' in df.columns:
            for task in df['task_type'].unique():
                mask = df['task_type'] == task
                for col in cols_to_norm:
                    if col in df.columns:
                        values = df.loc[mask, col]
                        if values.notna().any():
                            df.loc[mask, f'norm_{col}'] = self._minmax_normalize(values)
        else:
            # 全局归一化
            for col in cols_to_norm:
                if col in df.columns:
                    df[f'norm_{col}'] = self._minmax_normalize(df[col])
        
        return df
    
    @staticmethod
    def _minmax_normalize(series: pd.Series) -> pd.Series:
        """Min-Max归一化"""
        min_val = series.min()
        max_val = series.max()
        
        if max_val == min_val:
            return pd.Series(0.5, index=series.index)
        
        return (series - min_val) / (max_val - min_val)
    
    def get_summary_stats(self, by: str = 'model') -> pd.DataFrame:
        """
        获取汇总统计
        
        Args:
            by: 分组依据 ('model', 'task', 'model_task')
            
        Returns:
            汇总统计DataFrame
        """
        df = self.load_all_data()
        
        if by == 'model':
            group_cols = ['model_name']
        elif by == 'task':
            group_cols = ['task_type']
        elif by == 'model_task':
            group_cols = ['model_name', 'task_type']
        else:
            raise ValueError(f"无效的分组依据: {by}")
        
        # 计算统计量
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats = df.groupby(group_cols)[numeric_cols].agg(['mean', 'std', 'min', 'max', 'count'])
        
        return stats
    
    def list_models(self) -> List[str]:
        """列出所有模型"""
        df = self.load_all_data()
        return sorted(df['model_name'].unique().tolist())
    
    def list_tasks(self) -> List[str]:
        """列出所有任务类型"""
        df = self.load_all_data()
        return sorted(df['task_type'].unique().tolist())
    
    def refresh_data(self):
        """刷新数据 - 重新扫描并转换"""
        logger.info("刷新数据...")
        self.clear_cache()
        self.initialize_pipeline(force=True)
    
    def clear_cache(self):
        """清理缓存"""
        self._cache.clear()
        logger.info("缓存已清理")
    
    def validate_data(self) -> bool:
        """验证数据完整性"""
        master_file = self.processed_path / PipelineConfig.MASTER_DATA_FILE
        
        if not master_file.exists():
            logger.error("主数据文件不存在")
            return False
        
        is_valid, errors, warnings = self.validator.validate_file(master_file)
        self.validator.print_validation_report()
        
        return is_valid
    
    def get_metadata(self) -> Dict:
        """获取元数据"""
        metadata_file = self.processed_path / PipelineConfig.METADATA_FILE
        
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 生成元数据
        df = self.load_all_data()
        metadata = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'models': self.list_models(),
            'tasks': self.list_tasks(),
            'date_range': {
                'start': df['timestamp'].min().isoformat() if 'timestamp' in df.columns else None,
                'end': df['timestamp'].max().isoformat() if 'timestamp' in df.columns else None,
            },
            'last_updated': datetime.now().isoformat(),
        }
        
        # 保存元数据
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return metadata
    
    def __repr__(self):
        return f"ExperimentDataManager(base_path='{self.base_path}')"


if __name__ == '__main__':
    # 示例用法
    logging.basicConfig(level=logging.INFO)
    
    dm = ExperimentDataManager()
    
    # 初始化（首次运行）
    # dm.initialize_pipeline()
    
    # 加载数据
    df = dm.load_all_data()
    print(f"\n总数据: {len(df)} 行")
    
    # 按任务筛选
    df_code = dm.get_by_task('code')
    print(f"代码任务: {len(df_code)} 行")
    
    # 获取质量指标
    quality = dm.get_quality_metrics(task_type='code', normalized=True)
    print(f"\n质量指标: {quality.shape}")
    
    # 计算复合得分
    scores = dm.compute_composite_score()
    print(f"\n复合得分: {scores.shape}")
    
    # 元数据
    metadata = dm.get_metadata()
    print(f"\n元数据: {json.dumps(metadata, indent=2, ensure_ascii=False)}")
