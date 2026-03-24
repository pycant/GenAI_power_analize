"""
质量分析共享函数

包含质量数据分析中常用的工具函数
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


def setup_chinese_font():
    """设置中文字体"""
    try:
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        return True
    except:
        return False


def get_academic_colors():
    """获取学术配色方案"""
    return ['#0173B2', '#DE8F05', '#029E73', '#CC78BC',
            '#CA9161', '#949494', '#ECE133', '#56B4E9']


def load_quality_scores(task_type: str, use_raw: bool = True, 
                       data_dir: str = 'analysis/qe_research/results/quality_scores') -> pd.DataFrame:
    """
    加载质量评分数据
    
    Args:
        task_type: 任务类型（code, creative, math, qa, reasoning, summary, translation）
        use_raw: 是否使用原始精度数据
        data_dir: 数据目录路径
    
    Returns:
        pd.DataFrame: 质量评分数据框（模型为行，指标为列）
    """
    data_path = Path(data_dir)
    suffix = '_raw' if use_raw else ''
    filename = f'{task_type}_scores{suffix}.csv'
    file_path = data_path / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"数据文件不存在: {file_path}")
    
    # 读取转置格式的数据（指标为行，模型为列）
    # 第一列是指标名称（可能包含中文）
    df_transposed = pd.read_csv(file_path, index_col=0, encoding='utf-8-sig')
    
    # 转置为标准格式（模型为行，指标为列）
    df = df_transposed.T
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'model'}, inplace=True)
    
    # 清理列名（去除可能的空格）
    df.columns = df.columns.str.strip()
    
    # 确保数值列是数值类型
    for col in df.columns:
        if col != 'model':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def calculate_descriptive_stats(series: pd.Series) -> Dict:
    """
    计算描述性统计量
    
    Args:
        series: 数据序列
    
    Returns:
        dict: 包含各种统计量的字典
    """
    stats = {
        'mean': series.mean(),
        'median': series.median(),
        'std': series.std(),
        'min': series.min(),
        'max': series.max(),
        'range': series.max() - series.min(),
        'q25': series.quantile(0.25),
        'q75': series.quantile(0.75),
        'iqr': series.quantile(0.75) - series.quantile(0.25),
        'skewness': series.skew(),
        'kurtosis': series.kurtosis()
    }
    
    # 变异系数
    if stats['mean'] != 0:
        stats['cv'] = stats['std'] / abs(stats['mean'])
    else:
        stats['cv'] = np.nan
    
    return stats


def get_cost_type_metrics() -> List[str]:
    """
    获取成本型指标列表（越小越好的指标）
    
    Returns:
        List[str]: 成本型指标名称列表
    """
    # 根据METRICS_GUIDE.md定义的指标特性
    cost_metrics = [
        'perplexity',  # 困惑度：越低越好
        # 未来可能添加其他成本型指标，如：
        # 'latency',  # 延迟
        # 'error_rate',  # 错误率
        # 'cost',  # 成本
    ]
    return cost_metrics


def convert_cost_to_benefit(df: pd.DataFrame, cost_metrics: List[str] = None) -> pd.DataFrame:
    """
    将成本型指标转换为效益型指标（越小越好 -> 越大越好）
    
    使用倒数转换：benefit = 1 / (cost + epsilon)
    其中epsilon是一个小常数，避免除零错误
    
    Args:
        df: 数据框
        cost_metrics: 成本型指标列名列表，如果为None则自动获取
    
    Returns:
        pd.DataFrame: 转换后的数据框副本
    """
    if cost_metrics is None:
        cost_metrics = get_cost_type_metrics()
    
    df_converted = df.copy()
    epsilon = 1e-10  # 避免除零
    
    converted_count = 0
    for metric in cost_metrics:
        if metric in df.columns:
            # 检查是否有负值或零值
            min_val = df[metric].min()
            if min_val <= 0:
                # 如果有负值或零值，先平移到正数域
                df_converted[metric] = 1 / (df[metric] - min_val + 1 + epsilon)
            else:
                # 直接取倒数
                df_converted[metric] = 1 / (df[metric] + epsilon)
            
            print(f"  成本型指标转换: {metric} (原始范围: [{df[metric].min():.4f}, {df[metric].max():.4f}]) "
                  f"-> (转换后范围: [{df_converted[metric].min():.4f}, {df_converted[metric].max():.4f}])")
            converted_count += 1
    
    if converted_count == 0:
        print(f"  未发现需要转换的成本型指标")
    
    return df_converted


def normalize_scores(df: pd.DataFrame, columns: List[str], 
                     method: str = 'minmax') -> pd.DataFrame:
    """
    归一化指定列
    
    Args:
        df: 数据框
        columns: 要归一化的列名列表
        method: 归一化方法（'minmax', 'zscore', 'robust'）
    
    Returns:
        pd.DataFrame: 归一化后的数据框副本
    """
    df_norm = df.copy()
    
    for col in columns:
        if col not in df.columns:
            continue
        
        if method == 'minmax':
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val > min_val:
                df_norm[col] = (df[col] - min_val) / (max_val - min_val)
            else:
                df_norm[col] = 0.5
        
        elif method == 'zscore':
            mean_val = df[col].mean()
            std_val = df[col].std()
            if std_val > 0:
                df_norm[col] = (df[col] - mean_val) / std_val
            else:
                df_norm[col] = 0
        
        elif method == 'robust':
            median_val = df[col].median()
            iqr_val = df[col].quantile(0.75) - df[col].quantile(0.25)
            if iqr_val > 0:
                df_norm[col] = (df[col] - median_val) / iqr_val
            else:
                df_norm[col] = 0
    
    return df_norm


def identify_outliers(series: pd.Series, method: str = 'iqr', 
                     threshold: float = 1.5) -> Tuple[pd.Series, List]:
    """
    识别异常值
    
    Args:
        series: 数据序列
        method: 检测方法（'iqr', 'zscore'）
        threshold: 阈值（IQR方法默认1.5，Z-score方法默认3）
    
    Returns:
        tuple: (异常值掩码, 异常值索引列表)
    """
    if method == 'iqr':
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        outlier_mask = (series < lower_bound) | (series > upper_bound)
    
    elif method == 'zscore':
        if threshold == 1.5:  # 如果使用默认IQR阈值，改为Z-score默认值
            threshold = 3
        z_scores = np.abs((series - series.mean()) / series.std())
        outlier_mask = z_scores > threshold
    
    else:
        raise ValueError(f"不支持的方法: {method}")
    
    outlier_indices = series[outlier_mask].index.tolist()
    
    return outlier_mask, outlier_indices


def calculate_correlation_matrix(df: pd.DataFrame, 
                                 columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    计算相关系数矩阵
    
    Args:
        df: 数据框
        columns: 要计算相关性的列名列表（None表示所有数值列）
    
    Returns:
        pd.DataFrame: 相关系数矩阵
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    return df[columns].corr()


def plot_distribution(series: pd.Series, title: str, output_path: Path,
                     bins: int = 15, show_stats: bool = True):
    """
    绘制分布图（直方图+KDE）
    
    Args:
        series: 数据序列
        title: 图表标题
        output_path: 输出文件路径
        bins: 直方图分箱数
        show_stats: 是否显示统计摘要
    """
    setup_chinese_font()
    colors = get_academic_colors()
    
    fig, axes = plt.subplots(1, 2 if show_stats else 1, 
                            figsize=(14, 6) if show_stats else (10, 6))
    
    if show_stats:
        ax1, ax2 = axes
    else:
        ax1 = axes
    
    # 直方图 + KDE
    ax1.hist(series, bins=bins, color=colors[0], 
            edgecolor='black', alpha=0.7, density=True)
    series.plot(kind='kde', ax=ax1, color=colors[1], 
               linewidth=2, label='KDE')
    ax1.axvline(series.mean(), color='red', linestyle='--', 
               linewidth=2, label=f'均值: {series.mean():.3f}')
    ax1.axvline(series.median(), color='green', linestyle='--', 
               linewidth=2, label=f'中位数: {series.median():.3f}')
    ax1.set_xlabel('数值', fontsize=11)
    ax1.set_ylabel('密度', fontsize=11)
    ax1.set_title('分布图', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 统计摘要
    if show_stats:
        stats = calculate_descriptive_stats(series)
        stats_text = f"""
