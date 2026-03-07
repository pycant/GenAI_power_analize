"""
Pareto分析共享函数

包含所有任务脚本共用的核心算法实现
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def identify_pareto_frontier_2d(df, x_col, y_col, x_minimize=True, y_minimize=True):
    """
    识别2D帕累托前沿
    
    Args:
        df: 数据框
        x_col: X轴列名
        y_col: Y轴列名
        x_minimize: X轴是否最小化（True）或最大化（False）
        y_minimize: Y轴是否最小化（True）或最大化（False）
    
    Returns:
        pareto_mask: 布尔数组，True表示在帕累托前沿上
    """
    n = len(df)
    pareto_mask = np.ones(n, dtype=bool)
    
    for i in range(n):
        if not pareto_mask[i]:
            continue
        
        for j in range(n):
            if i == j:
                continue
            
            # 检查j是否支配i
            x_i, y_i = df.iloc[i][x_col], df.iloc[i][y_col]
            x_j, y_j = df.iloc[j][x_col], df.iloc[j][y_col]
            
            # 根据优化方向调整比较
            if x_minimize:
                x_better = x_j <= x_i
                x_strictly_better = x_j < x_i
            else:
                x_better = x_j >= x_i
                x_strictly_better = x_j > x_i
            
            if y_minimize:
                y_better = y_j <= y_i
                y_strictly_better = y_j < y_i
            else:
                y_better = y_j >= y_i
                y_strictly_better = y_j > y_i
            
            # j支配i：在所有维度上不差，且至少在一个维度上更好
            if x_better and y_better and (x_strictly_better or y_strictly_better):
                pareto_mask[i] = False
                break
    
    return pareto_mask


def identify_pareto_frontier_3d(df, quality_col='quality', energy_col='energy', speed_col='speed'):
    """
    识别3D帕累托前沿（质量最大化，能耗最小化，速度最大化）
    
    Args:
        df: 数据框
        quality_col: 质量列名（最大化）
        energy_col: 能耗列名（最小化）
        speed_col: 速度列名（最大化）
    
    Returns:
        pareto_mask: 布尔数组
    """
    n = len(df)
    pareto_mask = np.ones(n, dtype=bool)
    
    for i in range(n):
        if not pareto_mask[i]:
            continue
        
        for j in range(n):
            if i == j:
                continue
            
            q_i = df.iloc[i][quality_col]
            e_i = df.iloc[i][energy_col]
            s_i = df.iloc[i][speed_col]
            
            q_j = df.iloc[j][quality_col]
            e_j = df.iloc[j][energy_col]
            s_j = df.iloc[j][speed_col]
            
            # j支配i：质量≥，能耗≤，速度≥，且至少一个严格更好
            quality_better = q_j >= q_i
            energy_better = e_j <= e_i
            speed_better = s_j >= s_i
            
            strictly_better = (q_j > q_i) or (e_j < e_i) or (s_j > s_i)
            
            if quality_better and energy_better and speed_better and strictly_better:
                pareto_mask[i] = False
                break
    
    return pareto_mask


def calculate_hypervolume(df, pareto_mask, quality_col='quality', energy_col='energy', reference_point=None):
    """
    计算超体积指标（质量-能耗平面）
    
    Args:
        df: 数据框
        pareto_mask: 帕累托前沿掩码
        quality_col: 质量列名
        energy_col: 能耗列名
        reference_point: 参考点 (quality_ref, energy_ref)，默认为None
    
    Returns:
        hypervolume: 超体积值
    """
    pareto = df[pareto_mask].copy()
    
    if len(pareto) == 0:
        return 0.0
    
    # 归一化到[0,1]（质量最大化，能耗最小化）
    q_min, q_max = df[quality_col].min(), df[quality_col].max()
    e_min, e_max = df[energy_col].min(), df[energy_col].max()
    
    if q_max > q_min:
        pareto['q_norm'] = (pareto[quality_col] - q_min) / (q_max - q_min)
    else:
        pareto['q_norm'] = 0
    
    if e_max > e_min:
        pareto['e_norm'] = 1 - (pareto[energy_col] - e_min) / (e_max - e_min)
    else:
        pareto['e_norm'] = 0
    
    # 按质量排序
    pareto = pareto.sort_values('q_norm')
    
    # 计算超体积
    hv = 0
    for i in range(len(pareto)):
        if i == 0:
            width = pareto.iloc[i]['q_norm'] - 0
        else:
            width = pareto.iloc[i]['q_norm'] - pareto.iloc[i-1]['q_norm']
        
        height = pareto.iloc[i]['e_norm']
        hv += width * height
    
    return hv


def calculate_spacing(df, pareto_mask, quality_col='quality', energy_col='energy'):
    """
    计算间距指标（均匀性）
    
    Args:
        df: 数据框
        pareto_mask: 帕累托前沿掩码
        quality_col: 质量列名
        energy_col: 能耗列名
    
    Returns:
        spacing: 间距指标值
    """
    pareto = df[pareto_mask]
    
    if len(pareto) < 2:
        return 0
    
    # 归一化
    q_min, q_max = df[quality_col].min(), df[quality_col].max()
    e_min, e_max = df[energy_col].min(), df[energy_col].max()
    
    if q_max > q_min:
        q_norm = (pareto[quality_col] - q_min) / (q_max - q_min)
    else:
        q_norm = pd.Series([0] * len(pareto), index=pareto.index)
    
    if e_max > e_min:
        e_norm = (pareto[energy_col] - e_min) / (e_max - e_min)
    else:
        e_norm = pd.Series([0] * len(pareto), index=pareto.index)
    
    # 计算相邻点距离
    distances = []
    points = np.column_stack([q_norm, e_norm])
    
    for i in range(len(points)):
        min_dist = float('inf')
        for j in range(len(points)):
            if i != j:
                dist = np.linalg.norm(points[i] - points[j])
                min_dist = min(min_dist, dist)
        distances.append(min_dist)
    
    # 间距指标：距离的标准差
    mean_dist = np.mean(distances)
    spacing = np.sqrt(np.mean([(d - mean_dist)**2 for d in distances]))
    
    return spacing


def find_knee_point(df, pareto_mask, quality_col='quality', energy_col='energy'):
    """
    寻找拐点（膝点）
    
    使用曲率法：找到曲率最大的点
    
    Args:
        df: 数据框
        pareto_mask: 帕累托前沿掩码
        quality_col: 质量列名
        energy_col: 能耗列名
    
    Returns:
        knee_model: 拐点模型名称
    """
    pareto = df[pareto_mask].copy()
    
    if len(pareto) < 3:
        return pareto.iloc[0]['model'] if len(pareto) > 0 else None
    
    # 归一化
    q_min, q_max = df[quality_col].min(), df[quality_col].max()
    e_min, e_max = df[energy_col].min(), df[energy_col].max()
    
    if q_max > q_min:
        pareto['q_norm'] = (pareto[quality_col] - q_min) / (q_max - q_min)
    else:
        pareto['q_norm'] = 0
    
    if e_max > e_min:
        pareto['e_norm'] = (pareto[energy_col] - e_min) / (e_max - e_min)
    else:
        pareto['e_norm'] = 0
    
    # 按质量排序
    pareto = pareto.sort_values('q_norm')
    
    # 计算曲率
    max_curvature = -1
    knee_idx = 0
    
    for i in range(1, len(pareto) - 1):
        # 三点法计算曲率
        p1 = np.array([pareto.iloc[i-1]['q_norm'], pareto.iloc[i-1]['e_norm']])
        p2 = np.array([pareto.iloc[i]['q_norm'], pareto.iloc[i]['e_norm']])
        p3 = np.array([pareto.iloc[i+1]['q_norm'], pareto.iloc[i+1]['e_norm']])
        
        # 向量
        v1 = p2 - p1
        v2 = p3 - p2
        
        # 角度变化
        if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1, 1)
            curvature = 1 - cos_angle  # 曲率近似
            
            if curvature > max_curvature:
                max_curvature = curvature
                knee_idx = i
    
    return pareto.iloc[knee_idx]['model']


def plot_pareto_2d(df, pareto_mask, x_col, y_col, title, output_path,
                   x_label, y_label, x_minimize=True, y_minimize=True):
    """
    绘制2D帕累托前沿图
    
    Args:
        df: 数据框
        pareto_mask: 帕累托前沿掩码
        x_col: X轴列名
        y_col: Y轴列名
        title: 图表标题
        output_path: 输出文件路径
        x_label: X轴标签
        y_label: Y轴标签
        x_minimize: X轴是否最小化
        y_minimize: Y轴是否最小化
    """
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 非帕累托点
    non_pareto = df[~pareto_mask]
    ax.scatter(non_pareto[x_col], non_pareto[y_col],
              c='lightgray', s=100, alpha=0.6, label='非帕累托点')
    
    # 帕累托点
    pareto = df[pareto_mask]
    ax.scatter(pareto[x_col], pareto[y_col],
              c='red', s=200, marker='*', label='帕累托前沿', zorder=5)
    
    # 标注所有点
    for _, row in df.iterrows():
        ax.annotate(row['model'],
                   (row[x_col], row[y_col]),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=9, alpha=0.8)
    
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def load_energy_speed_data(task_name, energy_file, speed_file):
    """
    加载能耗和速度数据
    
    Args:
        task_name: 任务名称
        energy_file: 能耗文件路径
        speed_file: 速度文件路径
    
    Returns:
        energy_dict: 能耗字典 {model: energy}
        speed_dict: 速度字典 {model: speed}
    """
    # 加载能耗数据（转置）
    energy_df = pd.read_csv(energy_file, index_col=0)
    energy_dict = energy_df.loc[task_name].to_dict()
    
    # 加载速度数据（转置）
    speed_df = pd.read_csv(speed_file, index_col=0)
    speed_dict = speed_df.loc[task_name].to_dict()
    
    return energy_dict, speed_dict


def merge_quality_metrics(quality_df, energy_dict, speed_dict, model_mapping, quality_col='quality'):
    """
    合并质量、能耗、速度数据
    
    此函数兼容两种输入格式：
    1. 旧格式：quality_df 包含 'model' 和自定义质量列（需指定 quality_col）
    2. 新格式：quality_df 来自 load_process_quality_data()，包含 'model' 和 'quality' 列
    
    Args:
        quality_df (pd.DataFrame): 质量数据框
            - 必须包含 'model' 列
            - 旧格式：包含自定义质量列（通过 quality_col 指定）
            - 新格式：包含 'quality' 列（load_process_quality_data 的输出）
        energy_dict (dict): 能耗字典 {model_full: energy_value}
        speed_dict (dict): 速度字典 {model_full: speed_value}
        model_mapping (dict): 模型名称映射 {model_short: model_full}
        quality_col (str): 质量列名，默认 'quality'
            - 新格式（load_process_quality_data）：使用默认值 'quality'
            - 旧格式：指定实际的质量列名（如 'compilation_rate_mean'）
    
    Returns:
        pd.DataFrame: 合并后的数据框，包含列：
            - model: 模型短名称
            - model_full: 模型完整名称
            - quality: 质量得分
            - energy: 能耗值
            - speed: 速度值
    
    Examples:
        # 新格式（推荐）：使用 load_process_quality_data()
        quality_df = load_process_quality_data('code', method='entropy')
        merged_df = merge_quality_metrics(quality_df, energy_dict, speed_dict, MODEL_MAPPING)
        
        # 旧格式：手动加载的数据
        quality_df = pd.read_csv('quality_file.csv')
        merged_df = merge_quality_metrics(quality_df, energy_dict, speed_dict, 
                                          MODEL_MAPPING, quality_col='compilation_rate_mean')
    """
    # 验证输入
    if 'model' not in quality_df.columns:
        raise ValueError("quality_df 必须包含 'model' 列")
    
    if quality_col not in quality_df.columns:
        raise ValueError(f"quality_df 中不存在列 '{quality_col}'。"
                        f"可用列: {list(quality_df.columns)}")
    
    # 合并数据
    data = []
    for _, row in quality_df.iterrows():
        model_short = row['model']
        model_full = model_mapping.get(model_short)
        
        if model_full and model_full in energy_dict and model_full in speed_dict:
            data.append({
                'model': model_short,
                'model_full': model_full,
                'quality': row[quality_col],
                'energy': energy_dict[model_full],
                'speed': speed_dict[model_full]
            })
    
    return pd.DataFrame(data)


def load_process_quality_data(task_name, method='entropy', normalize_method='minmax', 
                               use_raw=True, verbose=True,output_dir='./figures', **kwargs):
    """
    加载并处理质量数据（集成 process_quality_data 模块）
    
    此函数提供统一接口，用于加载质量数据并应用不同的处理方法：
    - 'entropy': 熵权法加权
    - 'pca': PCA降维（取第一主成分）
    - 'mean': 简单平均
    - 'single': 使用单一指标（需指定 quality_column 参数）
    
    Args:
        task_name (str): 任务名称（code, creative, math, qa, reasoning, summary, translation）
        method (str): 处理方法
            - 'entropy': 熵权法加权（默认）
            - 'pca': PCA降维取第一主成分
            - 'mean': 简单平均所有指标
            - 'single': 使用单一指标
        normalize_method (str): 归一化方法（'minmax', 'zscore', 'robust', 'maxabs'）
        use_raw (bool): 是否使用原始数据（保留完整精度）
        verbose (bool): 是否输出详细信息
        **kwargs: 额外参数
            - quality_column (str): 当 method='single' 时，指定使用的质量列名
            - n_components (int): 当 method='pca' 时，PCA主成分数量（默认1）
            - weights (dict): 当 method='custom' 时，自定义权重字典
    
    Returns:
        pd.DataFrame: 包含 'model' 和 'quality' 列的数据框
    
    Examples:
        # 使用熵权法
        df = load_process_quality_data('code', method='entropy')
        
        # 使用单一指标
        df = load_process_quality_data('code', method='single', 
                                       quality_column='compilation_rate')
        
        # 使用PCA
        df = load_process_quality_data('reasoning', method='pca', n_components=1)
        
        # 使用简单平均
        df = load_process_quality_data('creative', method='mean')
    """
    from .process_quality_data import QualityDataProcessor
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"加载质量数据: {task_name.upper()}")
        print(f"处理方法: {method.upper()}")
        print(f"{'='*80}")
    
    # 初始化处理器
    processor = QualityDataProcessor(task_name=task_name, use_raw=use_raw, verbose=verbose)
    
    # 加载数据
    data = processor.load_quality_data()
    
    # 根据方法处理数据
    if method == 'entropy':
        # 熵权法
        weights = processor.calculate_entropy_weights()
        quality_score = processor.get_weighted_quality_score(weights, normalize_first=True)
        #绘制各指标的权重
        plt.figure(figsize=(8, 6),dpi=300)
        plt.bar(weights.keys(), weights.values(), color='skyblue')
        plt.savefig(output_dir / '/entropy_weights.png',dpi=300)
        print(f"✓ 权重可视化已保存:{output_dir}") 
        
        result_df = pd.DataFrame({
            'model': quality_score.index,
            'quality': quality_score.values
        })
        
        if verbose:
            print(f"\n✓ 熵权法处理完成")
            print(f"  质量得分范围: [{quality_score.min():.4f}, {quality_score.max():.4f}]")
    
    elif method == 'pca':
        # PCA降维
        n_components = kwargs.get('n_components', 1)
        pca_result = processor.apply_pca(n_components=n_components, normalize_first=True)
        
        # 使用第一主成分作为质量得分
        quality_score = pca_result['transformed']['PC1']
        
        result_df = pd.DataFrame({
            'model': quality_score.index,
            'quality': quality_score.values
        })
        
        if verbose:
            print(f"\n✓ PCA降维完成")
            print(f"  使用PC1作为质量得分")
            print(f"  PC1解释方差: {pca_result['explained_variance_ratio'][0]:.2%}")
    
    elif method == 'mean':
        # 简单平均
        normalized = processor.normalize(method=normalize_method)
        quality_score = normalized.mean(axis=1)
        
        result_df = pd.DataFrame({
            'model': quality_score.index,
            'quality': quality_score.values
        })
        
        if verbose:
            print(f"\n✓ 简单平均完成")
            print(f"  质量得分范围: [{quality_score.min():.4f}, {quality_score.max():.4f}]")
    
    elif method == 'single':
        # 使用单一指标
        quality_column = kwargs.get('quality_column')
        if quality_column is None:
            raise ValueError("method='single' 时必须指定 quality_column 参数")
        
        if quality_column not in data.columns:
            raise ValueError(f"指标 '{quality_column}' 不存在。可用指标: {list(data.columns)}")
        
        quality_score = data[quality_column]
        
        result_df = pd.DataFrame({
            'model': quality_score.index,
            'quality': quality_score.values
        })
        
        if verbose:
            print(f"\n✓ 使用单一指标: {quality_column}")
            print(f"  质量得分范围: [{quality_score.min():.4f}, {quality_score.max():.4f}]")
    
    elif method == 'custom':
        # 自定义权重
        weights = kwargs.get('weights')
        if weights is None:
            raise ValueError("method='custom' 时必须指定 weights 参数")
        
        quality_score = processor.get_weighted_quality_score(weights, normalize_first=True)
        
        result_df = pd.DataFrame({
            'model': quality_score.index,
            'quality': quality_score.values
        })
        
        if verbose:
            print(f"\n✓ 自定义权重处理完成")
            print(f"  质量得分范围: [{quality_score.min():.4f}, {quality_score.max():.4f}]")
    
    else:
        raise ValueError(f"不支持的处理方法: {method}. "
                        f"支持的方法: 'entropy', 'pca', 'mean', 'single', 'custom'")
    
    # 重置索引
    result_df = result_df.reset_index(drop=True)
    
    if verbose:
        print(f"\n✓ 数据加载完成: {len(result_df)} 个模型")
    
    return result_df



# ============================================================================
# 稳健性分析函数
# ============================================================================

def perturbation_analysis(df, x_col, y_col, x_minimize=True, y_minimize=True, 
                         noise_level=0.05, n_iterations=100):
    """
    扰动分析 - 评估帕累托前沿对数据噪声的敏感性
    
    Args:
        df: 数据框
        x_col: X轴列名
        y_col: Y轴列名
        x_minimize: X轴是否最小化
        y_minimize: Y轴是否最小化
        noise_level: 噪声水平（默认5%）
        n_iterations: 迭代次数（默认100）
    
    Returns:
        dict: 包含稳定性得分和一致性指标的字典
    """
    from collections import Counter
    
    # 原始前沿
    original_pareto = identify_pareto_frontier_2d(df, x_col, y_col, x_minimize, y_minimize)
    original_models = set(df[original_pareto]['model'].tolist())
    
    # 扰动分析
    pareto_models_count = Counter()
    pareto_sets = []
    
    np.random.seed(42)
    for i in range(n_iterations):
        # 添加噪声
        noisy_data = df.copy()
        noisy_data[x_col] = noisy_data[x_col] * (1 + np.random.uniform(-noise_level, noise_level, len(noisy_data)))
        noisy_data[y_col] = noisy_data[y_col] * (1 + np.random.uniform(-noise_level, noise_level, len(noisy_data)))
        
        # 识别前沿
        pareto_mask = identify_pareto_frontier_2d(noisy_data, x_col, y_col, x_minimize, y_minimize)
        pareto_models = noisy_data[pareto_mask]['model'].tolist()
        
        pareto_sets.append(set(pareto_models))
        for model in pareto_models:
            pareto_models_count[model] += 1
    
    # 计算稳定性得分
    stability_scores = {model: count / n_iterations for model, count in pareto_models_count.items()}
    
    # 计算前沿一致性（Jaccard相似度）
    consistency_scores = []
    for pareto_set in pareto_sets:
        if len(pareto_set | original_models) > 0:
            jaccard = len(pareto_set & original_models) / len(pareto_set | original_models)
            consistency_scores.append(jaccard)
    
    mean_consistency = np.mean(consistency_scores) if consistency_scores else 0
    std_consistency = np.std(consistency_scores) if consistency_scores else 0
    
    return {
        'original_models': original_models,
        'stability_scores': stability_scores,
        'model_counts': dict(pareto_models_count),
        'mean_consistency': mean_consistency,
        'std_consistency': std_consistency,
        'n_iterations': n_iterations
    }


def cross_validation_pareto(df, x_col, y_col, x_minimize=True, y_minimize=True, n_folds=5):
    """
    交叉验证分析 - 评估帕累托前沿的泛化能力
    
    Args:
        df: 数据框
        x_col: X轴列名
        y_col: Y轴列名
        x_minimize: X轴是否最小化
        y_minimize: Y轴是否最小化
        n_folds: 折数（默认5）
    
    Returns:
        dict: 包含交叉验证结果的字典
    """
    from collections import Counter
    
    n_models = len(df)
    indices = np.arange(n_models)
    np.random.seed(42)
    np.random.shuffle(indices)
    
    fold_size = n_models // n_folds
    pareto_models_per_fold = []
    
    for fold in range(n_folds):
        # 分割数据
        test_indices = indices[fold * fold_size : (fold + 1) * fold_size]
        train_indices = np.concatenate([indices[:fold * fold_size], indices[(fold + 1) * fold_size:]])
        
        train_data = df.iloc[train_indices].reset_index(drop=True)
        
        # 识别前沿
        pareto_mask = identify_pareto_frontier_2d(train_data, x_col, y_col, x_minimize, y_minimize)
        pareto_models = set(train_data[pareto_mask]['model'].tolist())
        pareto_models_per_fold.append(pareto_models)
    
    # 统计模型出现频率
    model_counts = Counter()
    for pareto_set in pareto_models_per_fold:
        for model in pareto_set:
            model_counts[model] += 1
    
    # 计算一致性
    all_models = set()
    for s in pareto_models_per_fold:
        all_models.update(s)
    
    consistency_scores = []
    for model in all_models:
        appearances = sum(1 for s in pareto_models_per_fold if model in s)
        consistency_scores.append(appearances / n_folds)
    
    mean_consistency = np.mean(consistency_scores) if consistency_scores else 0
    
    return {
        'model_counts': dict(model_counts),
        'mean_consistency': mean_consistency,
        'n_folds': n_folds,
        'pareto_per_fold': pareto_models_per_fold
    }


# ============================================================================
# 报告生成函数
# ============================================================================

def generate_pareto_report(df, results, output_dir, task_config):
    """
    生成帕累托分析报告（通用版本）
    
    Args:
        df: 数据框
        results: 分析结果字典，包含：
            - pareto_qe: 质量-能耗前沿掩码
            - pareto_qs: 质量-速度前沿掩码
            - pareto_3d: 三维前沿掩码
            - hypervolume_qe: 超体积
            - spacing_qe: 间距指标
            - knee_point: 拐点模型
            - robustness_qe: 稳健性分析结果（可选）
            - cross_val_qe: 交叉验证结果（可选）
        output_dir: 输出目录（Path对象）
        task_config: 任务配置字典，包含：
            - task_name: 任务名称（如'code', 'creative'等）
            - task_name_cn: 任务中文名称（如'代码生成', '创意写作'等）
            - quality_metric: 质量指标名称（如'编译成功率', 'Distinct-2'等）
            - report_filename: 报告文件名（可选，默认为'{TASK}_PARETO_ANALYSIS_REPORT.md'）
    
    Returns:
        report_path: 生成的报告文件路径
    """
    from pathlib import Path
    
    # 配置参数
    task_name = task_config.get('task_name', 'unknown')
    task_name_cn = task_config.get('task_name_cn', task_name)
    quality_metric = task_config.get('quality_metric', '质量得分')
    report_filename = task_config.get('report_filename', 
                                     f'{task_name.upper()}_PARETO_ANALYSIS_REPORT.md')
    
    report_file = Path(output_dir) / report_filename
    
    with open(report_file, 'w', encoding='utf-8') as f:
        # 标题和元数据
        f.write(f"# {task_name_cn}任务帕累托前沿分析报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # 1. 数据概览
        f.write("## 1. 数据概览\n\n")
        f.write(f"- **任务类型**: {task_name_cn}任务（{task_name}）\n")
        f.write(f"- **模型数量**: {len(df)}\n")
        f.write(f"- **质量指标**: {quality_metric}\n\n")
        
        # 2. 帕累托前沿识别
        f.write("## 2. 帕累托前沿识别\n\n")
        
        # 2.1 质量-能耗前沿
        f.write(f"### 2.1 质量-能耗前沿: {results['pareto_qe'].sum()} 个模型\n\n")
        pareto_qe_models = df[results['pareto_qe']].sort_values('quality', ascending=False)
        for _, row in pareto_qe_models.iterrows():
            f.write(f"- {row['model']}: 质量={row['quality']:.3f}, 能耗={row['energy']:.3f} J/token\n")
        
        # 2.2 质量-速度前沿
        f.write(f"\n### 2.2 质量-速度前沿: {results['pareto_qs'].sum()} 个模型\n\n")
        pareto_qs_models = df[results['pareto_qs']].sort_values('quality', ascending=False)
        for _, row in pareto_qs_models.iterrows():
            f.write(f"- {row['model']}: 质量={row['quality']:.3f}, 速度={row['speed']:.2f} tokens/s\n")
        
        # 2.3 三维前沿
        f.write(f"\n### 2.3 三维前沿: {results['pareto_3d'].sum()} 个模型\n\n")
        pareto_3d_models = df[results['pareto_3d']].sort_values('quality', ascending=False)
        for _, row in pareto_3d_models.iterrows():
            f.write(f"- {row['model']}: 质量={row['quality']:.3f}, 能耗={row['energy']:.3f}, 速度={row['speed']:.2f}\n")
        
        # 3. 定量指标
        f.write("\n## 3. 定量指标\n\n")
        f.write(f"- **超体积（质量-能耗）**: {results['hypervolume_qe']:.4f}\n")
        f.write(f"- **间距指标（质量-能耗）**: {results['spacing_qe']:.4f}\n")
        f.write(f"- **拐点模型**: {results['knee_point']}\n\n")
        
        # 4. 稳健性分析（如果有）
        if 'robustness_qe' in results and 'cross_val_qe' in results:
            f.write("## 4. 稳健性分析\n\n")
            
            # 4.1 扰动分析
            f.write("### 4.1 扰动分析（质量-能耗前沿）\n\n")
            rob = results['robustness_qe']
            f.write(f"**分析设置**: 噪声水平 ±{rob.get('noise_level', 0.05)*100:.0f}%, 迭代 {rob['n_iterations']} 次\n\n")
            f.write(f"**前沿一致性**: {rob['mean_consistency']:.2%} (标准差: {rob['std_consistency']:.2%})\n\n")
            
            if rob.get('stability_scores'):
                f.write("**稳定性得分** (模型在扰动中保持在前沿的频率):\n\n")
                f.write("| 模型 | 稳定性得分 | 出现次数 | 评级 |\n")
                f.write("|------|-----------|---------|------|\n")
                
                sorted_scores = sorted(rob['stability_scores'].items(), 
                                     key=lambda x: x[1], reverse=True)
                for model, score in sorted_scores:
                    count = rob['model_counts'].get(model, 0)
                    rating = "⭐⭐⭐⭐⭐" if score >= 0.9 else \
                            "⭐⭐⭐⭐" if score >= 0.7 else \
                            "⭐⭐⭐" if score >= 0.5 else "⭐⭐"
                    f.write(f"| {model} | {score:.2%} | {count}/{rob['n_iterations']} | {rating} |\n")
                f.write("\n")
            
            # 4.2 交叉验证
            f.write("### 4.2 交叉验证分析\n\n")
            cv = results['cross_val_qe']
            f.write(f"**{cv['n_folds']}折交叉验证一致性**: {cv['mean_consistency']:.2%}\n\n")
            
            if cv.get('model_counts'):
                f.write("**模型出现频率**:\n\n")
                f.write("| 模型 | 出现次数 | 频率 |\n")
                f.write("|------|---------|------|\n")
                
                sorted_counts = sorted(cv['model_counts'].items(), 
                                     key=lambda x: x[1], reverse=True)
                for model, count in sorted_counts:
                    freq = count / cv['n_folds']
                    f.write(f"| {model} | {count}/{cv['n_folds']} | {freq:.0%} |\n")
                f.write("\n")
        
        # 5. 推荐配置
        f.write("## 5. 推荐配置\n\n")
        
        # 找出最佳模型
        best_quality_model = df.loc[df['quality'].idxmax()]
        best_speed_model = df.loc[df['speed'].idxmax()]
        best_energy_model = df.loc[df['energy'].idxmin()]
        knee_model = df[df['model'] == results['knee_point']].iloc[0] if results['knee_point'] else None
        
        if knee_model is not None:
            f.write(f"### 最佳综合配置: {knee_model['model']} ⭐⭐⭐⭐⭐\n\n")
            f.write(f"- **{quality_metric}**: {knee_model['quality']:.3f}\n")
            f.write(f"- **每token能耗**: {knee_model['energy']:.3f} J/token\n")
            f.write(f"- **生成速度**: {knee_model['speed']:.2f} tokens/s\n")
            f.write(f"- **推荐理由**: 拐点模型，质量-能耗权衡最优\n\n")
        
        f.write(f"### 最高质量: {best_quality_model['model']}\n\n")
        f.write(f"- **{quality_metric}**: {best_quality_model['quality']:.3f}\n")
        f.write(f"- **每token能耗**: {best_quality_model['energy']:.3f} J/token\n")
        f.write(f"- **生成速度**: {best_quality_model['speed']:.2f} tokens/s\n\n")
        
        f.write(f"### 最低能耗: {best_energy_model['model']}\n\n")
        f.write(f"- **{quality_metric}**: {best_energy_model['quality']:.3f}\n")
        f.write(f"- **每token能耗**: {best_energy_model['energy']:.3f} J/token\n")
        f.write(f"- **生成速度**: {best_energy_model['speed']:.2f} tokens/s\n\n")
        
        f.write(f"### 最快速度: {best_speed_model['model']}\n\n")
        f.write(f"- **{quality_metric}**: {best_speed_model['quality']:.3f}\n")
        f.write(f"- **每token能耗**: {best_speed_model['energy']:.3f} J/token\n")
        f.write(f"- **生成速度**: {best_speed_model['speed']:.2f} tokens/s\n\n")
        
        # 6. 完整数据表
        f.write("## 6. 完整数据表\n\n")
        f.write("| 模型 | 质量 | 能耗(J/token) | 速度(tokens/s) | 质量-能耗前沿 | 质量-速度前沿 | 3D前沿 |\n")
        f.write("|------|------|--------------|---------------|-------------|-------------|--------|\n")
        
        for _, row in df.sort_values('quality', ascending=False).iterrows():
            qe_mark = "✓" if results['pareto_qe'][row.name] else ""
            qs_mark = "✓" if results['pareto_qs'][row.name] else ""
            td_mark = "✓" if results['pareto_3d'][row.name] else ""
            
            f.write(f"| {row['model']} | {row['quality']:.3f} | {row['energy']:.3f} | "
                   f"{row['speed']:.2f} | {qe_mark} | {qs_mark} | {td_mark} |\n")
        
        f.write("\n")
        
        # 页脚
        f.write("---\n\n")
        f.write(f"**生成脚本**: `analysis/qe_research/scripts/pareto_analysis_{task_name}.py`\n")
    
    return report_file


def print_analysis_summary(df, results, task_name_cn="任务"):
    """
    打印分析摘要到控制台
    
    Args:
        df: 数据框
        results: 分析结果字典
        task_name_cn: 任务中文名称
    """
    print("\n" + "="*80)
    print(f"{task_name_cn}分析摘要")
    print("="*80)
    
    print(f"\n📊 数据概览:")
    print(f"  - 模型数量: {len(df)}")
    print(f"  - 质量范围: {df['quality'].min():.3f} - {df['quality'].max():.3f}")
    print(f"  - 能耗范围: {df['energy'].min():.3f} - {df['energy'].max():.3f} J/token")
    print(f"  - 速度范围: {df['speed'].min():.2f} - {df['speed'].max():.2f} tokens/s")
    
    print(f"\n🎯 帕累托前沿:")
    print(f"  - 质量-能耗前沿: {results['pareto_qe'].sum()} 个模型")
    print(f"  - 质量-速度前沿: {results['pareto_qs'].sum()} 个模型")
    print(f"  - 三维前沿: {results['pareto_3d'].sum()} 个模型")
    
    print(f"\n📈 定量指标:")
    print(f"  - 超体积: {results['hypervolume_qe']:.4f}")
    print(f"  - 间距指标: {results['spacing_qe']:.4f}")
    print(f"  - 拐点模型: {results['knee_point']}")
    
    if 'robustness_qe' in results:
        print(f"\n🔒 稳健性:")
        print(f"  - 前沿一致性: {results['robustness_qe']['mean_consistency']:.2%}")
        if 'cross_val_qe' in results:
            print(f"  - 交叉验证: {results['cross_val_qe']['mean_consistency']:.2%}")
    
    print("\n" + "="*80)
