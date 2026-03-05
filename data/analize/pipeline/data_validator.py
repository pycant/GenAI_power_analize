"""
数据验证模块 - 确保数据完整性和一致性
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

from .schema import DataSchema, ColumnSchema

logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.schema = DataSchema()
        self.errors = []
        self.warnings = []
    
    def validate_dataframe(self, df: pd.DataFrame, task_type: str = None) -> Tuple[bool, List[str], List[str]]:
        """
        验证DataFrame
        
        Returns:
            (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # 1. 检查必需列
        self._check_required_columns(df, task_type)
        
        # 2. 检查数据类型
        self._check_data_types(df, task_type)
        
        # 3. 检查主键唯一性
        self._check_primary_key_uniqueness(df)
        
        # 4. 检查数值范围
        self._check_value_ranges(df, task_type)
        
        # 5. 检查缺失值
        self._check_missing_values(df, task_type)
        
        # 6. 检查任务类型一致性
        if 'task_type' in df.columns:
            self._check_task_types(df)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _check_required_columns(self, df: pd.DataFrame, task_type: str = None):
        """检查必需列"""
        required = set(self.schema.get_required_columns(task_type))
        actual = set(df.columns)
        missing = required - actual
        
        if missing:
            self.errors.append(f"缺少必需列: {missing}")
    
    def _check_data_types(self, df: pd.DataFrame, task_type: str = None):
        """检查数据类型"""
        dtype_dict = self.schema.get_dtype_dict(task_type)
        
        for col, expected_dtype in dtype_dict.items():
            if col not in df.columns:
                continue
            
            actual_dtype = str(df[col].dtype)
            
            # 简化类型比较
            if expected_dtype == 'category' and actual_dtype != 'category':
                self.warnings.append(f"列 '{col}' 应为category类型，当前为 {actual_dtype}")
            elif expected_dtype.startswith('float') and not actual_dtype.startswith('float'):
                self.warnings.append(f"列 '{col}' 应为float类型，当前为 {actual_dtype}")
            elif expected_dtype.startswith('int') and not actual_dtype.startswith('int'):
                self.warnings.append(f"列 '{col}' 应为int类型，当前为 {actual_dtype}")
    
    def _check_primary_key_uniqueness(self, df: pd.DataFrame):
        """检查主键唯一性"""
        pk_cols = [col for col in self.schema.PRIMARY_KEYS if col in df.columns]
        
        if len(pk_cols) < len(self.schema.PRIMARY_KEYS):
            self.warnings.append(f"主键列不完整: 需要 {self.schema.PRIMARY_KEYS}, 实际 {pk_cols}")
            return
        
        duplicates = df.duplicated(subset=pk_cols, keep=False)
        if duplicates.any():
            n_dups = duplicates.sum()
            self.errors.append(f"发现 {n_dups} 行主键重复")
            
            # 显示前几个重复的主键
            dup_keys = df[duplicates][pk_cols].drop_duplicates().head(5)
            self.errors.append(f"重复主键示例:\n{dup_keys}")
    
    def _check_value_ranges(self, df: pd.DataFrame, task_type: str = None):
        """检查数值范围"""
        columns = self.schema.get_all_columns(task_type)
        
        for col_schema in columns:
            col = col_schema.name
            if col not in df.columns or col_schema.valid_range is None:
                continue
            
            min_val, max_val = col_schema.valid_range
            out_of_range = (df[col] < min_val) | (df[col] > max_val)
            
            if out_of_range.any():
                n_invalid = out_of_range.sum()
                actual_min = df[col].min()
                actual_max = df[col].max()
                self.warnings.append(
                    f"列 '{col}' 有 {n_invalid} 个值超出范围 [{min_val}, {max_val}], "
                    f"实际范围 [{actual_min:.2f}, {actual_max:.2f}]"
                )
    
    def _check_missing_values(self, df: pd.DataFrame, task_type: str = None):
        """检查缺失值"""
        required_cols = self.schema.get_required_columns(task_type)
        
        for col in required_cols:
            if col not in df.columns:
                continue
            
            missing = df[col].isna().sum()
            if missing > 0:
                pct = missing / len(df) * 100
                self.errors.append(f"必需列 '{col}' 有 {missing} ({pct:.1f}%) 个缺失值")
        
        # 检查非必需列的缺失值（仅警告）
        all_cols = set(df.columns) - set(required_cols)
        for col in all_cols:
            missing = df[col].isna().sum()
            if missing > 0:
                pct = missing / len(df) * 100
                if pct > 50:  # 超过50%缺失才警告
                    self.warnings.append(f"列 '{col}' 有 {missing} ({pct:.1f}%) 个缺失值")
    
    def _check_task_types(self, df: pd.DataFrame):
        """检查任务类型一致性"""
        valid_tasks = set(self.schema.TASK_TYPES)
        actual_tasks = set(df['task_type'].unique())
        invalid_tasks = actual_tasks - valid_tasks
        
        if invalid_tasks:
            self.errors.append(f"发现无效的任务类型: {invalid_tasks}")
            self.errors.append(f"有效任务类型: {valid_tasks}")
    
    def validate_file(self, file_path: Path, task_type: str = None) -> Tuple[bool, List[str], List[str]]:
        """验证文件"""
        try:
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                return False, [f"不支持的文件格式: {file_path.suffix}"], []
            
            return self.validate_dataframe(df, task_type)
        
        except Exception as e:
            return False, [f"读取文件失败: {str(e)}"], []
    
    def print_validation_report(self):
        """打印验证报告"""
        print("\n" + "="*60)
        print("数据验证报告")
        print("="*60)
        
        if not self.errors and not self.warnings:
            print("✓ 数据验证通过，未发现问题")
        else:
            if self.errors:
                print(f"\n❌ 错误 ({len(self.errors)}):")
                for i, error in enumerate(self.errors, 1):
                    print(f"  {i}. {error}")
            
            if self.warnings:
                print(f"\n⚠ 警告 ({len(self.warnings)}):")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"  {i}. {warning}")
        
        print("="*60 + "\n")


def validate_all(base_path: str = 'data/analize') -> Dict[str, Tuple[bool, List[str], List[str]]]:
    """
    验证所有数据文件
    
    Returns:
        {file_name: (is_valid, errors, warnings)}
    """
    base_path = Path(base_path)
    validator = DataValidator()
    results = {}
    
    # 验证processed目录下的文件
    processed_path = base_path / 'processed'
    if processed_path.exists():
        for file_path in processed_path.glob('*.parquet'):
            print(f"\n验证文件: {file_path.name}")
            is_valid, errors, warnings = validator.validate_file(file_path)
            results[file_path.name] = (is_valid, errors, warnings)
            validator.print_validation_report()
    
    # 验证pre_data目录下的CSV文件
    pre_data_path = base_path / 'pre_data'
    if pre_data_path.exists():
        for file_path in pre_data_path.glob('*.csv'):
            print(f"\n验证文件: {file_path.name}")
            is_valid, errors, warnings = validator.validate_file(file_path)
            results[file_path.name] = (is_valid, errors, warnings)
            validator.print_validation_report()
    
    # 打印总结
    print("\n" + "="*60)
    print("验证总结")
    print("="*60)
    total = len(results)
    valid = sum(1 for v, _, _ in results.values() if v)
    print(f"总文件数: {total}")
    print(f"通过验证: {valid}")
    print(f"验证失败: {total - valid}")
    print("="*60 + "\n")
    
    return results


if __name__ == '__main__':
    # 运行验证
    logging.basicConfig(level=logging.INFO)
    validate_all()