统计摘要:
均值: {stats['mean']:.3f}
中位数: {stats['median']:.3f}
标准差: {stats['std']:.3f}
最小值: {stats['min']:.3f}
最大值: {stats['max']:.3f}
范围: {stats['range']:.3f}
变异系数: {stats['cv']:.3f}
偏度: {stats['skewness']:.3f}
峰度: {stats['kurtosis']:.3f}
        """
        ax2.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax2.axis('off')
    
    plt.suptitle(title, fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_boxplot(df: pd.DataFrame, value_col: str, group_col: str,
                title: str, output_path: Path, 
                xlabel: str = '模型', ylabel: str = '数值'):
    """
    绘制箱线图
    
    Args:
        df: 数据框
        value_col: 数值列名
        group_col: 分组列名
        title: 图表标题
        output_path: 输出文件路径
        xlabel: X轴标签
        ylabel: Y轴标签
    """
    setup_chinese_font()
    colors = get_academic_colors()
    
    plt.figure(figsize=(14, 6))
    
    # 按数值排序
    df_sorted = df.sort_values(value_col, ascending=False)
    
    # 为每个模型生成颜色（循环使用配色方案）
    n_models = len(df_sorted)
    model_colors = [colors[i % len(colors)] for i in range(n_models)]
    
    # 散点图
    positions = range(n_models)
    plt.scatter(positions, df_sorted[value_col], 
               c=model_colors, s=100, alpha=0.7, zorder=3, edgecolors='black', linewidths=0.5)
    
    # 添加水平线显示均值和中位数
    mean_val = df_sorted[value_col].mean()
    median_val = df_sorted[value_col].median()
    plt.axhline(mean_val, color='red', linestyle='--', linewidth=1.5, 
               alpha=0.7, label=f'均值: {mean_val:.3f}')
    plt.axhline(median_val, color='green', linestyle='--', linewidth=1.5, 
               alpha=0.7, label=f'中位数: {median_val:.3f}')
    
    plt.xticks(positions, df_sorted[group_col], rotation=45, ha='right')
    plt.xlabel(xlabel, fontsize=11)
    plt.ylabel(ylabel, fontsize=11)
    plt.title(title, fontsize=13, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_heatmap(corr_matrix: pd.DataFrame, title: str, output_path: Path):
    """
    绘制相关性热力图
    
    Args:
        corr_matrix: 相关系数矩阵
        title: 图表标题
        output_path: 输出文件路径
    """
    setup_chinese_font()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
               center=0, vmin=-1, vmax=1,
               square=True, linewidths=0.5,
               cbar_kws={'label': '相关系数'})
    plt.title(title, fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_radar_chart(df: pd.DataFrame, metrics: List[str], models: List[str],
                    title: str, output_path: Path):
    """
    绘制雷达图
    
    Args:
        df: 数据框（已归一化）
        metrics: 指标列表
        models: 要绘制的模型列表
        title: 图表标题
        output_path: 输出文件路径
    """
    setup_chinese_font()
    colors = get_academic_colors()
    
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # 闭合
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    for i, model in enumerate(models):
        model_data = df[df['model'] == model]
        if len(model_data) == 0:
            continue
        
        values = model_data[metrics].values.flatten().tolist()
        values += values[:1]  # 闭合
        
        ax.plot(angles, values, 'o-', linewidth=2, label=model, 
               color=colors[i % len(colors)])
        ax.fill(angles, values, alpha=0.15, color=colors[i % len(colors)])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_title(title, fontsize=13, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def save_table(df: pd.DataFrame, output_path: Path, index: bool = True):
    """
    保存数据表格为CSV
    
    Args:
        df: 数据框
        output_path: 输出文件路径
        index: 是否保存索引
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=index, encoding='utf-8-sig')


