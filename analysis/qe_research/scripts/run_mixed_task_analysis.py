"""
混合任务帕累托前沿分析 - 执行脚本

从 scripts 目录运行，避免导入路径问题
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
from typing import Dict, List, Tuple

from pareto_core import (
    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
    identify_pareto_frontier_2d, identify_pareto_frontier_3d,
    calculate_hypervolume, calculate_spacing, find_knee_point,
    plot_pareto_2d, load_energy_speed_data, load_process_quality_data,
    perturbation_analysis, cross_validation_pareto,
    generate_pareto_report, print_analysis_summary
)

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================================
# 模型排除配置
# ============================================================================

# 需要排除的模型（存在数据问题和缺失值）
EXCLUDED_MODELS = [
    'qwen25_7b_hf_8bit',  # 在其他任务上数据有缺失
    'qwen--qwen2.5-7b-instruct:8bit',
    'qwen2.5-7b-instruct:8bit'
]

# ============================================================================
# 权重配置
# ============================================================================

WEIGHT_CONFIGS = {
    'objective': {
        'name': '客观任务为主',
        'description': '适用于技术应用、工程实践、需要精确结果的场景',
        'weights': {
            'code': 0.30,
            'math': 0.25,
            'qa': 0.20,
            'reasoning': 0.15,
            'creative': 0.05,
            'summary': 0.03,
            'translation': 0.02
        }
    },
    'subjective': {
        'name': '主观任务为主',
        'description': '适用于内容创作、文学创作、需要创造性的场景',
        'weights': {
            'creative': 0.35,
            'summary': 0.25,
            'translation': 0.20,
            'code': 0.10,
            'math': 0.05,
            'qa': 0.03,
            'reasoning': 0.02
        }
    },
    'balanced': {
        'name': '均衡配置',
        'description': '适用于通用评估、综合应用',
        'weights': {
            'code': 1/7,
            'math': 1/7,
            'qa': 1/7,
            'reasoning': 1/7,
            'creative': 1/7,
            'summary': 1/7,
            'translation': 1/7
        }
    }
}

ALL_TASKS = ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']


# ============================================================================
# 核心函数
# ============================================================================

def normalize_weights(weights: Dict[str, float], verbose: bool = True) -> Dict[str, float]:
    """归一化权重，使其和为1"""
    total = sum(weights.values())
    
    if abs(total - 1.0) < 1e-6:
        if verbose:
            print(f"✓ 权重已归一化（总和 = {total:.6f}）")
        return weights.copy()
    
    normalized = {k: v / total for k, v in weights.items()}
    
    if verbose:
        print(f"⚠ 权重未归一化（原始总和 = {total:.6f}），已自动归一化")
        print("归一化前后对比：")
        for task in weights:
            print(f"  {task:12s}: {weights[task]:.4f} → {normalized[task]:.4f}")
    
    return normalized


def load_all_task_quality_data(tasks: List[str], output_dir: Path, verbose: bool = True) -> Dict[str, pd.DataFrame]:
    """加载所有任务的质量数据（支持缓存）"""
    quality_data = {}
    
    for task in tasks:
        if verbose:
            print(f"\n加载任务: {task}")
        
        task_output_dir = output_dir / task
        task_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查缓存文件是否存在
        cache_file = task_output_dir / 'pca_quality_scores.csv'
        
        if cache_file.exists():
            if verbose:
                print(f"  → 从缓存加载: {cache_file.name}")
            try:
                df = pd.read_csv(cache_file)
                quality_data[task] = df
                if verbose:
                    print(f"  ✓ 成功加载 {len(df)} 个模型的质量数据（缓存）")
                continue
            except Exception as e:
                if verbose:
                    print(f"  ⚠ 缓存加载失败，重新计算: {str(e)}")
        
        # 缓存不存在，重新计算并保存
        try:
            df = load_process_quality_data(
                task_name=task,
                method='pca',
                normalize_method='zscore',
                use_raw=True,
                verbose=verbose,
                output_dir=task_output_dir
            )
            quality_data[task] = df
            
            # 保存到缓存
            cache_file = task_output_dir / 'pca_quality_scores.csv'
            df.to_csv(cache_file, index=False, encoding='utf-8-sig')
            if verbose:
                print(f"  ✓ 成功加载 {len(df)} 个模型的质量数据，已保存缓存")
        except Exception as e:
            print(f"  ✗ 加载任务 {task} 失败: {str(e)}")
            continue
    
    return quality_data


def aggregate_quality_scores(quality_data: Dict[str, pd.DataFrame], 
                            weights: Dict[str, float],
                            gamma: float = 0.5,
                            verbose: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, float]]:
    """
    聚合多个任务的质量得分（包含凸显能力计算）
    
    方法A: Q_i = Σ(w_t * s_{i,t}) / Σ(w_t)
    其中 s_{i,t} = q_{i,t} * α_t (凸显得分)
    α_t = e^(γ * d̃_t) (凸显因子)
    d_t = σ_t / μ_t (任务难度，变异系数)
    d̃_t = (d_t - min) / (max - min) (归一化难度)
    
    Args:
        quality_data: 按任务组织的质量数据
        weights: 用户偏好权重
        gamma: 凸显因子调节参数 (默认 0.5)
        verbose: 是否打印详细信息
    
    Returns:
        quality_df: 聚合质量得分
        task_scores_df: 各任务得分矩阵
        task_difficulty: 任务难度字典
    """
    weights = normalize_weights(weights, verbose=verbose)
    
    # 统一列名：将 'quality' 重命名为 'quality_score'（如果需要）
    for task, df in quality_data.items():
        if 'quality' in df.columns and 'quality_score' not in df.columns:
            quality_data[task] = df.rename(columns={'quality': 'quality_score'})
    
    # 排除指定模型
    excluded_count = 0
    for task, df in quality_data.items():
        original_count = len(df)
        quality_data[task] = df[~df['model'].isin(EXCLUDED_MODELS)]
        excluded_count += original_count - len(quality_data[task])
    
    if verbose and excluded_count > 0:
        print(f"\n⚠ 已排除 {len(EXCLUDED_MODELS)} 个模型: {', '.join(EXCLUDED_MODELS)}")
        print(f"  共排除 {excluded_count} 条数据记录")
    
    all_models = set()
    for df in quality_data.values():
        all_models.update(df['model'].unique())
    
    if verbose:
        print(f"\n共有 {len(all_models)} 个模型")
    
    # =========================================================================
    # 步骤1: 计算任务难度 d_t = σ_t / μ_t (变异系数)
    # 使用原始质量得分（避免使用 Z-score 归一化数据）
    # =========================================================================
    task_difficulty = {}
    for task, df in quality_data.items():
        raw_scores = df['quality_score'].values  # 原始质量得分
        mean_score = raw_scores.mean()
        std_score = raw_scores.std()
        
        # 使用变异系数，但避免均值接近0的问题
        if abs(mean_score) > 1e-6:
            cv = std_score / abs(mean_score)  # 变异系数
        else:
            cv = std_score  # 当均值接近0时，使用标准差作为难度指标
        
        task_difficulty[task] = cv
    
    if verbose:
        print(f"\n任务难度 (变异系数/标准差):")
        for task, diff in task_difficulty.items():
            print(f"  {task}: {diff:.4f}")
    
    # =========================================================================
    # 步骤2: 归一化难度到 [0,1]
    # =========================================================================
    difficulty_values = list(task_difficulty.values())
    min_diff = min(difficulty_values)
    max_diff = max(difficulty_values)
    
    if max_diff > min_diff:
        normalized_difficulty = {task: (diff - min_diff) / (max_diff - min_diff) 
                                  for task, diff in task_difficulty.items()}
    else:
        normalized_difficulty = {task: 0.0 for task in task_difficulty}
    
    # =========================================================================
    # 步骤3: 计算凸显因子 α_t = e^(γ * d̃_t)
    # =========================================================================
    saliency_factor = {task: np.exp(gamma * norm_diff) 
                       for task, norm_diff in normalized_difficulty.items()}
    
    if verbose:
        print(f"\n凸显因子 (γ={gamma}):")
        for task, factor in saliency_factor.items():
            print(f"  {task}: {factor:.4f}")
    
    # =========================================================================
    # 步骤4: 计算各模型的凸显得分和综合质量
    # =========================================================================
    results = []
    task_scores_matrix = []
    
    for model in sorted(all_models):
        weighted_score = 0.0
        task_scores = {'model': model}
        
        for task, weight in weights.items():
            if task in quality_data:
                df = quality_data[task]
                model_data = df[df['model'] == model]
                
                if len(model_data) > 0:
                    quality_score = model_data['quality_score'].values[0]
                    
                    # Z-score 归一化
                    all_scores = df['quality_score'].values
                    mean_score = all_scores.mean()
                    std_score = all_scores.std()
                    
                    if std_score > 0:
                        normalized_score = (quality_score - mean_score) / std_score
                    else:
                        normalized_score = 0.0
                    
                    # 凸显得分: s_{i,t} = q_{i,t} * α_t
                    saliency_score = normalized_score * saliency_factor[task]
                    
                    # 方法A: 加权平均
                    weighted_score += weight * saliency_score
                    
                    task_scores[task] = saliency_score
                else:
                    task_scores[task] = np.nan
        
        task_scores['aggregated_quality'] = weighted_score
        task_scores['aggregated_quality_raw'] = weighted_score  # 原始加权得分
        task_scores_matrix.append(task_scores)
        
        results.append({
            'model': model,
            'quality': weighted_score
        })
    
    task_scores_df = pd.DataFrame(task_scores_matrix)
    quality_df = pd.DataFrame(results)
    
    if verbose:
        print(f"\n✓ 成功聚合 {len(results)} 个模型的质量得分")
        print(f"  质量得分范围: [{min(r['quality'] for r in results):.4f}, {max(r['quality'] for r in results):.4f}]")
    
    return quality_df, task_scores_df, task_difficulty


def plot_quality_visualizations(quality_df: pd.DataFrame, 
                                 task_scores_df: pd.DataFrame,
                                 weights: Dict[str, float],
                                 config_name: str,
                                 output_dir: Path,
                                 verbose: bool = True):
    """聚合质量得分的可视化（调用所有可视化函数）"""
    if verbose:
        print("\n步骤4.1: 生成质量聚合可视化")
        print("-" * 60)
    
    # 1. 聚合质量柱状图
    plot_aggregated_quality_bar(
        quality_df, config_name, 
        output_dir / 'aggregated_quality_ranking.png'
    )
    
    # 2. 任务贡献堆叠柱状图
    plot_task_contribution_stacked_bar(
        task_scores_df, weights, config_name,
        output_dir / 'task_contribution_stacked.png'
    )
    
    # 3. 质量分布箱线图
    plot_quality_boxplot(
        task_scores_df, config_name,
        output_dir / 'quality_distribution_boxplot.png'
    )
    
    if verbose:
        print(f"\n✓ 质量聚合可视化完成")


def plot_task_difficulty(task_difficulty: Dict[str, float], output_path: Path):
    """绘制任务难度柱状图（变异系数）"""
    tasks = list(task_difficulty.keys())
    difficulties = list(task_difficulty.values())
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(tasks)))
    sorted_indices = np.argsort(difficulties)[::-1]
    
    bars = ax.bar([tasks[i] for i in sorted_indices], 
                  [difficulties[i] for i in sorted_indices],
                  color=[colors[i] for i in sorted_indices],
                  edgecolor='black', linewidth=1.5)
    
    for bar, diff in zip(bars, [difficulties[i] for i in sorted_indices]):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                f'{diff:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Task Difficulty (CV = std/mean)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Coefficient of Variation', fontsize=12, fontweight='bold')
    ax.set_title('Task Difficulty Ranking (Higher CV = Harder Task)', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, max(difficulties) * 1.15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 任务难度图已保存: {output_path.name}")


def plot_saliency_factor(saliency_factor: Dict[str, float], output_path: Path):
    """绘制凸显因子柱状图"""
    tasks = list(saliency_factor.keys())
    factors = list(saliency_factor.values())
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(tasks)))
    sorted_indices = np.argsort(factors)[::-1]
    
    bars = ax.bar([tasks[i] for i in sorted_indices], 
                  [factors[i] for i in sorted_indices],
                  color=[colors[i] for i in sorted_indices],
                  edgecolor='black', linewidth=1.5)
    
    for bar, factor in zip(bars, [factors[i] for i in sorted_indices]):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                f'{factor:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Task Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Saliency Factor (alpha = exp(gamma * d_tilde))', fontsize=12, fontweight='bold')
    ax.set_title('Task Saliency Factor (Higher difficulty -> Higher alpha)', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, max(factors) * 1.15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 凸显因子图已保存: {output_path.name}")


def plot_difficulty_saliency_relationship(task_difficulty: Dict[str, float],
                                           saliency_factor: Dict[str, float],
                                           output_path: Path):
    """绘制难度-凸显因子关系图"""
    tasks = list(task_difficulty.keys())
    difficulties = [task_difficulty[t] for t in tasks]
    factors = [saliency_factor[t] for t in tasks]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scatter = ax.scatter(difficulties, factors, c=range(len(tasks)), 
                         cmap='viridis', s=200, edgecolor='black', linewidth=1.5)
    
    for i, task in enumerate(tasks):
        ax.annotate(task, (difficulties[i], factors[i]), 
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=11, fontweight='bold')
    
    # 添加趋势线
    z = np.polyfit(difficulties, factors, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(difficulties), max(difficulties), 100)
    ax.plot(x_line, p(x_line), 'r--', linewidth=2, alpha=0.7, label='趋势线')
    
    ax.set_xlabel('Task Difficulty (CV)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Saliency Factor (alpha)', fontsize=12, fontweight='bold')
    ax.set_title('Difficulty-Saliency Relationship (alpha = exp(gamma * d_tilde))', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper left')
    ax.grid(alpha=0.3, linestyle='--')
    
    plt.colorbar(scatter, ax=ax, label='任务索引')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 难度-凸显因子关系图已保存: {output_path.name}")


def plot_raw_vs_saliency_comparison(task_scores_df: pd.DataFrame,
                                     saliency_factor: Dict[str, float],
                                     output_path: Path):
    """绘制原始Z-score vs 凸显得分对比图"""
    tasks = [col for col in task_scores_df.columns if col not in ['model', 'aggregated_quality', 'aggregated_quality_raw']]
    
    # 计算每个任务的平均原始Z-score和平均凸显得分
    raw_means = []
    saliency_means = []
    
    for task in tasks:
        raw_means.append(task_scores_df[task].mean())
        saliency_means.append(task_scores_df[task].mean() * saliency_factor[task])
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(tasks))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, raw_means, width, label='原始 Z-score', 
                   color='steelblue', edgecolor='black', alpha=0.8)
    bars2 = ax.bar(x + width/2, saliency_means, width, label='凸显得分 (×α)',
                   color='coral', edgecolor='black', alpha=0.8)
    
    ax.set_xlabel('Task Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Raw Z-score vs Saliency Score Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(tasks)
    ax.legend(loc='upper right')
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 原始vs凸显得分对比图已保存: {output_path.name}")


def plot_saliency_intermediate_results(task_difficulty: Dict[str, float],
                                        saliency_factor: Dict[str, float],
                                        task_scores_df: pd.DataFrame,
                                        output_dir: Path,
                                        verbose: bool = True):
    """绘制凸显能力计算的中间结果可视化"""
    if verbose:
        print("\n步骤2.1: 生成凸显能力中间结果可视化")
        print("-" * 60)
    
    # 1. 任务难度柱状图
    plot_task_difficulty(task_difficulty, output_dir / 'task_difficulty.png')
    
    # 2. 凸显因子柱状图
    plot_saliency_factor(saliency_factor, output_dir / 'saliency_factor.png')
    
    # 3. 难度-凸显因子关系图
    plot_difficulty_saliency_relationship(task_difficulty, saliency_factor,
                                          output_dir / 'difficulty_saliency_relationship.png')
    
    # 4. 原始vs凸显得分对比
    plot_raw_vs_saliency_comparison(task_scores_df, saliency_factor,
                                     output_dir / 'raw_vs_saliency_comparison.png')
    
    if verbose:
        print(f"\n✓ 凸显能力中间结果可视化完成")


def merge_energy_speed_data(quality_df: pd.DataFrame, 
                            tasks: List[str],
                            verbose: bool = True) -> pd.DataFrame:
    """合并能耗和速度数据"""
    merged_data = []
    
    for _, row in quality_df.iterrows():
        model = row['model']
        quality = row['quality']
        
        # 使用 MODEL_MAPPING 转换模型名称
        model_full = MODEL_MAPPING.get(model)
        if not model_full:
            if verbose:
                print(f"Warning: Model '{model}' not in MODEL_MAPPING, skipping")
            continue
        
        energies = []
        speeds = []
        
        for task in tasks:
            energy_dict, speed_dict = load_energy_speed_data(
                task, 
                DATA_PATHS['energy'], 
                DATA_PATHS['speed']
            )
            
            if model_full in energy_dict:
                energies.append(energy_dict[model_full])
            if model_full in speed_dict:
                speeds.append(speed_dict[model_full])
        
        avg_energy = np.mean(energies) if energies else np.nan
        avg_speed = np.mean(speeds) if speeds else np.nan
        
        merged_data.append({
            'model': model,
            'quality': quality,
            'energy': avg_energy,
            'speed': avg_speed
        })
    
    df = pd.DataFrame(merged_data)
    
    # 显示缺失数据信息
    if verbose:
        missing_energy = df['energy'].isna().sum()
        missing_speed = df['speed'].isna().sum()
        if missing_energy > 0 or missing_speed > 0:
            print(f"\nData missing info:")
            print(f"  Missing energy data: {missing_energy} models")
            print(f"  Missing speed data: {missing_speed} models")
            if missing_energy > 0:
                missing_models = df[df['energy'].isna()]['model'].tolist()
                print(f"  Models missing energy: {', '.join(missing_models)}")
            if missing_speed > 0:
                missing_models = df[df['speed'].isna()]['model'].tolist()
                print(f"  Models missing speed: {', '.join(missing_models)}")
    
    # 删除包含 NaN 的行
    original_count = len(df)
    df = df.dropna()
    dropped_count = original_count - len(df)
    
    if verbose:
        if dropped_count > 0:
            print(f"\nExcluded {dropped_count} models due to missing data")
        print(f"\nMerged data: {len(df)} models")
        if len(df) > 0:
            print(f"  Energy range: [{df['energy'].min():.6f}, {df['energy'].max():.6f}] J/token")
            print(f"  Speed range: [{df['speed'].min():.2f}, {df['speed'].max():.2f}] tokens/s")
        else:
            print(f"  Warning: No models with complete data!")
    
    return df


def plot_task_weights(weights: Dict[str, float], config_name: str, output_path: Path):
    """绘制任务权重分布图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    tasks = list(weights.keys())
    values = list(weights.values())
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(tasks)))
    bars = ax.bar(tasks, values, color=colors, edgecolor='black', linewidth=1.5)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2%}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('任务类型', fontsize=12, fontweight='bold')
    ax.set_ylabel('权重', fontsize=12, fontweight='bold')
    ax.set_title(f'任务权重分布 - {WEIGHT_CONFIGS[config_name]["name"]}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, max(values) * 1.15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 任务权重图已保存: {output_path.name}")


def plot_quality_heatmap(task_scores_df: pd.DataFrame, config_name: str, output_path: Path):
    """绘制模型×任务质量热力图"""
    heatmap_data = task_scores_df.set_index('model')
    heatmap_data = heatmap_data.drop('aggregated_quality', axis=1, errors='ignore')
    
    if 'aggregated_quality' in task_scores_df.columns:
        sorted_models = task_scores_df.sort_values('aggregated_quality', ascending=False)['model'].values
        heatmap_data = heatmap_data.loc[sorted_models]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='RdYlGn', 
                cbar_kws={'label': '归一化质量得分'},
                linewidths=0.5, linecolor='gray',
                vmin=0, vmax=1, ax=ax)
    
    ax.set_title(f'模型×任务质量热力图 - {WEIGHT_CONFIGS[config_name]["name"]}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('任务类型', fontsize=12, fontweight='bold')
    ax.set_ylabel('模型', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 质量热力图已保存: {output_path.name}")


def plot_aggregated_quality_bar(quality_df: pd.DataFrame, config_name: str, output_path: Path):
    """绘制聚合质量柱状图（模型排名）"""
    sorted_df = quality_df.sort_values('quality', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(sorted_df)))
    bars = ax.barh(sorted_df['model'], sorted_df['quality'], color=colors, edgecolor='black', linewidth=0.5)
    
    for bar, score in zip(bars, sorted_df['quality']):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2.,
                f'{score:.3f}', va='center', fontsize=9)
    
    ax.set_xlabel('聚合质量得分 (Z-score)', fontsize=12, fontweight='bold')
    ax.set_ylabel('模型', fontsize=12, fontweight='bold')
    ax.set_title(f'模型聚合质量排名 - {WEIGHT_CONFIGS[config_name]["name"]}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 聚合质量柱状图已保存: {output_path.name}")


def plot_task_contribution_stacked_bar(task_scores_df: pd.DataFrame, 
                                        weights: Dict[str, float],
                                        config_name: str, output_path: Path):
    """绘制任务贡献堆叠柱状图"""
    plot_df = task_scores_df.copy()
    tasks = [col for col in plot_df.columns if col not in ['model', 'aggregated_quality']]
    
    # 按聚合质量排序
    plot_df = plot_df.sort_values('aggregated_quality', ascending=True)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    colors = plt.cm.Set2(np.linspace(0, 1, len(tasks)))
    bottom = np.zeros(len(plot_df))
    
    for i, task in enumerate(tasks):
        contribution = plot_df[task].fillna(0) * weights.get(task, 0)
        ax.barh(plot_df['model'], contribution, left=bottom, 
                color=colors[i], label=task, edgecolor='white', linewidth=0.5)
        bottom += contribution.values
    
    ax.set_xlabel('加权贡献得分', fontsize=12, fontweight='bold')
    ax.set_ylabel('模型', fontsize=12, fontweight='bold')
    ax.set_title(f'任务权重贡献分解 - {WEIGHT_CONFIGS[config_name]["name"]}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(title='任务类型', loc='lower right', fontsize=9)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 任务贡献堆叠柱状图已保存: {output_path.name}")


def plot_quality_boxplot(task_scores_df: pd.DataFrame, config_name: str, output_path: Path):
    """绘制各任务质量得分箱线图"""
    tasks = [col for col in task_scores_df.columns if col not in ['model', 'aggregated_quality']]
    
    # 准备数据
    box_data = []
    for task in tasks:
        for score in task_scores_df[task].dropna():
            box_data.append({'task': task, 'score': score})
    box_df = pd.DataFrame(box_data)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(tasks)))
    bp = ax.boxplot([task_scores_df[task].dropna() for task in tasks],
                    tick_labels=tasks, patch_artist=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_xlabel('任务类型', fontsize=12, fontweight='bold')
    ax.set_ylabel('Z-score 归一化质量得分', fontsize=12, fontweight='bold')
    ax.set_title(f'各任务质量得分分布 - {WEIGHT_CONFIGS[config_name]["name"]}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.7, label='均值=0')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 质量分布箱线图已保存: {output_path.name}")


def run_mixed_task_analysis(config_name: str, output_base_dir: Path):
    """运行混合任务分析"""
    config = WEIGHT_CONFIGS[config_name]
    output_dir = output_base_dir / config_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"混合任务帕累托前沿分析 - {config['name']}")
    print("="*80)
    print(f"配置: {config_name}")
    print(f"描述: {config['description']}")
    print(f"输出目录: {output_dir}")
    print("="*80)
    
    # 1. 加载质量数据
    print("\n步骤1: 加载质量数据")
    print("-" * 80)
    quality_data = load_all_task_quality_data(ALL_TASKS, output_dir, verbose=True)
    
    if not quality_data:
        print("✗ 没有成功加载任何任务数据，退出")
        return
    
    # 2. 聚合质量得分
    print("\n步骤2: 聚合质量得分")
    print("-" * 80)
    quality_df, task_scores_df, task_difficulty = aggregate_quality_scores(
        quality_data, config['weights'], gamma=0.5, verbose=True
    )
    
    task_scores_file = output_dir / 'task_quality_scores.csv'
    task_scores_df.to_csv(task_scores_file, index=False, encoding='utf-8-sig')
    print(f"✓ 任务得分矩阵已保存: {task_scores_file.name}")
    
    # 保存各任务的PCA原始得分数据
    pca_scores_list = []
    for task, df in quality_data.items():
        task_pca_df = df[['model', 'quality_score']].copy()
        task_pca_df['task'] = task
        pca_scores_list.append(task_pca_df)
    
    if pca_scores_list:
        all_pca_scores = pd.concat(pca_scores_list, ignore_index=True)
        pca_scores_file = output_dir / 'pca_scores_all_tasks.csv'
        all_pca_scores.to_csv(pca_scores_file, index=False, encoding='utf-8-sig')
        print(f"✓ PCA得分数据已保存: {pca_scores_file.name}")
    
    # 保存任务难度信息
    difficulty_file = output_dir / 'task_difficulty.csv'
    difficulty_values = list(task_difficulty.values())
    min_diff = min(difficulty_values)
    max_diff = max(difficulty_values)
    
    difficulty_df = pd.DataFrame([
        {'task': task, 'difficulty_cv': diff, 
         'saliency_factor': np.exp(0.5 * (diff - min_diff) / (max_diff - min_diff if max_diff > min_diff else 1))}
        for task, diff in task_difficulty.items()
    ])
    difficulty_df.to_csv(difficulty_file, index=False, encoding='utf-8-sig')
    print(f"✓ 任务难度信息已保存: {difficulty_file.name}")
    
    # 2.1 凸显能力中间结果可视化
    saliency_factor = {
        task: np.exp(0.5 * (diff - min_diff) / (max_diff - min_diff if max_diff > min_diff else 1))
        for task, diff in task_difficulty.items()
    }
    plot_saliency_intermediate_results(task_difficulty, saliency_factor, task_scores_df, output_dir, verbose=True)
    
    # 3. 合并能耗和速度数据
    print("\n步骤3: 合并能耗和速度数据")
    print("-" * 80)
    df = merge_energy_speed_data(quality_df, ALL_TASKS, verbose=True)
    
    merged_file = output_dir / 'merged_data.csv'
    df.to_csv(merged_file, index=False, encoding='utf-8-sig')
    print(f"✓ 合并数据已保存: {merged_file.name}")
    
    # 4. 生成可视化
    print("\n步骤4: 生成可视化")
    print("-" * 80)
    
    plot_task_weights(config['weights'], config_name, output_dir / 'task_weights.png')
    plot_quality_heatmap(task_scores_df, config_name, output_dir / 'quality_heatmap.png')
    
    # 4.1 聚合质量可视化（新增）
    plot_quality_visualizations(quality_df, task_scores_df, config['weights'], config_name, output_dir, verbose=True)
    
    # 5. 帕累托前沿分析
    print("\n步骤5: 帕累托前沿分析")
    print("-" * 80)
    
    pareto_qe = identify_pareto_frontier_2d(df, 'quality', 'energy', x_minimize=False, y_minimize=True)
    print(f"✓ 质量-能耗前沿: {pareto_qe.sum()} 个模型")
    
    pareto_qs = identify_pareto_frontier_2d(df, 'quality', 'speed', x_minimize=False, y_minimize=False)
    print(f"✓ 质量-速度前沿: {pareto_qs.sum()} 个模型")
    
    pareto_3d = identify_pareto_frontier_3d(df)
    print(f"✓ 三维前沿: {pareto_3d.sum()} 个模型")
    
    # 6. 生成帕累托图
    print("\n步骤6: 生成帕累托图")
    print("-" * 80)
    
    plot_pareto_2d(df, pareto_qe, 'quality', 'energy',
                   f'混合任务：质量-能耗帕累托前沿 ({config["name"]})',
                   output_dir / 'pareto_quality_energy.png',
                   '综合质量得分', '平均能耗 (J/token)',
                   x_minimize=False, y_minimize=True)
    
    plot_pareto_2d(df, pareto_qs, 'quality', 'speed',
                   f'混合任务：质量-速度帕累托前沿 ({config["name"]})',
                   output_dir / 'pareto_quality_speed.png',
                   '综合质量得分', '平均速度 (tokens/s)',
                   x_minimize=False, y_minimize=False)
    
    # 7. 计算定量指标
    print("\n步骤7: 计算定量指标")
    print("-" * 80)
    
    hv_qe = calculate_hypervolume(df, pareto_qe, 'quality', 'energy')
    print(f"✓ 超体积（质量-能耗）: {hv_qe:.4f}")
    
    spacing_qe = calculate_spacing(df, pareto_qe, 'quality', 'energy')
    print(f"✓ 间距指标（质量-能耗）: {spacing_qe:.4f}")
    
    knee = find_knee_point(df, pareto_qe, 'quality', 'energy')
    print(f"✓ 拐点模型: {knee}")
    
    # 8. 稳健性分析
    print("\n步骤8: 稳健性分析")
    print("-" * 80)
    
    print("扰动分析（质量-能耗前沿）...")
    robustness_qe = perturbation_analysis(df, 'quality', 'energy',
                                          x_minimize=False, y_minimize=True,
                                          noise_level=0.05, n_iterations=100)
    print(f"✓ 前沿一致性: {robustness_qe['mean_consistency']:.2%}")
    
    print("交叉验证分析（质量-能耗前沿）...")
    cross_val_qe = cross_validation_pareto(df, 'quality', 'energy',
                                           x_minimize=False, y_minimize=True,
                                           n_folds=5)
    print(f"✓ 交叉验证一致性: {cross_val_qe['mean_consistency']:.2%}")
    
    results = {
        'pareto_qe': pareto_qe,
        'pareto_qs': pareto_qs,
        'pareto_3d': pareto_3d,
        'hypervolume_qe': hv_qe,
        'spacing_qe': spacing_qe,
        'knee_point': knee,
        'robustness_qe': robustness_qe,
        'cross_val_qe': cross_val_qe
    }
    
    # 9. 生成报告
    print("\n步骤9: 生成报告")
    print("-" * 80)
    
    task_config = {
        'task_name': 'mixed',
        'task_name_cn': f'混合任务 - {config["name"]}',
        'quality_metric': '综合质量得分',
        'quality_method': 'weighted_aggregation',
        'report_filename': 'MIXED_TASK_ANALYSIS_REPORT.md'
    }
    
    report_path = generate_pareto_report(df, results, output_dir, task_config)
    print(f"✓ 报告已保存: {report_path.name}")
    
    print_analysis_summary(df, results, f"混合任务 - {config['name']}")
    
    print("\n" + "="*80)
    print(f"分析完成！配置: {config_name}")
    print("="*80)
    print(f"输出目录: {output_dir}")


def main():
    """主函数"""
    output_base_dir = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'mixed_task_analysis' / 'task_02'
    
    print("\n" + "="*80)
    print("混合任务帕累托前沿分析 - 批量执行")
    print("="*80)
    print(f"输出基础目录: {output_base_dir}")
    print(f"配置数量: {len(WEIGHT_CONFIGS)}")
    print("="*80)
    
    for idx, config_name in enumerate(WEIGHT_CONFIGS.keys(), 1):
        print(f"\n\n{'#'*80}")
        print(f"# 进度: {idx}/{len(WEIGHT_CONFIGS)} - 配置: {config_name}")
        print(f"{'#'*80}\n")
        
        try:
            run_mixed_task_analysis(config_name, output_base_dir)
            print(f"\n✓ 配置 {config_name} 完成！")
        except Exception as e:
            print(f"\n✗ 配置 {config_name} 失败: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n\n" + "="*80)
    print("所有配置分析完成！")
    print("="*80)
    print(f"结果保存在: {output_base_dir}")
    print("="*80)


if __name__ == '__main__':
    main()
