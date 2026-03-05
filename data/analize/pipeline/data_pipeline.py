"""
ETL数据管道 - 将原始数据转换为标准化格式
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime

from .schema import DataSchema, PipelineConfig

logger = logging.getLogger(__name__)


class DataPipeline:
    """数据转换管道"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or PipelineConfig.BASE_PATH)
        self.raw_path = self.base_path / 'pre_data'
        self.results_path = self.base_path / 'results'
        self.processed_path = self.base_path / 'processed'
        self.schema = DataSchema()
        
        # 确保输出目录存在
        self.processed_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"数据管道初始化: {self.base_path}")
    
    def run_full_pipeline(self):
        """运行完整的ETL管道"""
        logger.info("="*60)
        logger.info("开始运行数据管道")
        logger.info("="*60)
        
        start_time = datetime.now()
        
        try:
            # 1. 加载原始数据
            logger.info("\n[1/5] 加载原始数据...")
            raw_data = self._load_raw_data()
            logger.info(f"  ✓ 加载完成: {len(raw_data)} 行")
            
            # 2. 清洗和标准化
            logger.info("\n[2/5] 清洗和标准化...")
            cleaned_data = self._clean_and_standardize(raw_data)
            logger.info(f"  ✓ 清洗完成: {len(cleaned_data)} 行")
            
            # 3. 计算派生指标
            logger.info("\n[3/5] 计算派生指标...")
            enriched_data = self._compute_derived_metrics(cleaned_data)
            logger.info(f"  ✓ 计算完成: {len(enriched_data.columns)} 列")
            
            # 4. 保存主数据
            logger.info("\n[4/5] 保存主数据...")
            self._save_master_data(enriched_data)
            logger.info(f"  ✓ 保存完成")
            
            # 5. 生成分析数据
            logger.info("\n[5/5] 生成分析数据...")
            self._generate_analysis_data(enriched_data)
            logger.info(f"  ✓ 生成完成")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info("\n" + "="*60)
            logger.info(f"数据管道完成 (耗时: {elapsed:.2f}秒)")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"数据管道失败: {str(e)}", exc_info=True)
            raise
    
    def _load_raw_data(self) -> pd.DataFrame:
        """加载原始数据"""
        dfs = []
        
        # 1. 加载原始实验JSON数据（新增）
        try:
            from .converters import SummaryJsonLoader
            logger.info("  加载原始实验数据 (summary.json)...")
            summary_loader = SummaryJsonLoader(base_path=self.base_path.parent)
            df_summary = summary_loader.load_all_summary_data()
            if not df_summary.empty:
                logger.info(f"    ✓ 加载 {len(df_summary)} 条实验记录")
                dfs.append(df_summary)
        except Exception as e:
            logger.warning(f"  加载实验JSON数据失败: {e}")
        
        # 2. 加载 responses_raw.csv
        responses_file = self.raw_path / 'responses_raw.csv'
        if responses_file.exists():
            logger.info(f"  加载: {responses_file.name}")
            df = pd.read_csv(responses_file)
            dfs.append(df)
        
        # 3. 加载 comparison_matrices 下的数据
        matrices_path = self.raw_path / 'comparison_matrices'
        if matrices_path.exists():
            for task_dir in matrices_path.iterdir():
                if task_dir.is_dir():
                    for csv_file in task_dir.glob('*.csv'):
                        logger.info(f"  加载: {task_dir.name}/{csv_file.name}")
                        df = pd.read_csv(csv_file)
                        if 'task_type' not in df.columns:
                            df['task_type'] = task_dir.name
                        dfs.append(df)
        
        # 4. 加载 results 下的质量评估结果
        if self.results_path.exists():
            for task_dir in self.results_path.iterdir():
                if task_dir.is_dir():
                    for csv_file in task_dir.glob('quality_summary_*.csv'):
                        logger.info(f"  加载: {task_dir.name}/{csv_file.name}")
                        df = pd.read_csv(csv_file)
                        if 'task_type' not in df.columns:
                            # 从文件名推断任务类型
                            task = csv_file.stem.replace('quality_summary_', '')
                            df['task_type'] = task
                        dfs.append(df)
        
        if not dfs:
            raise FileNotFoundError("未找到任何数据文件")
        
        # 合并所有数据
        combined = pd.concat(dfs, ignore_index=True)
        
        return combined
    
    def _clean_and_standardize(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗和标准化数据"""
        df = df.copy()
        
        # 1. 标准化列名（转小写，替换空格）
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # 2. 标准化模型名称
        if 'model_name' in df.columns:
            df['model_name'] = df['model_name'].str.lower().str.strip()
        elif 'model' in df.columns:
            df['model_name'] = df['model'].str.lower().str.strip()
            df = df.drop('model', axis=1)
        
        # 3. 标准化任务类型
        if 'task_type' in df.columns:
            df['task_type'] = df['task_type'].str.lower().str.strip()
        elif 'task' in df.columns:
            df['task_type'] = df['task'].str.lower().str.strip()
            df = df.drop('task', axis=1)
        
        # 4. 确保主键列存在
        for pk in self.schema.PRIMARY_KEYS:
            if pk not in df.columns:
                if pk == 'prompt_id' and 'prompt' in df.columns:
                    # 从prompt列生成ID
                    df['prompt_id'] = pd.factorize(df['prompt'])[0]
                elif pk == 'run_id':
                    df['run_id'] = 0  # 默认运行ID
        
        # 5. 转换数据类型
        df = self._convert_dtypes(df)
        
        # 6. 处理缺失值
        df = self._handle_missing_values(df)
        
        # 7. 去重
        pk_cols = [col for col in self.schema.PRIMARY_KEYS if col in df.columns]
        if pk_cols:
            df = df.drop_duplicates(subset=pk_cols, keep='last')
        
        return df
    
    def _convert_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换数据类型"""
        df = df.copy()
        
        # Category类型
        for col in ['model_name', 'task_type']:
            if col in df.columns:
                df[col] = df[col].astype('category')
        
        # 数值类型
        numeric_cols = {
            'latency_s': 'float32',
            'toks_per_s': 'float32',
            'gpu_energy_j': 'float32',
            'cpu_usage': 'float32',
            'memory_usage': 'float32',
            'bartscore': 'float32',
            'distinct_2': 'float32',
            'quality_score': 'float32',
            'prompt_id': 'int32',
            'run_id': 'int32',
        }
        
        for col, dtype in numeric_cols.items():
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype)
                except Exception as e:
                    logger.warning(f"无法转换列 '{col}' 为 {dtype}: {e}")
        
        # 布尔类型
        bool_cols = ['code_compiles', 'final_answer_correct']
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        df = df.copy()
        
        # 对于效率指标，缺失值填充为中位数
        efficiency_cols = ['latency_s', 'toks_per_s', 'gpu_energy_j']
        for col in efficiency_cols:
            if col in df.columns and df[col].isna().any():
                median = df[col].median()
                df[col] = df[col].fillna(median)
                logger.info(f"  列 '{col}' 缺失值填充为中位数: {median:.2f}")
        
        # 对于质量指标，保留缺失值（不同任务有不同指标）
        
        return df
    
    def _compute_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算派生指标"""
        df = df.copy()
        
        # 按任务分组计算归一化指标
        if 'task_type' in df.columns:
            for task in df['task_type'].unique():
                mask = df['task_type'] == task
                
                # 归一化效率指标
                if 'toks_per_s' in df.columns:
                    df.loc[mask, 'norm_toks_per_s'] = self._normalize(df.loc[mask, 'toks_per_s'])
                
                if 'latency_s' in df.columns:
                    df.loc[mask, 'norm_latency_s'] = self._normalize(df.loc[mask, 'latency_s'])
                
                if 'gpu_energy_j' in df.columns:
                    df.loc[mask, 'norm_gpu_energy_j'] = self._normalize(df.loc[mask, 'gpu_energy_j'])
                
                # 归一化质量指标
                quality_cols = self.schema.get_quality_columns(task)
                for col in quality_cols:
                    if col in df.columns:
                        df.loc[mask, f'norm_{col}'] = self._normalize(df.loc[mask, col])
        
        # 计算效率得分
        if all(col in df.columns for col in ['norm_toks_per_s', 'norm_latency_s', 'norm_gpu_energy_j']):
            weights = PipelineConfig.EFFICIENCY_WEIGHTS
            df['efficiency_score'] = (
                weights['throughput'] * df['norm_toks_per_s'] +
                weights['latency'] * (1 - df['norm_latency_s']) +
                weights['energy'] * (1 - df['norm_gpu_energy_j'])
            )
        
        # 计算综合质量得分（取所有归一化质量指标的平均）
        norm_quality_cols = [col for col in df.columns if col.startswith('norm_') and 'quality' in col or 'bartscore' in col or 'distinct' in col]
        if norm_quality_cols:
            df['norm_quality'] = df[norm_quality_cols].mean(axis=1)
        
        # 计算质效比
        if 'norm_quality' in df.columns and 'efficiency_score' in df.columns:
            df['qe_ratio'] = (df['norm_quality'] + 0.01) / (1.01 - df['efficiency_score'])
        
        return df
    
    @staticmethod
    def _normalize(series: pd.Series) -> pd.Series:
        """Min-Max归一化"""
        min_val = series.min()
        max_val = series.max()
        
        if pd.isna(min_val) or pd.isna(max_val) or max_val == min_val:
            return pd.Series(0.5, index=series.index)
        
        return (series - min_val) / (max_val - min_val)
    
    def _save_master_data(self, df: pd.DataFrame):
        """保存主数据"""
        output_file = self.processed_path / PipelineConfig.MASTER_DATA_FILE
        
        # 优化存储：使用category类型
        for col in ['model_name', 'task_type']:
            if col in df.columns and df[col].dtype != 'category':
                df[col] = df[col].astype('category')
        
        # 保存为Parquet格式
        df.to_parquet(
            output_file,
            engine='pyarrow',
            compression='snappy',
            index=False
        )
        
        file_size = output_file.stat().st_size / 1024 / 1024
        logger.info(f"  保存主数据: {output_file.name} ({file_size:.2f} MB)")
    
    def _generate_analysis_data(self, df: pd.DataFrame):
        """生成分析数据"""
        
        # 1. 质量指标表
        quality_cols = self.schema.PRIMARY_KEYS.copy()
        quality_cols += [col for col in df.columns if 'quality' in col or 'bartscore' in col or 'distinct' in col or 'rouge' in col]
        quality_cols = [col for col in quality_cols if col in df.columns]
        
        if quality_cols:
            quality_df = df[quality_cols].copy()
            output_file = self.processed_path / PipelineConfig.QUALITY_METRICS_FILE
            quality_df.to_parquet(output_file, engine='pyarrow', compression='snappy', index=False)
            logger.info(f"  生成质量指标表: {output_file.name}")
        
        # 2. 效率指标表
        efficiency_cols = self.schema.PRIMARY_KEYS.copy()
        efficiency_cols += self.schema.get_efficiency_columns()
        efficiency_cols += [col for col in df.columns if col.startswith('norm_') and any(e in col for e in ['latency', 'toks', 'energy'])]
        efficiency_cols = [col for col in efficiency_cols if col in df.columns]
        
        if efficiency_cols:
            efficiency_df = df[efficiency_cols].copy()
            output_file = self.processed_path / PipelineConfig.EFFICIENCY_METRICS_FILE
            efficiency_df.to_parquet(output_file, engine='pyarrow', compression='snappy', index=False)
            logger.info(f"  生成效率指标表: {output_file.name}")
        
        # 3. 按任务汇总
        task_summaries_path = self.processed_path / 'task_summaries'
        task_summaries_path.mkdir(exist_ok=True)
        
        if 'task_type' in df.columns:
            for task in df['task_type'].unique():
                task_df = df[df['task_type'] == task].copy()
                output_file = task_summaries_path / f'{task}_summary.parquet'
                task_df.to_parquet(output_file, engine='pyarrow', compression='snappy', index=False)
                logger.info(f"  生成任务汇总: {output_file.name} ({len(task_df)} 行)")
        
        # 4. 元数据
        metadata = {
            'pipeline_version': '1.0',
            'created_at': datetime.now().isoformat(),
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'models': sorted(df['model_name'].unique().tolist()) if 'model_name' in df.columns else [],
            'tasks': sorted(df['task_type'].unique().tolist()) if 'task_type' in df.columns else [],
            'columns': df.columns.tolist(),
        }
        
        metadata_file = self.processed_path / PipelineConfig.METADATA_FILE
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  生成元数据: {metadata_file.name}")


if __name__ == '__main__':
    # 运行管道
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    pipeline = DataPipeline()
    pipeline.run_full_pipeline()