def format_number(value: float, precision: int = 3) -> str:
    """
    格式化数值
    
    Args:
        value: 数值
        precision: 小数位数
    
    Returns:
        str: 格式化后的字符串
    """
    if pd.isna(value):
        return 'N/A'
    return f'{value:.{precision}f}'


def get_task_info(task_type: str) -> Dict:
    """
    获取任务信息
    
    Args:
        task_type: 任务类型
    
    Returns:
        dict: 任务信息字典
    """
    task_info_map = {
        'code': {
            'name_cn': '代码生成',
            'primary_metrics': ['compilation_success', 'functional_correctness', 'code_length'],
            'description': '评估模型生成代码的语法正确性、功能完整性和代码质量'
        },
        'creative': {
            'name_cn': '创意写作',
            'primary_metrics': ['distinct_2', 'distinct_1', 'metaphor_count'],
            'description': '评估模型创意文本的词汇多样性、流畅度和修辞手法'
        },
        'math': {
            'name_cn': '数学推理',
            'primary_metrics': ['exact_match', 'extraction_confidence', 'has_answer'],
            'description': '评估模型数学问题求解的准确性和答案提取能力'
        },
        'qa': {
            'name_cn': '问答',
            'primary_metrics': ['confidence_score', 'answer_length', 'certainty_count'],
            'description': '评估模型回答问题的完整性、确定性和置信度'
        },
        'reasoning': {
            'name_cn': '逻辑推理',
            'primary_metrics': ['conclusion_correct', 'completeness_score', 'coherence_score'],
            'description': '评估模型逻辑推理的正确性、完整性和连贯性'
        },
        'summary': {
            'name_cn': '摘要生成',
            'primary_metrics': ['bartscore_avg', 'bertscore_f1', 'bartscore_faith'],
            'description': '评估模型生成摘要的质量、忠实度和信息性'
        },
        'translation': {
            'name_cn': '翻译',
            'primary_metrics': ['bertscore_f1', 'bleu_1', 'bertscore_precision'],
            'description': '评估模型翻译的语义相似度和词汇匹配度'
        }
    }
    
    return task_info_map.get(task_type, {
        'name_cn': task_type,
        'primary_metrics': [],
        'description': '未知任务类型'
    })
