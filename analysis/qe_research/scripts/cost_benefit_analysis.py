"""
成本效益分析脚本 - 第5章实现

实现内容:
5.1 成本核算模型与指标定义
5.2 跨任务成本效益比较与模型排序
5.3 任务难度加权的成本效益分析
5.4 场景化模型选择策略
5.5 成本-质量权衡的边际效益分析
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from scipy import stats
from scipy.optimize import curve_fit

from pareto_core import (
    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
    load_energy_speed_data, load_average_energy_speed_data, load_process_quality_data
)

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================================
# 预计算质量得分数据路径配置
# ============================================================================

# 混合任务分析结果目录
MIXED_TASK_RESULTS_DIR = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'mixed_task_analysis'

# 三种需求类型的质量得分文件
QUALITY_SCORE_FILES = {
    'balanced': MIXED_TASK_RESULTS_DIR / 'task_02' / 'balanced' / 'aggregated_quality_scores.csv',
    'objective': MIXED_TASK_RESULTS_DIR / 'task_02' / 'objective' / 'aggregated_quality_scores.csv',
    'subjective': MIXED_TASK_RESULTS_DIR / 'task_02' / 'subjective' / 'aggregated_quality_scores.csv'
}

# ============================================================================
# 5.1 成本核算模型与指标定义
# ============================================================================

class CostModel:
    """成本核算模型"""
    
    def __init__(self, 
                 energy_cost_per_kwh: float = 0.12,  # 电价 $/kWh
                 gpu_depreciation_per_hour: float = 0.50,  # GPU折旧 $/hour
                 inference_time_weight: float = 1.0):  # 推理时间权重
        """
        Args:
            energy_cost_per_kwh: 电价 (美元/千瓦时)
            gpu_depreciation_per_hour: GPU折旧成本 (美元/小时)
            inference_time_weight: 推理时间权重系数
        """
        self.energy_cost_per_kwh = energy_cost_per_kwh
        self.gpu_depreciation_per_hour = gpu_depreciation_per_hour
        self.inference_time_weight = inference_time_weight
    
    def calculate_energy_cost(self, energy_j_per_token: float, num_tokens: int = 1000) -> float:
        """计算能耗成本 (美元)"""
        energy_kwh = (energy_j_per_token * num_tokens) / (3600 * 1000)  # J -> kWh
        return energy_kwh * self.energy_cost_per_kwh
    
    def calculate_time_cost(self, tokens_per_second: float, num_tokens: int = 1000) -> float:
        """计算时间成本 (美元)"""
        time_hours = (num_tokens / tokens_per_second) / 3600  # seconds -> hours
        return time_hours * self.gpu_depreciation_per_hour * self.inference_time_weight
    
    def calculate_total_cost(self, energy_j_per_token: float, 
                            tokens_per_second: float, 
                            num_tokens: int = 1000) -> Dict[str, float]:
        """计算总成本"""
        energy_cost = self.calculate_energy_cost(energy_j_per_token, num_tokens)
        time_cost = self.calculate_time_cost(tokens_per_second, num_tokens)
        total_cost = energy_cost + time_cost
        
        return {
            'energy_cost': energy_cost,
            'time_cost': time_cost,
            'total_cost': total_cost,
            'cost_per_token': total_cost / num_tokens
        }


def calculate_cost_metrics(df: pd.DataFrame, cost_model: CostModel) -> pd.DataFrame:
    """为数据框添加成本指标"""
    results = []
    
    for _, row in df.iterrows():
        costs = cost_model.calculate_total_cost(
            row['energy'], 
            row['speed'],
            num_tokens=1000
        )
        
        result = row.to_dict()
        result.update(costs)
        
        # 成本效益比 (Cost-Benefit Ratio)
        if row['quality'] > 0:
            result['cbr'] = costs['total_cost'] / row['quality']  # 越小越好
        else:
            result['cbr'] = np.inf
        
        # 质量成本比 (Quality per Cost)
        if costs['total_cost'] > 0:
            result['qpc'] = row['quality'] / costs['total_cost']  # 越大越好
        else:
            result['qpc'] = np.inf
        
        results.append(result)
    
    return pd.DataFrame(results)


# ============================================================================
# 5.2 跨任务成本效益比较与模型排序
# ============================================================================

def load_precomputed_quality_scores(quality_type: str, 
                                    verbose: bool = True) -> pd.DataFrame:
    """
    加载预计算的质量得分数据
    
    Args:
        quality_type: 'balanced', 'objective', 或 'subjective'
        verbose: 是否打印详细信息
    
    Returns:
        包含 model 和 quality 列的数据框
    """
    if quality_type not in QUALITY_SCORE_FILES:
        raise ValueError(f"未知的质量类型: {quality_type}，可选值: {list(QUALITY_SCORE_FILES.keys())}")
    
    file_path = QUALITY_SCORE_FILES[quality_type]
    
    if not file_path.exists():
        raise FileNotFoundError(f"质量得分文件不存在: {file_path}")
    
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    
    if verbose:
        print(f"✓ 加载 {quality_type} 质量得分: {len(df)} 个模型")
        print(f"  文件路径: {file_path}")
        print(f"  质量范围: [{df['quality'].min():.4f}, {df['quality'].max():.4f}]")
    
    return df


def cross_task_cost_benefit_comparison(tasks: List[str], 
                                       cost_model: CostModel,
                                       output_dir: Path,
                                       verbose: bool = True) -> pd.DataFrame:
    """跨任务成本效益比较"""
    all_results = []
    
    for task in tasks:
        if verbose:
            print(f"\n处理任务: {task}")
        
        # 加载质量数据
        try:
            quality_df = load_process_quality_data(
                task_name=task,
                method='pca',
                normalize_method='zscore',
                use_raw=True,
                verbose=False
            )
        except Exception as e:
            if verbose:
                print(f"  跳过任务 {task}: {str(e)}")
            continue
        
        # 加载能耗和速度数据
        energy_dict, speed_dict = load_energy_speed_data(
            task, DATA_PATHS['energy'], DATA_PATHS['speed']
        )
        
        # 合并数据
        for _, row in quality_df.iterrows():
            model = row['model']
            model_full = MODEL_MAPPING.get(model)
            
            if model_full and model_full in energy_dict and model_full in speed_dict:
                all_results.append({
                    'task': task,
                    'model': model,
                    'quality': row['quality'],  # 使用 'quality' 而不是 'quality_score'
                    'energy': energy_dict[model_full],
                    'speed': speed_dict[model_full]
                })
    
    df = pd.DataFrame(all_results)
    
    # 计算成本指标
    df = calculate_cost_metrics(df, cost_model)
    
    # 保存结果
    output_file = output_dir / 'cross_task_cost_benefit.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    if verbose:
        print(f"\n✓ 跨任务成本效益数据已保存: {output_file.name}")
        print(f"  总记录数: {len(df)}")
    
    return df


def rank_models_by_cost_benefit(df: pd.DataFrame, 
                                 metric: str = 'qpc',
                                 output_dir: Path = None) -> pd.DataFrame:
    """按成本效益指标排序模型
    
    Args:
        metric: 'qpc' (质量成本比, 越大越好) 或 'cbr' (成本效益比, 越小越好)
    """
    # 按任务分组计算平均值
    grouped = df.groupby('model').agg({
        'quality': 'mean',
        'energy': 'mean',
        'speed': 'mean',
        'total_cost': 'mean',
        'qpc': 'mean',
        'cbr': 'mean'
    }).reset_index()
    
    # 排序
    ascending = (metric == 'cbr')  # CBR越小越好
    ranked = grouped.sort_values(metric, ascending=ascending).reset_index(drop=True)
    ranked['rank'] = range(1, len(ranked) + 1)
    
    if output_dir:
        output_file = output_dir / f'model_ranking_by_{metric}.csv'
        ranked.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✓ 模型排名已保存: {output_file.name}")
    
    return ranked


# ============================================================================
# 5.3 任务难度加权的成本效益分析
# ============================================================================

def calculate_task_difficulty(df: pd.DataFrame, tasks: List[str]) -> Dict[str, float]:
    """计算任务难度 (变异系数)"""
    task_difficulty = {}
    
    for task in tasks:
        task_data = df[df['task'] == task]
        if len(task_data) > 0:
            quality_scores = task_data['quality'].values
            mean_score = quality_scores.mean()
            std_score = quality_scores.std()
            
            if abs(mean_score) > 1e-6:
                cv = std_score / abs(mean_score)
            else:
                cv = std_score
            
            task_difficulty[task] = cv
    
    return task_difficulty


def difficulty_weighted_cost_benefit(df: pd.DataFrame,
                                     task_difficulty: Dict[str, float],
                                     user_weights: Optional[Dict[str, float]] = None,
                                     output_dir: Path = None) -> pd.DataFrame:
    """任务难度加权的成本效益分析"""
    # 归一化难度
    diff_values = list(task_difficulty.values())
    min_diff, max_diff = min(diff_values), max(diff_values)
    
    if max_diff > min_diff:
        norm_difficulty = {task: (diff - min_diff) / (max_diff - min_diff) 
                          for task, diff in task_difficulty.items()}
    else:
        norm_difficulty = {task: 0.5 for task in task_difficulty}
    
    # 默认用户权重 (均等)
    if user_weights is None:
        tasks = list(task_difficulty.keys())
        user_weights = {task: 1.0 / len(tasks) for task in tasks}
    
    # 归一化用户权重
    total_weight = sum(user_weights.values())
    user_weights = {k: v / total_weight for k, v in user_weights.items()}
    
    # 计算综合权重: w_t * d_t
    combined_weights = {task: user_weights.get(task, 0) * task_difficulty.get(task, 0)
                       for task in task_difficulty.keys()}
    
    # 归一化综合权重
    total_combined = sum(combined_weights.values())
    if total_combined > 0:
        combined_weights = {k: v / total_combined for k, v in combined_weights.items()}
    
    # 计算加权质量和成本
    results = []
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        
        weighted_quality = 0
        weighted_cost = 0
        total_weight_used = 0
        
        for task in task_difficulty.keys():
            task_data = model_data[model_data['task'] == task]
            if len(task_data) > 0:
                weight = combined_weights.get(task, 0)
                weighted_quality += weight * task_data['quality'].mean()
                weighted_cost += weight * task_data['total_cost'].mean()
                total_weight_used += weight
        
        if total_weight_used > 0:
            weighted_quality /= total_weight_used
            weighted_cost /= total_weight_used
            
            results.append({
                'model': model,
                'weighted_quality': weighted_quality,
                'weighted_cost': weighted_cost,
                'weighted_qpc': weighted_quality / weighted_cost if weighted_cost > 0 else 0,
                'weighted_cbr': weighted_cost / weighted_quality if weighted_quality > 0 else np.inf
            })
    
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values('weighted_qpc', ascending=False).reset_index(drop=True)
    result_df['rank'] = range(1, len(result_df) + 1)
    
    if output_dir:
        output_file = output_dir / 'difficulty_weighted_cost_benefit.csv'
        result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✓ 难度加权成本效益分析已保存: {output_file.name}")
    
    return result_df


# ============================================================================
# 5.4 场景化模型选择策略
# ============================================================================

SCENARIO_CONFIGS = {
    'cost_sensitive': {
        'name': '成本敏感场景',
        'description': '预算受限，优先考虑低成本',
        'quality_threshold': 0.0,  # 最低质量要求
        'cost_weight': 0.8,  # 成本权重
        'quality_weight': 0.2  # 质量权重
    },
    'quality_priority': {
        'name': '质量优先场景',
        'description': '追求最高质量，成本次要',
        'quality_threshold': 0.5,
        'cost_weight': 0.2,
        'quality_weight': 0.8
    },
    'balanced': {
        'name': '均衡场景',
        'description': '质量和成本并重',
        'quality_threshold': 0.0,
        'cost_weight': 0.5,
        'quality_weight': 0.5
    },
    'speed_critical': {
        'name': '速度关键场景',
        'description': '实时应用，速度最重要',
        'quality_threshold': 0.0,
        'cost_weight': 0.3,
        'quality_weight': 0.3,
        'speed_weight': 0.4
    }
}


def scenario_based_selection(df: pd.DataFrame,
                             scenario: str,
                             output_dir: Path = None) -> pd.DataFrame:
    """场景化模型选择"""
    config = SCENARIO_CONFIGS[scenario]
    
    # 归一化指标到 [0, 1]
    df_norm = df.copy()
    
    # 质量: 越大越好 -> 归一化到 [0, 1]
    q_min, q_max = df['quality'].min(), df['quality'].max()
    if q_max > q_min:
        df_norm['quality_norm'] = (df['quality'] - q_min) / (q_max - q_min)
    else:
        df_norm['quality_norm'] = 0.5
    
    # 成本: 越小越好 -> 反向归一化到 [0, 1]
    c_min, c_max = df['total_cost'].min(), df['total_cost'].max()
    if c_max > c_min:
        df_norm['cost_norm'] = 1 - (df['total_cost'] - c_min) / (c_max - c_min)
    else:
        df_norm['cost_norm'] = 0.5
    
    # 速度: 越大越好 -> 归一化到 [0, 1]
    if 'speed_weight' in config:
        s_min, s_max = df['speed'].min(), df['speed'].max()
        if s_max > s_min:
            df_norm['speed_norm'] = (df['speed'] - s_min) / (s_max - s_min)
        else:
            df_norm['speed_norm'] = 0.5
    
    # 计算综合得分
    df_norm['scenario_score'] = (
        config['quality_weight'] * df_norm['quality_norm'] +
        config['cost_weight'] * df_norm['cost_norm']
    )
    
    if 'speed_weight' in config:
        df_norm['scenario_score'] += config['speed_weight'] * df_norm['speed_norm']
    
    # 应用质量阈值
    df_filtered = df_norm[df_norm['quality_norm'] >= config['quality_threshold']]
    
    # 排序
    df_ranked = df_filtered.sort_values('scenario_score', ascending=False).reset_index(drop=True)
    df_ranked['rank'] = range(1, len(df_ranked) + 1)
    
    if output_dir:
        output_file = output_dir / f'scenario_selection_{scenario}.csv'
        df_ranked.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✓ 场景选择结果已保存: {output_file.name}")
    
    return df_ranked


# ============================================================================
# 5.5 成本-质量权衡的边际效益分析
# ============================================================================

def marginal_benefit_analysis(df: pd.DataFrame, 
                              output_dir: Path = None) -> Dict:
    """边际效益分析（使用排名计算，更稳定）"""
    # 按成本排序
    df_sorted = df.sort_values('total_cost').reset_index(drop=True)
    
    # 使用排名计算边际效益（更稳定）
    df_sorted['cost_rank'] = df_sorted['total_cost'].rank()
    df_sorted['quality_rank'] = df_sorted['quality'].rank()
    
    # 计算边际成本和边际质量（使用排名差）
    marginal_data = []
    for i in range(1, len(df_sorted)):
        delta_cost_rank = df_sorted.loc[i, 'cost_rank'] - df_sorted.loc[i-1, 'cost_rank']
        delta_quality_rank = df_sorted.loc[i, 'quality_rank'] - df_sorted.loc[i-1, 'quality_rank']
        
        # 边际效益 = 质量排名变化 / 成本排名变化
        if delta_cost_rank > 0:
            marginal_benefit = delta_quality_rank / delta_cost_rank
        else:
            marginal_benefit = 0
        
        marginal_data.append({
            'model': df_sorted.loc[i, 'model'],
            'cost': df_sorted.loc[i, 'total_cost'],
            'quality': df_sorted.loc[i, 'quality'],
            'cost_rank': df_sorted.loc[i, 'cost_rank'],
            'quality_rank': df_sorted.loc[i, 'quality_rank'],
            'delta_cost_rank': delta_cost_rank,
            'delta_quality_rank': delta_quality_rank,
            'marginal_benefit': marginal_benefit
        })
    
    marginal_df = pd.DataFrame(marginal_data)
    
    # 拟合成本-质量曲线（使用原始值）
    try:
        # 对数函数拟合: Q = a * log(C) + b
        def log_func(x, a, b):
            return a * np.log(x + 1e-10) + b
        
        popt, _ = curve_fit(log_func, df_sorted['total_cost'], df_sorted['quality'])
        
        # 计算拟合优度
        y_pred = log_func(df_sorted['total_cost'], *popt)
        r2 = 1 - np.sum((df_sorted['quality'] - y_pred)**2) / np.sum((df_sorted['quality'] - df_sorted['quality'].mean())**2)
        
        fit_params = {'a': popt[0], 'b': popt[1], 'r2': r2}
    except:
        fit_params = None
    
    # 识别拐点 (边际效益最高的点)
    if len(marginal_df) > 0:
        knee_idx = marginal_df['marginal_benefit'].idxmax()
        knee_model = marginal_df.loc[knee_idx, 'model']
    else:
        knee_model = None
    
    results = {
        'marginal_df': marginal_df,
        'fit_params': fit_params,
        'knee_model': knee_model
    }
    
    if output_dir:
        output_file = output_dir / 'marginal_benefit_analysis.csv'
        marginal_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✓ 边际效益分析已保存: {output_file.name}")
    
    return results


# ============================================================================
# 可视化函数
# ============================================================================

def plot_cost_benefit_scatter(df: pd.DataFrame, output_path: Path):
    """绘制成本-质量散点图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    scatter = ax.scatter(df['total_cost'], df['quality'], 
                        s=200, c=df['qpc'], cmap='RdYlGn',
                        edgecolor='black', linewidth=1.5, alpha=0.7)
    
    for _, row in df.iterrows():
        ax.annotate(row['model'], (row['total_cost'], row['quality']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=9, alpha=0.8)
    
    ax.set_xlabel('Total Cost ($)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Quality Score', fontsize=12, fontweight='bold')
    ax.set_title('Cost-Benefit Trade-off Analysis', fontsize=14, fontweight='bold', pad=20)
    ax.grid(alpha=0.3, linestyle='--')
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Quality per Cost (QPC)', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 成本效益散点图已保存: {output_path.name}")


def plot_marginal_benefit_curve(marginal_df: pd.DataFrame, 
                                df_sorted: pd.DataFrame,
                                fit_params: Optional[Dict],
                                output_path: Path):
    """绘制边际效益曲线"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 子图1: 成本-质量曲线
    ax1.plot(df_sorted['total_cost'], df_sorted['quality'], 
            'o-', linewidth=2, markersize=8, label='实际数据')
    
    # 添加模型标签
    for i, row in df_sorted.iterrows():
        ax1.annotate(row['model'][:10], (row['total_cost'], row['quality']),
                    xytext=(3, 3), textcoords='offset points', fontsize=7, alpha=0.7)
    
    if fit_params:
        x_fit = np.linspace(df_sorted['total_cost'].min(), 
                           df_sorted['total_cost'].max(), 100)
        y_fit = fit_params['a'] * np.log(x_fit + 1e-10) + fit_params['b']
        ax1.plot(x_fit, y_fit, 'r--', linewidth=2, alpha=0.7,
                label=f'对数拟合 (R²={fit_params["r2"]:.3f})')
    
    ax1.set_xlabel('Total Cost ($/千token)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Quality Score', fontsize=12, fontweight='bold')
    ax1.set_title('成本-质量曲线', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3, linestyle='--')
    
    # 子图2: 边际效益（使用排名计算）
    colors = ['green' if mb > 0 else 'red' for mb in marginal_df['marginal_benefit']]
    ax2.bar(range(len(marginal_df)), marginal_df['marginal_benefit'],
           color=colors, edgecolor='black', alpha=0.7)
    
    # 添加模型标签
    ax2.set_xticks(range(len(marginal_df)))
    ax2.set_xticklabels([m[:8] for m in marginal_df['model']], rotation=45, ha='right', fontsize=8)
    
    ax2.set_xlabel('模型 (按成本排序)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('边际效益 (Δ排名/Δ成本)', fontsize=12, fontweight='bold')
    ax2.set_title('边际效益分析', fontsize=13, fontweight='bold')
    ax2.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.7)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 边际效益曲线已保存: {output_path.name}")


def plot_scenario_comparison(scenario_results: Dict[str, pd.DataFrame],
                             output_path: Path):
    """绘制场景对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, (scenario, df) in enumerate(scenario_results.items()):
        ax = axes[idx]
        config = SCENARIO_CONFIGS[scenario]
        
        # 取前10个模型
        top_models = df.head(10)
        
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(top_models)))
        bars = ax.barh(range(len(top_models)), top_models['scenario_score'],
                      color=colors, edgecolor='black', linewidth=1)
        
        ax.set_yticks(range(len(top_models)))
        ax.set_yticklabels(top_models['model'], fontsize=9)
        ax.set_xlabel('Scenario Score', fontsize=11, fontweight='bold')
        ax.set_title(f'{config["name"]}\n{config["description"]}', 
                    fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # 添加数值标签
        for i, (bar, score) in enumerate(zip(bars, top_models['scenario_score'])):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                   f'{score:.3f}', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 场景对比图已保存: {output_path.name}")


# ============================================================================
# 雷达图可视化函数
# ============================================================================

def plot_radar_chart(df: pd.DataFrame,
                     categories: List[str],
                     model_col: str = 'model',
                     value_cols: List[str] = None,
                     output_path: Path = None,
                     title: str = 'Model Comparison Radar Chart',
                     figsize: tuple = (10, 10)):
    """
    绘制单模型多维度雷达图
    
    Args:
        df: 数据框
        categories: 维度类别列表
        model_col: 模型名称列
        value_cols: 数值列列表（与categories对应）
        output_path: 输出路径
        title: 图表标题
        figsize: 图表大小
    """
    if value_cols is None:
        value_cols = categories
    
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    
    # 计算角度
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # 闭合
    
    # 归一化数据
    df_norm = df.copy()
    for col in value_cols:
        col_min = df[col].min()
        col_max = df[col].max()
        if col_max > col_min:
            df_norm[col] = (df[col] - col_min) / (col_max - col_min)
        else:
            df_norm[col] = 0.5
    
    # 为每个模型绘制雷达图
    colors = plt.cm.Set3(np.linspace(0, 1, len(df)))
    
    for idx, (_, row) in enumerate(df_norm.iterrows()):
        values = [row[col] for col in value_cols]
        values += values[:1]  # 闭合
        
        ax.plot(angles, values, 'o-', linewidth=2, 
                label=row[model_col], color=colors[idx], alpha=0.7)
        ax.fill(angles, values, alpha=0.15, color=colors[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ 雷达图已保存: {output_path.name}")
    plt.close()


def plot_multi_model_radar(df: pd.DataFrame,
                           top_models: List[str],
                           categories: List[str],
                           value_cols: List[str],
                           output_path: Path,
                           title: str = 'Top Models Comparison Radar Chart'):
    """
    绘制多模型对比雷达图（Top模型）
    
    Args:
        df: 数据框
        top_models: 要比较的模型列表
        categories: 维度类别列表
        value_cols: 数值列列表
        output_path: 输出路径
        title: 图表标题
    """
    # 筛选Top模型
    df_top = df[df['model'].isin(top_models)].copy()
    
    if len(df_top) == 0:
        print(f"⚠ 未找到指定的模型: {top_models}")
        return
    
    plot_radar_chart(
        df=df_top,
        categories=categories,
        model_col='model',
        value_cols=value_cols,
        output_path=output_path,
        title=title
    )


def plot_scenario_radar(scenario_results: Dict[str, pd.DataFrame],
                        output_path: Path):
    """
    绘制场景对比雷达图
    
    Args:
        scenario_results: 场景结果字典
        output_path: 输出路径
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 14), subplot_kw=dict(polar=True))
    axes = axes.flatten()
    
    # 场景名称映射
    scenario_names = {
        'cost_sensitive': '成本敏感',
        'quality_priority': '质量优先',
        'balanced': '均衡',
        'speed_critical': '速度关键'
    }
    
    # 维度配置
    scenario_configs = {
        'cost_sensitive': {
            'categories': ['质量', '成本效益', '速度', '能耗效率', '稳定性'],
            'cols': ['quality', 'qpc', 'speed', 'energy', 'cbr'],
            'weights': [0.2, 0.8, 0.0, 0.0, 0.0]
        },
        'quality_priority': {
            'categories': ['质量', '成本效益', '速度', '能耗效率', '稳定性'],
            'cols': ['quality', 'qpc', 'speed', 'energy', 'cbr'],
            'weights': [0.8, 0.2, 0.0, 0.0, 0.0]
        },
        'balanced': {
            'categories': ['质量', '成本效益', '速度', '能耗效率', '稳定性'],
            'cols': ['quality', 'qpc', 'speed', 'energy', 'cbr'],
            'weights': [0.5, 0.5, 0.0, 0.0, 0.0]
        },
        'speed_critical': {
            'categories': ['质量', '成本效益', '速度', '能耗效率', '稳定性'],
            'cols': ['quality', 'qpc', 'speed', 'energy', 'cbr'],
            'weights': [0.3, 0.3, 0.4, 0.0, 0.0]
        }
    }
    
    for idx, (scenario, df_scenario) in enumerate(scenario_results.items()):
        if idx >= 4:
            break
            
        ax = axes[idx]
        config = scenario_configs.get(scenario, scenario_configs['balanced'])
        
        # 计算角度
        categories = config['categories']
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        # 获取Top 3模型
        df_top = df_scenario.head(3)
        
        # 归一化
        df_norm = df_top.copy()
        for col in config['cols']:
            if col in df_norm.columns:
                col_min = df_norm[col].min()
                col_max = df_norm[col].max()
                if col_max > col_min:
                    df_norm[col] = (df_norm[col] - col_min) / (col_max - col_min)
                else:
                    df_norm[col] = 0.5
        
        # 绘制
        colors = ['#2ecc71', '#3498db', '#e74c3c']
        for i, (_, row) in enumerate(df_norm.iterrows()):
            values = []
            for col in config['cols']:
                if col in row.index:
                    values.append(row[col])
                else:
                    values.append(0.5)
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, 
                   label=row['model'], color=colors[i], alpha=0.7)
            ax.fill(angles, values, alpha=0.1, color=colors[i])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=9)
        ax.set_ylim(0, 1)
        ax.set_title(f"{scenario_names.get(scenario, scenario)}\n{SCENARIO_CONFIGS[scenario]['description']}", 
                    fontsize=10, fontweight='bold', pad=10)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('场景化模型选择雷达图对比', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 场景雷达图已保存: {output_path.name}")


def plot_cost_quality_efficiency_radar(df: pd.DataFrame,
                                        top_n: int = 5,
                                        output_path: Path = None):
    """
    绘制成本-质量-效率综合雷达图
    
    Args:
        df: 成本效益数据框
        top_n: 显示Top N模型
        output_path: 输出路径
    """
    # 按QPC排序选择Top N模型
    df_sorted = df.sort_values('qpc', ascending=False).head(top_n)
    
    # 定义维度
    categories = ['质量', '速度', '能效', '成本效益', '综合评分']
    
    # 计算综合评分 (归一化后的加权平均)
    df_plot = df_sorted.copy()
    
    # 归一化各指标
    for col in ['quality', 'speed', 'energy', 'qpc']:
        col_min = df_plot[col].min()
        col_max = df_plot[col].max()
        if col_max > col_min:
            df_plot[f'{col}_norm'] = (df_plot[col] - col_min) / (col_max - col_min)
        else:
            df_plot[f'{col}_norm'] = 0.5
    
    # 综合评分 = 0.3*质量 + 0.3*速度 + 0.2*能效 + 0.2*成本效益
    df_plot['composite'] = (0.3 * df_plot['quality_norm'] + 
                           0.3 * df_plot['speed_norm'] + 
                           0.2 * (1 - df_plot['energy_norm']) + 
                           0.2 * df_plot['qpc_norm'])
    
    # 绘制雷达图
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    value_cols = ['quality_norm', 'speed_norm', 'energy_norm', 'qpc_norm', 'composite']
    
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(df_plot)))
    
    for idx, (_, row) in enumerate(df_plot.iterrows()):
        values = [row[col] for col in value_cols]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, 
               label=row['model'], color=colors[idx], alpha=0.7)
        ax.fill(angles, values, alpha=0.1, color=colors[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.set_title(f'Top {top_n} 模型综合能力雷达图\n(质量·速度·能效·成本效益)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ 综合能力雷达图已保存: {output_path.name}")
    plt.close()


# ============================================================================
# 主执行函数
# ============================================================================

def run_cost_benefit_analysis(tasks: List[str],
                              output_base_dir: Path,
                              cost_model: Optional[CostModel] = None,
                              user_weights: Optional[Dict[str, float]] = None):
    """运行完整的成本效益分析"""
    if cost_model is None:
        cost_model = CostModel()
    
    output_dir = output_base_dir / 'cost_benefit_analysis'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print("第5章: 成本效益分析与选择策略")
    print("="*80)
    
    # 5.1 & 5.2: 跨任务成本效益比较
    print("\n5.1-5.2: 成本核算与跨任务比较")
    print("-" * 80)
    df_cross_task = cross_task_cost_benefit_comparison(tasks, cost_model, output_dir)
    
    # 模型排序
    ranked_qpc = rank_models_by_cost_benefit(df_cross_task, 'qpc', output_dir)
    ranked_cbr = rank_models_by_cost_benefit(df_cross_task, 'cbr', output_dir)
    
    print(f"\nTop 5 模型 (按QPC排序):")
    print(ranked_qpc.head()[['rank', 'model', 'qpc', 'quality', 'total_cost']])
    
    # 5.3: 任务难度加权
    print("\n5.3: 任务难度加权的成本效益分析")
    print("-" * 80)
    task_difficulty = calculate_task_difficulty(df_cross_task, tasks)
    print("任务难度:")
    for task, diff in sorted(task_difficulty.items(), key=lambda x: x[1], reverse=True):
        print(f"  {task}: {diff:.4f}")
    
    df_weighted = difficulty_weighted_cost_benefit(
        df_cross_task, task_difficulty, user_weights, output_dir
    )
    print(f"\nTop 5 模型 (难度加权):")
    print(df_weighted.head()[['rank', 'model', 'weighted_qpc', 'weighted_quality', 'weighted_cost']])
    
    # 5.4: 场景化选择
    print("\n5.4: 场景化模型选择策略")
    print("-" * 80)
    
    # 按模型聚合数据，只对数值列计算平均
    numeric_cols = ['quality', 'energy', 'speed', 'total_cost', 'qpc', 'cbr']
    df_agg = df_cross_task.groupby('model')[numeric_cols].mean().reset_index()
    
    scenario_results = {}
    for scenario in SCENARIO_CONFIGS.keys():
        print(f"\n场景: {SCENARIO_CONFIGS[scenario]['name']}")
        df_scenario = scenario_based_selection(
            df_agg,
            scenario, output_dir
        )
        scenario_results[scenario] = df_scenario
        print(f"  推荐模型: {df_scenario.iloc[0]['model']}")
    
    # 5.5: 边际效益分析
    print("\n5.5: 成本-质量权衡的边际效益分析")
    print("-" * 80)
    df_avg = df_cross_task.groupby('model')[numeric_cols].mean().reset_index()
    marginal_results = marginal_benefit_analysis(df_avg, output_dir)
    
    if marginal_results['knee_model']:
        print(f"拐点模型: {marginal_results['knee_model']}")
    
    if marginal_results['fit_params']:
        print(f"成本-质量拟合: Q = {marginal_results['fit_params']['a']:.3f} * log(C) + {marginal_results['fit_params']['b']:.3f}")
        print(f"拟合优度 R²: {marginal_results['fit_params']['r2']:.3f}")
    
    # 生成可视化
    print("\n生成可视化图表...")
    print("-" * 80)
    plot_cost_benefit_scatter(df_avg, output_dir / 'cost_benefit_scatter.png')
    plot_marginal_benefit_curve(
        marginal_results['marginal_df'],
        df_avg.sort_values('total_cost'),
        marginal_results['fit_params'],
        output_dir / 'marginal_benefit_curve.png'
    )
    plot_scenario_comparison(scenario_results, output_dir / 'scenario_comparison.png')
    
    print("\n" + "="*80)
    print("成本效益分析完成!")
    print(f"结果保存在: {output_dir}")
    print("="*80)
    
    return {
        'cross_task': df_cross_task,
        'ranked_qpc': ranked_qpc,
        'ranked_cbr': ranked_cbr,
        'weighted': df_weighted,
        'scenarios': scenario_results,
        'marginal': marginal_results
    }


def run_single_type_cost_benefit_analysis(quality_type: str,
                                           cost_model: Optional[CostModel] = None,
                                           output_base_dir: Optional[Path] = None,
                                           verbose: bool = True) -> Dict:
    """
    对单一需求类型进行成本效益分析
    
    Args:
        quality_type: 'balanced', 'objective', 或 'subjective'
        cost_model: 成本模型
        output_base_dir: 输出目录
        verbose: 是否打印详细信息
    
    Returns:
        分析结果字典
    """
    if cost_model is None:
        cost_model = CostModel()
    
    if output_base_dir is None:
        output_base_dir = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results'
    
    # 质量类型名称映射
    TYPE_NAMES = {
        'balanced': '均衡配置',
        'objective': '客观任务为主',
        'subjective': '主观任务为主'
    }
    
    type_name = TYPE_NAMES.get(quality_type, quality_type)
    output_dir = output_base_dir / 'cost_benefit_analysis' / quality_type
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"成本效益分析 - {type_name}")
    print("="*80)
    
    # 加载预计算的质量得分
    if verbose:
        print(f"\n加载 {type_name} 质量得分数据...")
    quality_df = load_precomputed_quality_scores(quality_type, verbose=verbose)
    
    # 加载平均能耗和速度数据（跨任务平均）
    energy_dict, speed_dict = load_average_energy_speed_data(
        DATA_PATHS['energy'], DATA_PATHS['speed']
    )
    
    # 合并数据
    all_results = []
    for _, row in quality_df.iterrows():
        model = row['model']
        model_full = MODEL_MAPPING.get(model)
        
        if model_full and model_full in energy_dict and model_full in speed_dict:
            all_results.append({
                'model': model,
                'quality': row['quality'],
                'energy': energy_dict[model_full],
                'speed': speed_dict[model_full]
            })
    
    df = pd.DataFrame(all_results)
    
    if len(df) == 0:
        print(f"✗ 没有找到有效的模型数据")
        return None
    
    # 计算成本指标
    df = calculate_cost_metrics(df, cost_model)
    
    if verbose:
        print(f"\n有效模型数量: {len(df)}")
        print(f"质量范围: [{df['quality'].min():.4f}, {df['quality'].max():.4f}]")
        print(f"能耗范围: [{df['energy'].min():.4f}, {df['energy'].max():.4f}] J/token")
        print(f"速度范围: [{df['speed'].min():.2f}, {df['speed'].max():.2f}] tokens/s")
    
    # 保存数据
    data_file = output_dir / 'cost_benefit_data.csv'
    df.to_csv(data_file, index=False, encoding='utf-8-sig')
    if verbose:
        print(f"✓ 数据已保存: {data_file.name}")
    
    # 模型排序
    ranked_qpc = rank_models_by_cost_benefit(df, 'qpc', output_dir)
    ranked_cbr = rank_models_by_cost_benefit(df, 'cbr', output_dir)
    
    if verbose:
        print(f"\nTop 5 模型 (按QPC排序):")
        print(ranked_qpc.head()[['rank', 'model', 'qpc', 'quality', 'total_cost']])
    
    # 场景化选择
    scenario_results = {}
    for scenario in SCENARIO_CONFIGS.keys():
        if verbose:
            print(f"\n场景: {SCENARIO_CONFIGS[scenario]['name']}")
        df_scenario = scenario_based_selection(df, scenario, output_dir)
        scenario_results[scenario] = df_scenario
        if verbose:
            print(f"  推荐模型: {df_scenario.iloc[0]['model']}")
    
    # 边际效益分析
    if verbose:
        print("\n边际效益分析...")
    df_sorted = df.sort_values('total_cost').reset_index(drop=True)
    marginal_results = marginal_benefit_analysis(df_sorted, output_dir)
    
    if marginal_results['knee_model'] and verbose:
        print(f"拐点模型: {marginal_results['knee_model']}")
    
    # 生成可视化
    if verbose:
        print("\n生成可视化图表...")
    plot_cost_benefit_scatter(df, output_dir / 'cost_benefit_scatter.png')
    plot_marginal_benefit_curve(
        marginal_results['marginal_df'],
        df_sorted,
        marginal_results['fit_params'],
        output_dir / 'marginal_benefit_curve.png'
    )
    plot_scenario_comparison(scenario_results, output_dir / 'scenario_comparison.png')
    
    # 生成雷达图
    if verbose:
        print("\n生成雷达图...")
    
    # 准备综合评分数据
    df_radar = df.copy()
    for col in ['quality', 'speed', 'energy', 'qpc']:
        col_min = df_radar[col].min()
        col_max = df_radar[col].max()
        if col_max > col_min:
            df_radar[f'{col}_norm'] = (df_radar[col] - col_min) / (col_max - col_min)
        else:
            df_radar[f'{col}_norm'] = 0.5
    
    # 综合评分 = 0.3*质量 + 0.3*速度 + 0.2*能效 + 0.2*成本效益
    df_radar['composite'] = (0.3 * df_radar['quality_norm'] + 
                             0.3 * df_radar['speed_norm'] + 
                             0.2 * (1 - df_radar['energy_norm']) + 
                             0.2 * df_radar['qpc_norm'])
    
    # 1. 综合能力雷达图 (Top 5模型)
    plot_cost_quality_efficiency_radar(
        df_radar, 
        top_n=5, 
        output_path=output_dir / 'comprehensive_radar.png'
    )
    
    # 2. 多模型对比雷达图 (Top 5)
    top_5_models = ranked_qpc.head(5)['model'].tolist()
    plot_multi_model_radar(
        df=df_radar,
        top_models=top_5_models,
        categories=['质量', '速度', '能效', '成本效益', '综合评分'],
        value_cols=['quality_norm', 'speed_norm', 'energy_norm', 'qpc_norm', 'composite'],
        output_path=output_dir / 'top_models_radar.png',
        title=f'Top 5 模型综合能力雷达图 - {type_name}'
    )
    
    # 3. 场景对比雷达图
    plot_scenario_radar(
        scenario_results,
        output_path=output_dir / 'scenario_radar.png'
    )
    
    # 生成详细报告
    generate_single_type_report(quality_type, {
        'quality_type': quality_type,
        'data': df,
        'ranked_qpc': ranked_qpc,
        'ranked_cbr': ranked_cbr,
        'scenarios': scenario_results,
        'marginal': marginal_results
    }, output_dir, cost_model)
    
    print("\n" + "="*80)
    print(f"{type_name} 成本效益分析完成!")
    print(f"结果保存在: {output_dir}")
    print("="*80)
    
    return {
        'quality_type': quality_type,
        'data': df,
        'ranked_qpc': ranked_qpc,
        'ranked_cbr': ranked_cbr,
        'scenarios': scenario_results,
        'marginal': marginal_results
    }


def run_multi_type_cost_benefit_analysis(output_base_dir: Optional[Path] = None,
                                          cost_model: Optional[CostModel] = None,
                                          quality_types: List[str] = None) -> Dict[str, Dict]:
    """
    对多种需求类型进行成本效益分析
    
    Args:
        output_base_dir: 输出目录
        cost_model: 成本模型
        quality_types: 要分析的质量类型列表，默认分析所有三种
    
    Returns:
        包含各类型分析结果的字典
    """
    if cost_model is None:
        cost_model = CostModel()
    
    if output_base_dir is None:
        output_base_dir = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results'
    
    if quality_types is None:
        quality_types = ['balanced', 'objective', 'subjective']
    
    # 质量类型名称映射
    TYPE_NAMES = {
        'balanced': '均衡配置',
        'objective': '客观任务为主',
        'subjective': '主观任务为主'
    }
    
    print("\n" + "="*80)
    print("多类型成本效益分析")
    print("="*80)
    print(f"分析类型: {', '.join([TYPE_NAMES[t] for t in quality_types])}")
    print("="*80)
    
    all_results = {}
    
    for quality_type in quality_types:
        result = run_single_type_cost_benefit_analysis(
            quality_type=quality_type,
            cost_model=cost_model,
            output_base_dir=output_base_dir,
            verbose=True
        )
        if result:
            all_results[quality_type] = result
    
    # 生成对比报告
    if len(all_results) > 1:
        generate_comparison_report(all_results, output_base_dir, cost_model)
    
    print("\n" + "="*80)
    print("多类型成本效益分析完成!")
    print("="*80)
    
    return all_results


def generate_comparison_report(all_results: Dict[str, Dict],
                               output_base_dir: Path,
                               cost_model: CostModel):
    """生成多类型对比报告"""
    
    TYPE_NAMES = {
        'balanced': '均衡配置',
        'objective': '客观任务为主',
        'subjective': '主观任务为主'
    }
    
    report = []
    report.append("# 多类型成本效益对比分析报告")
    report.append("")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("---")
    report.append("")
    
    # 1. 各类型Top模型对比
    report.append("## 1. 各类型最佳模型对比")
    report.append("")
    report.append("| 需求类型 | 最佳QPC模型 | QPC值 | 最佳CBR模型 | CBR值 |")
    report.append("|----------|------------|-------|-------------|-------|")
    
    for qtype, result in all_results.items():
        if len(result['ranked_qpc']) > 0:
            best_qpc = result['ranked_qpc'].iloc[0]
            best_cbr = result['ranked_cbr'].iloc[0]
            report.append(f"| {TYPE_NAMES[qtype]} | {best_qpc['model']} | {best_qpc['qpc']:.4f} | "
                         f"{best_cbr['model']} | {best_cbr['cbr']:.4f} |")
    report.append("")
    
    # 2. 场景推荐对比
    report.append("## 2. 场景推荐模型对比")
    report.append("")
    
    for scenario in SCENARIO_CONFIGS.keys():
        report.append(f"### {SCENARIO_CONFIGS[scenario]['name']}")
        report.append("")
        report.append(f"**场景描述**: {SCENARIO_CONFIGS[scenario]['description']}")
        report.append("")
        report.append("| 需求类型 | 推荐模型 | 场景得分 |")
        report.append("|----------|----------|----------|")
        
        for qtype, result in all_results.items():
            if len(result['scenarios']) > 0 and scenario in result['scenarios']:
                best = result['scenarios'][scenario].iloc[0]
                report.append(f"| {TYPE_NAMES[qtype]} | {best['model']} | {best['scenario_score']:.4f} |")
        report.append("")
    
    # 3. 边际效益对比
    report.append("## 3. 边际效益分析对比")
    report.append("")
    
    for qtype, result in all_results.items():
        if result['marginal']['knee_model']:
            report.append(f"### {TYPE_NAMES[qtype]}")
            report.append("")
            report.append(f"- **拐点模型**: {result['marginal']['knee_model']}")
            if result['marginal']['fit_params']:
                params = result['marginal']['fit_params']
                report.append(f"- **拟合公式**: Q = {params['a']:.4f} × log(C) + {params['b']:.4f}")
                report.append(f"- **拟合优度 R²**: {params['r2']:.4f}")
            report.append("")
    
    # 4. 综合建议
    report.append("## 4. 综合建议")
    report.append("")
    report.append("基于多类型成本效益分析，提出以下建议：")
    report.append("")
    report.append("1. **均衡场景**: 推荐使用均衡配置(balanced)的分析结果")
    report.append("2. **技术应用**: 客观任务为主(objective)更适合工程实践")
    report.append("3. **内容创作**: 主观任务为主(subjective)更适合创意场景")
    report.append("")
    report.append("---")
    report.append("")
    report.append(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 保存报告
    report_file = output_base_dir / 'cost_benefit_analysis' / 'MULTI_TYPE_COMPARISON_REPORT.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"\n✓ 对比报告已生成: {report_file}")


def generate_single_type_report(quality_type: str,
                                 result: Dict,
                                 output_dir: Path,
                                 cost_model: CostModel):
    """为单一需求类型生成详细报告"""
    
    TYPE_NAMES = {
        'balanced': '均衡配置',
        'objective': '客观任务为主',
        'subjective': '主观任务为主'
    }
    
    type_name = TYPE_NAMES.get(quality_type, quality_type)
    df = result['data']
    ranked_qpc = result['ranked_qpc']
    ranked_cbr = result['ranked_cbr']
    scenario_results = result['scenarios']
    marginal_results = result['marginal']
    
    report = []
    report.append(f"# {type_name} 成本效益分析报告")
    report.append("")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**需求类型**: {type_name}")
    report.append("")
    report.append("---")
    report.append("")
    
    # 1. 数据概览
    report.append("## 1. 数据概览")
    report.append("")
    report.append(f"- **模型数量**: {len(df)}")
    report.append(f"- **质量范围**: [{df['quality'].min():.4f}, {df['quality'].max():.4f}]")
    report.append(f"- **能耗范围**: [{df['energy'].min():.4f}, {df['energy'].max():.4f}] J/token")
    report.append(f"- **速度范围**: [{df['speed'].min():.2f}, {df['speed'].max():.2f}] tokens/s")
    report.append(f"- **成本范围**: [${df['total_cost'].min():.6f}, ${df['total_cost'].max():.6f}]")
    report.append("")
    
    # 2. 成本核算模型
    report.append("## 2. 成本核算模型")
    report.append("")
    report.append("### 2.1 成本参数配置")
    report.append("")
    report.append(f"- **电价**: ${cost_model.energy_cost_per_kwh}/kWh")
    report.append(f"- **GPU折旧**: ${cost_model.gpu_depreciation_per_hour}/hour")
    report.append(f"- **时间权重**: {cost_model.inference_time_weight}")
    report.append("")
    report.append("### 2.2 成本计算公式")
    report.append("")
    report.append("1. **能耗成本**: `C_energy = (E × N) / 3600000 × P_kwh`")
    report.append("2. **时间成本**: `C_time = (N / Speed) / 3600 × D_gpu`")
    report.append("3. **总成本**: `C_total = C_energy + C_time`")
    report.append("")
    
    # 3. 成本效益指标
    report.append("## 3. 成本效益指标定义")
    report.append("")
    report.append("| 指标 | 定义 | 优化方向 | 说明 |")
    report.append("|------|------|----------|------|")
    report.append("| QPC | Quality per Cost = Q / C | 越大越好 | 单位成本的质量产出 |")
    report.append("| CBR | Cost-Benefit Ratio = C / Q | 越小越好 | 单位质量的成本投入 |")
    report.append("| 边际效益 | ΔQ / ΔC | 越大越好 | 成本增加带来的质量提升 |")
    report.append("")
    
    # 4. 模型排序
    report.append("## 4. 模型成本效益排序")
    report.append("")
    
    # 4.1 按QPC排序
    report.append("### 4.1 按质量成本比(QPC)排序")
    report.append("")
    report.append("| 排名 | 模型 | QPC | 质量得分 | 总成本($) | 能耗(J/token) | 速度(tokens/s) |")
    report.append("|------|------|-----|----------|-----------|---------------|----------------|")
    
    for _, row in ranked_qpc.iterrows():
        report.append(f"| {int(row['rank'])} | {row['model']} | {row['qpc']:.4f} | "
                     f"{row['quality']:.4f} | {row['total_cost']:.6f} | "
                     f"{row['energy']:.4f} | {row['speed']:.2f} |")
    report.append("")
    
    # 4.2 按CBR排序
    report.append("### 4.2 按成本效益比(CBR)排序")
    report.append("")
    report.append("CBR越小表示达到相同质量所需成本越低，是成本敏感场景的关键指标。")
    report.append("")
    report.append("| 排名 | 模型 | CBR | 质量得分 | 总成本($) |")
    report.append("|------|------|-----|----------|-----------|")
    
    for _, row in ranked_cbr.iterrows():
        if row['cbr'] != float('inf') and not pd.isna(row['cbr']):
            report.append(f"| {int(row['rank'])} | {row['model']} | {row['cbr']:.6f} | "
                         f"{row['quality']:.4f} | {row['total_cost']:.6f} |")
    report.append("")
    
    # 5. 场景化选择
    report.append("## 5. 场景化模型选择策略")
    report.append("")
    
    for scenario, df_scenario in scenario_results.items():
        config = SCENARIO_CONFIGS[scenario]
        report.append(f"### 5.{list(SCENARIO_CONFIGS.keys()).index(scenario)+1} {config['name']}")
        report.append("")
        report.append(f"**场景描述**: {config['description']}")
        report.append("")
        report.append("| 排名 | 模型 | 场景得分 | 质量 | 成本($) | 速度(tokens/s) |")
        report.append("|------|------|----------|------|---------|----------------|")
        
        for _, row in df_scenario.head(5).iterrows():
            report.append(f"| {int(row['rank'])} | {row['model']} | {row['scenario_score']:.4f} | "
                         f"{row['quality']:.4f} | {row['total_cost']:.6f} | {row['speed']:.2f} |")
        report.append("")
    
    # 6. 边际效益分析
    report.append("## 6. 成本-质量权衡的边际效益分析")
    report.append("")
    
    if marginal_results['fit_params']:
        params = marginal_results['fit_params']
        report.append("### 6.1 成本-质量拟合曲线")
        report.append("")
        report.append("采用对数函数拟合成本-质量关系:")
        report.append("")
        report.append(f"```")
        report.append(f"Q = {params['a']:.4f} × log(C) + {params['b']:.4f}")
        report.append(f"R² = {params['r2']:.4f}")
        report.append(f"```")
        report.append("")
        report.append("**解释**: 对数关系表明质量随成本增加呈现边际递减效应，")
        report.append("即初期成本投入带来显著质量提升，后期提升逐渐放缓。")
        report.append("")
    
    if marginal_results['knee_model']:
        report.append("### 6.2 拐点识别")
        report.append("")
        report.append(f"**拐点模型**: {marginal_results['knee_model']}")
        report.append("")
        report.append("拐点模型是边际效益最高的模型，代表成本-质量权衡的最优点。")
        report.append("在该点之前，增加成本能显著提升质量；之后质量提升放缓。")
        report.append("")
    
    if 'marginal_df' in marginal_results and len(marginal_results['marginal_df']) > 0:
        df_marginal = marginal_results['marginal_df']
        report.append("### 6.3 边际效益排序")
        report.append("")
        report.append("| 模型 | 成本($) | 质量 | 成本增量(排名) | 质量增量(排名) | 边际效益 |")
        report.append("|------|---------|------|---------------|---------------|----------|")
        
        df_sorted = df_marginal.sort_values('marginal_benefit', ascending=False)
        for _, row in df_sorted.head(10).iterrows():
            report.append(f"| {row['model']} | {row['cost']:.6f} | {row['quality']:.4f} | "
                         f"{row.get('delta_cost_rank', row.get('delta_cost', 0)):.1f} | {row.get('delta_quality_rank', row.get('delta_quality', 0)):.1f} | "
                         f"{row['marginal_benefit']:.2f} |")
        report.append("")
    
    # 7. 综合结论
    report.append("## 7. 综合结论与建议")
    report.append("")
    
    if len(ranked_qpc) > 0:
        best_qpc = ranked_qpc.iloc[0]
        report.append("### 7.1 主要发现")
        report.append("")
        report.append(f"1. **最佳质量成本比模型**: {best_qpc['model']}")
        report.append(f"   - QPC: {best_qpc['qpc']:.4f}")
        report.append(f"   - 质量: {best_qpc['quality']:.4f}")
        report.append(f"   - 成本: ${best_qpc['total_cost']:.6f}")
        report.append("")
    
    if marginal_results['knee_model']:
        report.append(f"2. **成本-质量拐点模型**: {marginal_results['knee_model']}")
        report.append("   - 该模型代表边际效益最优点")
        report.append("   - 适合追求性价比的应用场景")
        report.append("")
    
    report.append("### 7.2 决策建议")
    report.append("")
    report.append("1. **预算充足场景**: 选择质量最高的模型，忽略成本差异")
    report.append("2. **预算受限场景**: 选择QPC最高或CBR最低的模型")
    report.append("3. **均衡场景**: 选择拐点模型，获得最佳性价比")
    report.append("4. **实时应用**: 优先考虑速度，在满足延迟要求前提下选择质量最高的模型")
    report.append("")
    
    report.append("### 7.3 成本优化策略")
    report.append("")
    report.append("1. **模型量化**: 4-bit量化可显著降低能耗和时间成本，质量损失可控")
    report.append("2. **批处理**: 增大batch size可提高吞吐量，降低单token成本")
    report.append("3. **混合部署**: 根据任务难度动态选择模型，简单任务用小模型")
    report.append("4. **缓存策略**: 对常见查询缓存结果，避免重复推理")
    report.append("")
    
    report.append("---")
    report.append("")
    report.append(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append(f"**数据来源**: {type_name} 质量得分分析")
    report.append("")
    report.append("**分析工具**: Python + pandas + scipy + matplotlib")
    report.append("")
    
    # 保存报告
    report_file = output_dir / 'COST_BENEFIT_ANALYSIS_REPORT.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✓ 详细报告已生成: {report_file.name}")


if __name__ == '__main__':
    # 配置
    ALL_TASKS = ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']
    OUTPUT_DIR = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results'
    
    # 运行多类型成本效益分析
    results = run_multi_type_cost_benefit_analysis(
        output_base_dir=OUTPUT_DIR,
        cost_model=CostModel(
            energy_cost_per_kwh=0.08,
            gpu_depreciation_per_hour=0.25,
            inference_time_weight=1.2
        )
    )
