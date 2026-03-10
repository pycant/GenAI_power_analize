"""
质量数据处理模块

功能：
1. 从 analysis/qe_research/results/quality_scores 加载质量数据
2. 提供多种归一化方法（Z-Score、Min-Max、Robust Scaling）
3. 实现熵权法计算指标权重
4. 实现PCA降维分析

使用示例：
    from pareto_core.process_quality_data import QualityDataProcessor
    
    # 初始化处理器
    processor = QualityDataProcessor(task_name='code')
    
    # 加载数据
    df = processor.load_quality_data()
    
    # 归一化
    df_norm = processor.normalize(method='minmax')
    
    # 熵权法
    weights = processor.calculate_entropy_weights()
    quality_score = processor.get_weighted_quality_score(weights)
    
    # PCA降维
    pca_result = processor.apply_pca(n_components=2)
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import warnings

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class QualityDataProcessor:
    """质量数据处理器"""
    
    # 质量数据目录
    QUALITY_DATA_DIR = project_root / 'analysis' / 'qe_research' / 'results' / 'quality_scores'
    
    # 支持的任务类型
    SUPPORTED_TASKS = ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']
    
    def __init__(self, task_name: str, use_raw: bool = True, verbose: bool = True):
        """
        初始化质量数据处理器
        
        Args:
            task_name: 任务名称（code, creative, math, qa, reasoning, summary, translation）
            use_raw: 是否使用原始数据（保留完整精度）
            verbose: 是否输出详细信息
        """
        if task_name not in self.SUPPORTED_TASKS:
            raise ValueError(f"不支持的任务类型: {task_name}. 支持的任务: {self.SUPPORTED_TASKS}")
        
        self.task_name = task_name
        self.use_raw = use_raw
        self.verbose = verbose
        
        # 数据存储
        self.raw_data = None  # 原始数据（指标×模型）
        self.data = None  # 转置后的数据（模型×指标）
        self.normalized_data = None  # 归一化后的数据
        self.weights = None  # 熵权法权重
        self.pca_result = None  # PCA结果
        
        if self.verbose:
            print(f"初始化质量数据处理器: 任务={task_name}, 使用原始数据={use_raw}")
    
    @staticmethod
    def get_cost_type_metrics() -> List[str]:
        """
        获取成本型指标列表（越小越好的指标）
        
        Returns:
            List[str]: 成本型指标名称列表
        """
        # 根据METRICS_GUIDE.md和QUALITY_SCORES_GENERATION_REPORT_V2.md定义
        cost_metrics = [
            'perplexity',  # 困惑度：越低越好（creative任务）
            # 未来可能添加其他成本型指标
        ]
        return cost_metrics
    
    def convert_cost_to_benefit(self, data: pd.DataFrame, 
                                cost_metrics: Optional[List[str]] = None) -> pd.DataFrame:
        """
        将成本型指标转换为效益型指标（越小越好 -> 越大越好）
        
        使用倒数转换：benefit = 1 / (cost + epsilon)
        
        Args:
            data: 输入数据框
            cost_metrics: 成本型指标列名列表，如果为None则自动获取
        
        Returns:
            pd.DataFrame: 转换后的数据框副本
        """
        if cost_metrics is None:
            cost_metrics = self.get_cost_type_metrics()
        
        df_converted = data.copy()
        epsilon = 1e-10  # 避免除零
        
        converted_count = 0
        for metric in cost_metrics:
            if metric in df_converted.columns:
                # 检查是否有负值或零值
                min_val = df_converted[metric].min()
                if min_val <= 0:
                    # 如果有负值或零值，先平移到正数域
                    df_converted[metric] = 1 / (df_converted[metric] - min_val + 1 + epsilon)
                else:
                    # 直接取倒数
                    df_converted[metric] = 1 / (df_converted[metric] + epsilon)
                
                if self.verbose:
                    print(f"  成本型指标转换: {metric} (原始范围: [{data[metric].min():.4f}, {data[metric].max():.4f}]) "
                          f"-> (转换后范围: [{df_converted[metric].min():.4f}, {df_converted[metric].max():.4f}])")
                converted_count += 1
        
        if converted_count == 0 and self.verbose:
            print(f"  未发现需要转换的成本型指标")
        
        return df_converted
    
    def load_quality_data(self) -> pd.DataFrame:
        """
        加载质量数据
        
        Returns:
            pd.DataFrame: 质量数据（模型×指标格式）
        """
        # 构建文件路径
        suffix = '_raw' if self.use_raw else ''
        file_path = self.QUALITY_DATA_DIR / f'{self.task_name}_scores{suffix}.csv'
        
        if not file_path.exists():
            raise FileNotFoundError(f"质量数据文件不存在: {file_path}")
        
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"加载质量数据: {self.task_name.upper()}")
            print(f"{'='*80}")
            print(f"文件路径: {file_path}")
        
        # 读取数据（第一列为指标名称）
        self.raw_data = pd.read_csv(file_path, index_col=0, encoding='utf-8-sig')
        
        # 转置：从（指标×模型）转为（模型×指标）
        self.data = self.raw_data.T.copy()
        
        if self.verbose:
            print(f"✓ 数据加载成功")
            print(f"  模型数量: {len(self.data)}")
            print(f"  指标数量: {len(self.data.columns)}")
            print(f"  指标列表: {', '.join(self.data.columns[:5])}{'...' if len(self.data.columns) > 5 else ''}")
        
        # 成本型指标转换（在归一化之前）
        if self.verbose:
            print(f"\n检查成本型指标...")
        self.data = self.convert_cost_to_benefit(self.data)
        
        return self.data.copy()
    
    def normalize(self, method: str = 'minmax', 
                  columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        归一化数据
        
        Args:
            method: 归一化方法
                - 'minmax': Min-Max归一化 [0, 1]
                - 'zscore': Z-Score标准化（均值0，标准差1）
                - 'robust': 鲁棒标准化（使用中位数和四分位距）
                - 'maxabs': 最大绝对值归一化 [-1, 1]
            columns: 要归一化的列名列表（None表示所有列）
        
        Returns:
            pd.DataFrame: 归一化后的数据
        """
        if self.data is None:
            raise ValueError("请先调用 load_quality_data() 加载数据")
        
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"数据归一化: {method.upper()}")
            print(f"{'='*80}")
        
        # 选择要归一化的列
        if columns is None:
            columns = self.data.columns.tolist()
        
        # 复制数据
        normalized = self.data.copy()
        
        # 对每列进行归一化
        for col in columns:
            if col not in normalized.columns:
                warnings.warn(f"列 '{col}' 不存在，跳过")
                continue
            
            values = normalized[col].values
            
            # 处理缺失值
            mask = ~np.isnan(values)
            if not mask.any():
                warnings.warn(f"列 '{col}' 全为NaN，跳过")
                continue
            
            if method == 'minmax':
                # Min-Max归一化: (x - min) / (max - min)
                min_val = np.nanmin(values)
                max_val = np.nanmax(values)
                if max_val - min_val > 1e-10:
                    normalized.loc[mask, col] = (values[mask] - min_val) / (max_val - min_val)
                else:
                    normalized.loc[mask, col] = 0.5  # 所有值相同时设为0.5
            
            elif method == 'zscore':
                # Z-Score标准化: (x - mean) / std
                mean_val = np.nanmean(values)
                std_val = np.nanstd(values)
                if std_val > 1e-10:
                    normalized.loc[mask, col] = (values[mask] - mean_val) / std_val
                else:
                    normalized.loc[mask, col] = 0.0  # 标准差为0时设为0
            
            elif method == 'robust':
                # 鲁棒标准化: (x - median) / IQR
                median_val = np.nanmedian(values)
                q75, q25 = np.nanpercentile(values[mask], [75, 25])
                iqr = q75 - q25
                if iqr > 1e-10:
                    normalized.loc[mask, col] = (values[mask] - median_val) / iqr
                else:
                    normalized.loc[mask, col] = 0.0
            
            elif method == 'maxabs':
                # 最大绝对值归一化: x / max(|x|)
                max_abs = np.nanmax(np.abs(values[mask]))
                if max_abs > 1e-10:
                    normalized.loc[mask, col] = values[mask] / max_abs
                else:
                    normalized.loc[mask, col] = 0.0
            
            else:
                raise ValueError(f"不支持的归一化方法: {method}")
        
        self.normalized_data = normalized
        
        if self.verbose:
            print(f"✓ 归一化完成")
            print(f"  方法: {method}")
            print(f"  处理列数: {len(columns)}")
        
        return normalized.copy()
    
    def calculate_entropy_weights(self, 
                                   data: Optional[pd.DataFrame] = None,
                                   columns: Optional[List[str]] = None) -> Dict[str, float]:
        """
        使用熵权法计算指标权重
        
        熵权法原理：
        1. 数据归一化（Min-Max）
        2. 计算每个指标的信息熵
        3. 计算信息效用值（1 - 熵）
        4. 归一化得到权重
        
        Args:
            data: 输入数据（None表示使用已加载的数据）
            columns: 要计算权重的列（None表示所有列）
        
        Returns:
            Dict[str, float]: 指标权重字典
        """
        if data is None:
            if self.data is None:
                raise ValueError("请先调用 load_quality_data() 加载数据")
            data = self.data
        
        if self.verbose:
            print(f"\n{'='*80}")
            print("熵权法计算指标权重")
            print(f"{'='*80}")
        
        # 选择列
        if columns is None:
            columns = data.columns.tolist()
        
        # 首先删除全为NaN的列
        valid_columns = []
        for col in columns:
            if not data[col].isna().all():
                valid_columns.append(col)
            elif self.verbose:
                print(f"⚠ 跳过全为NaN的列: {col}")
        
        if len(valid_columns) == 0:
            raise ValueError("所有列都是NaN，无法计算熵权")
        
        if self.verbose and len(valid_columns) < len(columns):
            print(f"✓ 有效指标数: {len(valid_columns)}/{len(columns)}")
        
        # 提取数据并处理缺失值
        X = data[valid_columns].values
        
        # 删除包含NaN的行
        mask = ~np.isnan(X).any(axis=1)
        X_clean = X[mask]
        
        if len(X_clean) == 0:
            raise ValueError("所有行都包含NaN，无法计算熵权")
        
        n_samples, n_features = X_clean.shape
        
        if self.verbose:
            print(f"有效样本数: {n_samples}/{len(X)}")
            print(f"指标数量: {n_features}")
        
        # 步骤1: Min-Max归一化到[0, 1]
        X_norm = np.zeros_like(X_clean, dtype=float)
        for j in range(n_features):
            col = X_clean[:, j]
            min_val, max_val = col.min(), col.max()
            if max_val - min_val > 1e-10:
                X_norm[:, j] = (col - min_val) / (max_val - min_val)
            else:
                X_norm[:, j] = 0.5
        
        # 步骤2: 计算每个指标的信息熵
        entropies = np.zeros(n_features)
        for j in range(n_features):
            # 计算概率分布（避免log(0)）
            p = X_norm[:, j] + 1e-10
            p = p / p.sum()
            
            # 计算熵
            entropies[j] = -np.sum(p * np.log(p)) / np.log(n_samples)
        
        # 步骤3: 计算信息效用值（差异系数）
        d = 1 - entropies
        
        # 步骤4: 归一化得到权重
        weights_array = d / d.sum()
        
        # 转换为字典（使用valid_columns）
        weights = {col: float(w) for col, w in zip(valid_columns, weights_array)}
        
        self.weights = weights
        
        if self.verbose:
            print(f"\n✓ 熵权法计算完成")
            print(f"\n指标权重（降序）:")
            sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            for metric, weight in sorted_weights:
                print(f"  {metric:<30} {weight:.4f} ({weight*100:.2f}%)")
        
        return weights
    
    def get_weighted_quality_score(self, 
                                    weights: Optional[Dict[str, float]] = None,
                                    data: Optional[pd.DataFrame] = None,
                                    normalize_first: bool = True) -> pd.Series:
        """
        计算加权质量得分
        
        Args:
            weights: 指标权重字典（None表示使用已计算的权重）
            data: 输入数据（None表示使用已加载的数据）
            normalize_first: 是否先归一化再加权
        
        Returns:
            pd.Series: 每个模型的加权质量得分
        """
        if weights is None:
            if self.weights is None:
                raise ValueError("请先调用 calculate_entropy_weights() 计算权重")
            weights = self.weights
        
        if data is None:
            if self.data is None:
                raise ValueError("请先调用 load_quality_data() 加载数据")
            data = self.data
        
        if self.verbose:
            print(f"\n{'='*80}")
            print("计算加权质量得分")
            print(f"{'='*80}")
        
        # 如果需要，先归一化
        if normalize_first:
            if self.verbose:
                print("步骤1: 归一化数据（Min-Max）")
            data_to_use = self.normalize(method='minmax', columns=list(weights.keys()))
        else:
            data_to_use = data
        
        # 计算加权得分
        if self.verbose:
            print("步骤2: 计算加权得分")
        
        scores = pd.Series(0.0, index=data_to_use.index)
        
        for metric, weight in weights.items():
            if metric in data_to_use.columns:
                # 处理NaN：用该指标的均值填充
                values = data_to_use[metric].fillna(data_to_use[metric].mean())
                scores += weight * values
        
        if self.verbose:
            print(f"\n✓ 加权得分计算完成")
            print(f"\n模型得分（降序）:")
            sorted_scores = scores.sort_values(ascending=False)
            for model, score in sorted_scores.items():
                print(f"  {model:<30} {score:.4f}")
        
        return scores
    
    def apply_pca(self, 
                  n_components: Union[int, float] = 2,
                  data: Optional[pd.DataFrame] = None,
                  normalize_first: bool = True) -> Dict:
        """
        应用PCA降维
        
        Args:
            n_components: 主成分数量
                - int: 保留的主成分数量
                - float (0-1): 保留的方差比例
            data: 输入数据（None表示使用已加载的数据）
            normalize_first: 是否先标准化（推荐True）
        
        Returns:
            Dict: PCA结果字典
                - 'transformed': 降维后的数据（DataFrame）
                - 'components': 主成分载荷矩阵（DataFrame）
                - 'explained_variance_ratio': 解释方差比例（array）
                - 'cumulative_variance_ratio': 累积方差比例（array）
                - 'n_components': 实际主成分数量
        """
        try:
            from sklearn.decomposition import PCA
        except ImportError:
            raise ImportError("PCA需要安装scikit-learn: pip install scikit-learn")
        
        if data is None:
            if self.data is None:
                raise ValueError("请先调用 load_quality_data() 加载数据")
            data = self.data
        
        if self.verbose:
            print(f"\n{'='*80}")
            print("PCA降维分析")
            print(f"{'='*80}")
        
        # 处理缺失值：
        # 1. 删除全为NaN的列
        data_clean = data.dropna(axis=1, how='all')
        
        if len(data_clean.columns) == 0:
            raise ValueError("所有列都是NaN，无法进行PCA")
        
        # 2. 删除包含NaN的行
        data_clean = data_clean.dropna(axis=0)
        
        if len(data_clean) == 0:
            raise ValueError("删除NaN后没有有效样本，无法进行PCA")
        
        if self.verbose:
            removed_cols = set(data.columns) - set(data_clean.columns)
            if removed_cols:
                print(f"⚠️  已删除全为NaN的列: {removed_cols}")
            print(f"有效样本数: {len(data_clean)}/{len(data)}")
            print(f"有效特征数: {len(data_clean.columns)}/{len(data.columns)}")
        
        # 标准化
        if normalize_first:
            if self.verbose:
                print("步骤1: Z-Score标准化")
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(data_clean.values)
        else:
            X_scaled = data_clean.values
        
        # PCA
        if self.verbose:
            print(f"步骤2: PCA降维（n_components={n_components}）")
        
        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X_scaled)
        
        # 构建结果
        n_comp = pca.n_components_
        
        # 降维后的数据
        pc_columns = [f'PC{i+1}' for i in range(n_comp)]
        transformed_df = pd.DataFrame(
            X_pca,
            index=data_clean.index,
            columns=pc_columns
        )
        
        # 主成分载荷矩阵
        components_df = pd.DataFrame(
            pca.components_.T,
            index=data_clean.columns,
            columns=pc_columns
        )
        
        # 方差比例
        explained_var = pca.explained_variance_ratio_
        cumulative_var = np.cumsum(explained_var)
        
        result = {
            'transformed': transformed_df,
            'components': components_df,
            'explained_variance_ratio': explained_var,
            'cumulative_variance_ratio': cumulative_var,
            'n_components': n_comp,
            'pca_model': pca
        }
        
        self.pca_result = result
        
        if self.verbose:
            print(f"\n✓ PCA降维完成")
            print(f"  实际主成分数: {n_comp}")
            print(f"\n各主成分解释方差比例:")
            for i in range(n_comp):
                print(f"  PC{i+1}: {explained_var[i]:.4f} ({explained_var[i]*100:.2f}%)")
            print(f"\n累积解释方差: {cumulative_var[-1]:.4f} ({cumulative_var[-1]*100:.2f}%)")
            
            # 显示主要贡献指标
            print(f"\n各主成分的主要贡献指标（|载荷|>0.3）:")
            for i in range(min(3, n_comp)):  # 只显示前3个主成分
                pc_name = f'PC{i+1}'
                loadings = components_df[pc_name].abs().sort_values(ascending=False)
                top_features = loadings[loadings > 0.3]
                if len(top_features) > 0:
                    print(f"\n  {pc_name}:")
                    for feat, load in top_features.items():
                        sign = '+' if components_df.loc[feat, pc_name] > 0 else '-'
                        print(f"    {sign} {feat:<25} {load:.3f}")
        
        return result
    
    def get_summary_statistics(self, data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        获取数据的描述性统计
        
        Args:
            data: 输入数据（None表示使用已加载的数据）
        
        Returns:
            pd.DataFrame: 描述性统计表
        """
        if data is None:
            if self.data is None:
                raise ValueError("请先调用 load_quality_data() 加载数据")
            data = self.data
        
        stats = data.describe().T
        stats['missing'] = data.isnull().sum()
        stats['missing_pct'] = (stats['missing'] / len(data) * 100).round(2)
        
        return stats
    
    def export_results(self, output_dir: Union[str, Path], prefix: str = ''):
        """
        导出所有处理结果
        
        Args:
            output_dir: 输出目录
            prefix: 文件名前缀
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if prefix:
            prefix = f"{prefix}_"
        
        # 导出原始数据
        if self.data is not None:
            self.data.to_csv(output_dir / f'{prefix}quality_data.csv', encoding='utf-8-sig')
        
        # 导出归一化数据
        if self.normalized_data is not None:
            self.normalized_data.to_csv(output_dir / f'{prefix}normalized_data.csv', encoding='utf-8-sig')
        
        # 导出权重
        if self.weights is not None:
            weights_df = pd.DataFrame(list(self.weights.items()), columns=['指标', '权重'])
            weights_df = weights_df.sort_values('权重', ascending=False)
            weights_df.to_csv(output_dir / f'{prefix}entropy_weights.csv', index=False, encoding='utf-8-sig')
        
        # 导出PCA结果
        if self.pca_result is not None:
            self.pca_result['transformed'].to_csv(output_dir / f'{prefix}pca_transformed.csv', encoding='utf-8-sig')
            self.pca_result['components'].to_csv(output_dir / f'{prefix}pca_components.csv', encoding='utf-8-sig')
            
            # 导出方差解释
            var_df = pd.DataFrame({
                '主成分': [f'PC{i+1}' for i in range(self.pca_result['n_components'])],
                '解释方差比例': self.pca_result['explained_variance_ratio'],
                '累积方差比例': self.pca_result['cumulative_variance_ratio']
            })
            var_df.to_csv(output_dir / f'{prefix}pca_variance.csv', index=False, encoding='utf-8-sig')
        
        if self.verbose:
            print(f"\n✓ 结果已导出到: {output_dir}")


# ============================================================================
# 便捷函数
# ============================================================================

def quick_process(task_name: str, 
                  normalize_method: str = 'minmax',
                  use_entropy: bool = True,
                  use_pca: bool = True,
                  n_components: int = 2,
                  output_dir: Optional[Union[str, Path]] = None) -> Dict:
    """
    一键完成质量数据处理流程
    
    Args:
        task_name: 任务名称
        normalize_method: 归一化方法
        use_entropy: 是否使用熵权法
        use_pca: 是否使用PCA
        n_components: PCA主成分数量
        output_dir: 输出目录（None表示不导出）
    
    Returns:
        Dict: 处理结果字典
    """
    processor = QualityDataProcessor(task_name=task_name, verbose=True)
    
    # 加载数据
    data = processor.load_quality_data()
    
    # 归一化
    normalized = processor.normalize(method=normalize_method)
    
    results = {
        'processor': processor,
        'raw_data': data,
        'normalized_data': normalized
    }
    
    # 熵权法
    if use_entropy:
        weights = processor.calculate_entropy_weights()
        quality_score = processor.get_weighted_quality_score(weights)
        results['entropy_weights'] = weights
        results['weighted_quality_score'] = quality_score
    
    # PCA
    if use_pca:
        pca_result = processor.apply_pca(n_components=n_components)
        results['pca_result'] = pca_result
    
    # 导出
    if output_dir is not None:
        processor.export_results(output_dir, prefix=task_name)
    
    return results


if __name__ == '__main__':
    """示例用法"""
    
    # 示例1: 基础用法
    print("\n" + "="*80)
    print("示例1: 基础用法")
    print("="*80)
    
    processor = QualityDataProcessor(task_name='code')
    data = processor.load_quality_data()
    print(f"\n数据形状: {data.shape}")
    print(f"\n前5行:\n{data.head()}")
    
    # 示例2: 归一化
    print("\n" + "="*80)
    print("示例2: 多种归一化方法")
    print("="*80)
    
    for method in ['minmax', 'zscore', 'robust']:
        normalized = processor.normalize(method=method)
        print(f"\n{method.upper()} 归一化后的统计:")
        print(normalized.describe().loc[['mean', 'std', 'min', 'max']].round(3))
    
    # 示例3: 熵权法
    print("\n" + "="*80)
    print("示例3: 熵权法计算权重")
    print("="*80)
    
    weights = processor.calculate_entropy_weights()
    quality_score = processor.get_weighted_quality_score(weights)
    
    # 示例4: PCA
    print("\n" + "="*80)
    print("示例4: PCA降维")
    print("="*80)
    
    pca_result = processor.apply_pca(n_components=2)
    print(f"\nPCA降维后的数据:\n{pca_result['transformed']}")
    
    # 示例5: 一键处理
    print("\n" + "="*80)
    print("示例5: 一键处理（reasoning任务）")
    print("="*80)
    
    results = quick_process(
        task_name='reasoning',
        normalize_method='minmax',
        use_entropy=True,
        use_pca=True,
        n_components=3
    )
    
    print("\n✓ 所有示例完成！")
