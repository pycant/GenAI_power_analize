"""
权重敏感性分析脚本

基于已保存的PCA得分数据，分析权重参数变化对质效比结果的影响
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import itertools
from scipy.stats import spearmanr, kendalltau

# 导入混合任务分析的函数
sys.path.append(str(Path(__file__).parent))
from run_mixed_task_analysis import (
    normalize_weights, aggregate_quality_scores, merge_energy_speed_data,
    WEIGHT_CONFIGS, ALL_TASKS, EXCLUDED_MODELS
)

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================================
# 敏感性分析配置
# ============================================================================

# 权重扰动范围
PERTURBATION_LEVELS = [0.1, 0.2, 0.3, 0.5]  # 扰动幅度

# 权重网格搜索范围（用于全局敏感性分析）
WEIGHT_GRID_POINTS = 3  # 每个维度的网格点数（减少计算量）

# 分析输出目录
SENSITIVITY_OUTPUT_DIR = project_root / 'analysis' / 'qe_research' / 'results' / 'sensitivity_analysis'
# ============================================================================
# 数据加载函数
# ============================================================================

def load_pca_scores_from_cache(cache_file: Path) -> Dict[str, pd.DataFrame]:
    """从缓存文件加载PCA得分数据"""
    if not cache_file.exists():
        raise FileNotFoundError(f"缓存文件不存在: {cache_file}")
    
    # 读取数据
    df = pd.read_csv(cache_file)
    print(f"✓ 从缓存加载数据: {len(df)} 条记录")
    
    # 按任务分组
    quality_data = {}
    for task in df['task'].unique():
        task_df = df[df['task'] == task][['model', 'quality_score']].copy()
        quality_data[task] = task_df
        print(f"  - {task}: {len(task_df)} 个模型")
    
    return quality_data


def simulate_quality_data_from_pca(pca_scores: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """将PCA得分数据转换为质量数据格式（兼容原有函数）"""
    quality_data = {}
    
    for task, df in pca_scores.items():
        # 重命名列以匹配原有格式
        quality_df = df.rename(columns={'quality_score': 'quality_score'}).copy()
        quality_data[task] = quality_df
    
    return quality_data


# ============================================================================
# 敏感性分析核心函数
# ============================================================================

def perturb_weights(base_weights: Dict[str, float], 
                   perturbation_level: float,
                   n_samples: int = 100) -> List[Dict[str, float]]:
    """生成权重扰动样本
    
    Args:
        base_weights: 基准权重配置
        perturbation_level: 扰动幅度 (0-1)
        n_samples: 生成样本数量
    
    Returns:
        扰动权重配置列表
    """
    perturbed_weights = []
    
    for _ in range(n_samples):
        # 生成随机扰动
        perturbation = {}
        for task in base_weights:
            # 使用正态分布生成扰动
            noise = np.random.normal(0, perturbation_level * base_weights[task])
            perturbation[task] = max(0.001, base_weights[task] + noise)  # 确保权重为正
        
        # 归一化权重
        normalized = normalize_weights(perturbation, verbose=False)
        perturbed_weights.append(normalized)
    
    return perturbed_weights


def generate_weight_grid(tasks: List[str], n_points: int = 5) -> List[Dict[str, float]]:
    """生成权重网格（用于全局敏感性分析）
    
    Args:
        tasks: 任务列表
        n_points: 每个维度的网格点数
    
    Returns:
        权重配置网格
    """
    # 生成每个任务的权重候选值
    weight_values = np.linspace(0.05, 0.8, n_points)
    
    # 生成所有组合（限制总数以避免组合爆炸）
    if len(tasks) <= 4:
        # 小规模：完整网格
        combinations = list(itertools.product(weight_values, repeat=len(tasks)))
    else:
        # 大规模：随机采样
        n_samples = min(200, n_points ** len(tasks))  # 减少样本数
        combinations = []
        for _ in range(n_samples):
            combo = [np.random.choice(weight_values) for _ in tasks]
            combinations.append(tuple(combo))
    
    # 转换为权重字典并归一化
    weight_configs = []
    for combo in combinations:
        weights = dict(zip(tasks, combo))
        normalized = normalize_weights(weights, verbose=False)
        weight_configs.append(normalized)
    
    return weight_configs


def calculate_ranking_stability(rankings: List[pd.Series]) -> Dict[str, float]:
    """计算排名稳定性指标
    
    Args:
        rankings: 排名序列列表
    
    Returns:
        稳定性指标字典
    """
    if len(rankings) < 2:
        return {'spearman_mean': 1.0, 'kendall_mean': 1.0, 'top3_stability': 1.0}
    
    # 计算两两相关性
    spearman_corrs = []
    kendall_corrs = []
    
    for i in range(len(rankings)):
        for j in range(i + 1, len(rankings)):
            # 找到共同模型
            common_models = set(rankings[i].index) & set(rankings[j].index)
            if len(common_models) >= 3:
                common_models_list = list(common_models)
                rank_i = rankings[i].loc[common_models_list]
                rank_j = rankings[j].loc[common_models_list]
                
                spearman_corr, _ = spearmanr(rank_i.values, rank_j.values)
                kendall_corr, _ = kendalltau(rank_i.values, rank_j.values)
                
                spearman_corrs.append(spearman_corr)
                kendall_corrs.append(kendall_corr)
    
    # 计算Top-3稳定性
    top3_stability = calculate_top_k_stability(rankings, k=3)
    
    return {
        'spearman_mean': np.mean(spearman_corrs) if spearman_corrs else 1.0,
        'kendall_mean': np.mean(kendall_corrs) if kendall_corrs else 1.0,
        'top3_stability': top3_stability
    }


def calculate_top_k_stability(rankings: List[pd.Series], k: int = 3) -> float:
    """计算Top-K排名稳定性"""
    if len(rankings) < 2:
        return 1.0
    
    top_k_sets = []
    for ranking in rankings:
        top_k = set(ranking.nlargest(k).index)
        top_k_sets.append(top_k)
    
    # 计算交集比例
    intersection_ratios = []
    for i in range(len(top_k_sets)):
        for j in range(i + 1, len(top_k_sets)):
            intersection = len(top_k_sets[i] & top_k_sets[j])
            union = len(top_k_sets[i] | top_k_sets[j])
            if union > 0:
                intersection_ratios.append(intersection / union)
    
    return np.mean(intersection_ratios) if intersection_ratios else 1.0
# ============================================================================
# 敏感性分析执行函数
# ============================================================================

def run_perturbation_analysis(quality_data: Dict[str, pd.DataFrame],
                             base_config_name: str,
                             output_dir: Path,
                             verbose: bool = True) -> Dict:
    """运行权重扰动敏感性分析"""
    base_config = WEIGHT_CONFIGS[base_config_name]
    base_weights = base_config['weights']
    
    results = {
        'base_config': base_config_name,
        'perturbation_results': {},
        'stability_metrics': {}
    }
    
    if verbose:
        print(f"\n权重扰动敏感性分析 - {base_config['name']}")
        print("=" * 60)
    
    # 计算基准结果
    base_quality_df, base_task_scores_df, base_difficulty = aggregate_quality_scores(
        quality_data, base_weights, gamma=0.5, verbose=False
    )
    base_ranking = base_quality_df.set_index('model')['quality'].sort_values(ascending=False)
    
    if verbose:
        print(f"基准配置Top-5模型:")
        for i, (model, score) in enumerate(base_ranking.head(5).items(), 1):
            print(f"  {i}. {model}: {score:.4f}")
    
    # 对每个扰动级别进行分析
    for perturbation_level in PERTURBATION_LEVELS:
        if verbose:
            print(f"\n扰动级别: {perturbation_level:.1%}")
        
        # 生成扰动权重
        perturbed_weights_list = perturb_weights(base_weights, perturbation_level, n_samples=50)
        
        # 计算扰动结果
        perturbed_rankings = []
        quality_scores_list = []
        
        for weights in perturbed_weights_list:
            try:
                quality_df, _, _ = aggregate_quality_scores(
                    quality_data, weights, gamma=0.5, verbose=False
                )
                ranking = quality_df.set_index('model')['quality'].sort_values(ascending=False)
                perturbed_rankings.append(ranking)
                quality_scores_list.append(quality_df.set_index('model')['quality'])
            except Exception as e:
                if verbose:
                    print(f"    警告: 权重配置计算失败: {e}")
                continue
        
        # 计算稳定性指标
        stability = calculate_ranking_stability(perturbed_rankings)
        
        # 计算质量得分变异性
        if quality_scores_list:
            quality_matrix = pd.concat(quality_scores_list, axis=1)
            quality_std = quality_matrix.std(axis=1).mean()
            quality_cv = (quality_matrix.std(axis=1) / quality_matrix.mean(axis=1).abs()).mean()
        else:
            quality_std = 0.0
            quality_cv = 0.0
        
        results['perturbation_results'][perturbation_level] = {
            'n_samples': len(perturbed_rankings),
            'stability': stability,
            'quality_std': quality_std,
            'quality_cv': quality_cv,
            'rankings': perturbed_rankings[:10]  # 保存前10个用于可视化
        }
        
        if verbose:
            print(f"    样本数: {len(perturbed_rankings)}")
            print(f"    Spearman相关性: {stability['spearman_mean']:.3f}")
            print(f"    Kendall相关性: {stability['kendall_mean']:.3f}")
            print(f"    Top-3稳定性: {stability['top3_stability']:.3f}")
            print(f"    质量得分标准差: {quality_std:.4f}")
            print(f"    质量得分变异系数: {quality_cv:.4f}")
    
    # 保存结果
    results['base_ranking'] = base_ranking
    results['base_quality_df'] = base_quality_df
    
    return results


def run_global_sensitivity_analysis(quality_data: Dict[str, pd.DataFrame],
                                   output_dir: Path,
                                   verbose: bool = True) -> Dict:
    """运行全局权重敏感性分析"""
    if verbose:
        print(f"\n全局权重敏感性分析")
        print("=" * 60)
    
    # 生成权重网格
    weight_configs = generate_weight_grid(ALL_TASKS, n_points=WEIGHT_GRID_POINTS)
    
    if verbose:
        print(f"生成权重配置: {len(weight_configs)} 个")
    
    # 计算所有配置的结果
    all_rankings = []
    all_quality_scores = []
    weight_config_records = []
    
    for i, weights in enumerate(weight_configs):
        try:
            quality_df, _, _ = aggregate_quality_scores(
                quality_data, weights, gamma=0.5, verbose=False
            )
            ranking = quality_df.set_index('model')['quality'].sort_values(ascending=False)
            all_rankings.append(ranking)
            all_quality_scores.append(quality_df.set_index('model')['quality'])
            
            # 记录权重配置
            weight_record = weights.copy()
            weight_record['config_id'] = i
            weight_config_records.append(weight_record)
            
        except Exception as e:
            if verbose and i < 10:  # 只显示前10个错误
                print(f"    警告: 配置 {i} 计算失败: {e}")
            continue
    
    if verbose:
        print(f"成功计算: {len(all_rankings)} 个配置")
    
    # 分析结果
    results = {
        'n_configs': len(all_rankings),
        'weight_configs': pd.DataFrame(weight_config_records),
        'global_stability': calculate_ranking_stability(all_rankings),
        'rankings_sample': all_rankings[:20],  # 保存样本用于可视化
        'quality_scores_sample': all_quality_scores[:20]
    }
    
    # 计算权重-性能关系
    if len(all_quality_scores) > 10:
        quality_matrix = pd.concat(all_quality_scores, axis=1)
        results['quality_variance_by_model'] = quality_matrix.var(axis=1).sort_values(ascending=False)
        results['quality_mean_by_model'] = quality_matrix.mean(axis=1).sort_values(ascending=False)
    
    if verbose:
        stability = results['global_stability']
        print(f"全局稳定性指标:")
        print(f"  Spearman相关性: {stability['spearman_mean']:.3f}")
        print(f"  Kendall相关性: {stability['kendall_mean']:.3f}")
        print(f"  Top-3稳定性: {stability['top3_stability']:.3f}")
    
    return results
# ============================================================================
# 可视化函数
# ============================================================================

def plot_perturbation_stability(results: Dict, output_dir: Path):
    """绘制扰动稳定性图表"""
    perturbation_levels = list(results['perturbation_results'].keys())
    
    # 提取指标
    spearman_scores = [results['perturbation_results'][level]['stability']['spearman_mean'] 
                      for level in perturbation_levels]
    kendall_scores = [results['perturbation_results'][level]['stability']['kendall_mean'] 
                     for level in perturbation_levels]
    top3_stability = [results['perturbation_results'][level]['stability']['top3_stability'] 
                     for level in perturbation_levels]
    quality_cv = [results['perturbation_results'][level]['quality_cv'] 
                 for level in perturbation_levels]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. 排名相关性
    ax1.plot(perturbation_levels, spearman_scores, 'o-', label='Spearman', linewidth=2, markersize=8)
    ax1.plot(perturbation_levels, kendall_scores, 's-', label='Kendall', linewidth=2, markersize=8)
    ax1.set_xlabel('扰动幅度', fontweight='bold')
    ax1.set_ylabel('排名相关性', fontweight='bold')
    ax1.set_title('排名稳定性 vs 权重扰动', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1)
    
    # 2. Top-3稳定性
    ax2.plot(perturbation_levels, top3_stability, 'o-', color='green', linewidth=2, markersize=8)
    ax2.set_xlabel('扰动幅度', fontweight='bold')
    ax2.set_ylabel('Top-3稳定性', fontweight='bold')
    ax2.set_title('Top-3排名稳定性', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1)
    
    # 3. 质量得分变异性
    ax3.plot(perturbation_levels, quality_cv, 'o-', color='red', linewidth=2, markersize=8)
    ax3.set_xlabel('扰动幅度', fontweight='bold')
    ax3.set_ylabel('质量得分变异系数', fontweight='bold')
    ax3.set_title('质量得分变异性', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. 综合稳定性指标
    combined_stability = [(s + k + t) / 3 for s, k, t in zip(spearman_scores, kendall_scores, top3_stability)]
    ax4.plot(perturbation_levels, combined_stability, 'o-', color='purple', linewidth=2, markersize=8)
    ax4.set_xlabel('扰动幅度', fontweight='bold')
    ax4.set_ylabel('综合稳定性', fontweight='bold')
    ax4.set_title('综合稳定性指标', fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'perturbation_stability.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 扰动稳定性图已保存: perturbation_stability.png")


def plot_ranking_heatmap(results: Dict, output_dir: Path):
    """绘制排名变化热力图"""
    base_ranking = results['base_ranking']
    
    # 选择最大扰动级别的结果
    max_perturbation = max(results['perturbation_results'].keys())
    perturbed_rankings = results['perturbation_results'][max_perturbation]['rankings']
    
    if not perturbed_rankings:
        return
    
    # 构建排名矩阵
    models = base_ranking.index[:10]  # 取前10个模型
    ranking_matrix = []
    
    # 基准排名
    base_ranks = {model: i+1 for i, model in enumerate(base_ranking.index)}
    ranking_matrix.append([base_ranks.get(model, len(models)+1) for model in models])
    
    # 扰动排名
    for ranking in perturbed_rankings[:10]:  # 取前10个扰动结果
        ranks = {model: i+1 for i, model in enumerate(ranking.index)}
        ranking_matrix.append([ranks.get(model, len(models)+1) for model in models])
    
    ranking_df = pd.DataFrame(ranking_matrix, 
                             columns=[f"{model[:15]}..." if len(model) > 15 else model for model in models],
                             index=['基准'] + [f'扰动{i+1}' for i in range(len(ranking_matrix)-1)])
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    sns.heatmap(ranking_df, annot=True, fmt='d', cmap='RdYlGn_r', 
                cbar_kws={'label': '排名'}, ax=ax)
    
    ax.set_title(f'模型排名变化热力图 (扰动幅度: {max_perturbation:.1%})', 
                 fontweight='bold', pad=20)
    ax.set_xlabel('模型', fontweight='bold')
    ax.set_ylabel('权重配置', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'ranking_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 排名热力图已保存: ranking_heatmap.png")


def plot_weight_sensitivity_radar(results: Dict, output_dir: Path):
    """绘制权重敏感性雷达图"""
    if 'quality_variance_by_model' not in results:
        return
    
    # 选择变异性最高的前8个模型
    top_variable_models = results['quality_variance_by_model'].head(8)
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # 角度设置
    angles = np.linspace(0, 2 * np.pi, len(top_variable_models), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))  # 闭合
    
    # 归一化方差值
    values = top_variable_models.values
    values_norm = (values - values.min()) / (values.max() - values.min()) if values.max() > values.min() else values
    values_norm = np.concatenate((values_norm, [values_norm[0]]))  # 闭合
    
    # 绘制雷达图
    ax.plot(angles, values_norm, 'o-', linewidth=2, markersize=8, color='red', alpha=0.7)
    ax.fill(angles, values_norm, alpha=0.25, color='red')
    
    # 设置标签
    model_labels = [f"{model[:10]}..." if len(model) > 10 else model for model in top_variable_models.index]
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(model_labels)
    ax.set_ylim(0, 1)
    ax.set_title('模型权重敏感性雷达图\n(质量得分方差)', fontweight='bold', pad=30)
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'weight_sensitivity_radar.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 权重敏感性雷达图已保存: weight_sensitivity_radar.png")


def generate_sensitivity_report(perturbation_results: Dict, 
                               global_results: Dict,
                               output_dir: Path):
    """生成敏感性分析报告"""
    report_content = f"""# 权重敏感性分析报告

## 分析概述

本报告分析了权重参数变化对GenAI模型质效比评估结果的影响，包括局部扰动分析和全局敏感性分析。

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. 局部扰动分析

### 1.1 基准配置
- **配置名称**: {perturbation_results['base_config']}
- **基准Top-5模型**:
"""
    
    # 添加基准排名
    for i, (model, score) in enumerate(perturbation_results['base_ranking'].head(5).items(), 1):
        report_content += f"  {i}. {model}: {score:.4f}\n"
    
    report_content += "\n### 1.2 扰动稳定性结果\n\n"
    report_content += "| 扰动幅度 | Spearman相关性 | Kendall相关性 | Top-3稳定性 | 质量变异系数 |\n"
    report_content += "|---------|---------------|--------------|------------|-------------|\n"
    
    for level, result in perturbation_results['perturbation_results'].items():
        stability = result['stability']
        report_content += f"| {level:.1%} | {stability['spearman_mean']:.3f} | {stability['kendall_mean']:.3f} | {stability['top3_stability']:.3f} | {result['quality_cv']:.4f} |\n"
    
    report_content += f"""

### 1.3 稳定性评估

基于扰动分析结果：

- **高稳定性** (相关性 > 0.8): 权重变化对排名影响较小，结果可靠
- **中等稳定性** (0.6 < 相关性 ≤ 0.8): 权重变化有一定影响，需要谨慎解释
- **低稳定性** (相关性 ≤ 0.6): 权重变化显著影响结果，需要进一步验证

## 2. 全局敏感性分析

### 2.1 分析范围
- **权重配置数量**: {global_results['n_configs']}
- **网格点数**: {WEIGHT_GRID_POINTS} (每维度)

### 2.2 全局稳定性指标
- **Spearman相关性**: {global_results['global_stability']['spearman_mean']:.3f}
- **Kendall相关性**: {global_results['global_stability']['kendall_mean']:.3f}
- **Top-3稳定性**: {global_results['global_stability']['top3_stability']:.3f}

## 3. 主要发现

### 3.1 权重敏感性
"""
    
    # 分析最敏感的模型
    if 'quality_variance_by_model' in global_results:
        top_sensitive = global_results['quality_variance_by_model'].head(3)
        report_content += "**权重敏感性最高的模型**:\n"
        for i, (model, variance) in enumerate(top_sensitive.items(), 1):
            report_content += f"{i}. {model}: 方差 = {variance:.4f}\n"
        
        report_content += "\n**权重敏感性最低的模型**:\n"
        bottom_sensitive = global_results['quality_variance_by_model'].tail(3)
        for i, (model, variance) in enumerate(bottom_sensitive.items(), 1):
            report_content += f"{i}. {model}: 方差 = {variance:.4f}\n"
    
    report_content += f"""

### 3.2 建议

1. **权重设置建议**: 基于稳定性分析，推荐使用相对稳定的权重配置
2. **结果解释**: 对于权重敏感性高的模型，需要更谨慎地解释排名结果
3. **进一步分析**: 可以针对特定应用场景优化权重配置

## 4. 技术细节

### 4.1 分析方法
- **扰动方法**: 正态分布随机扰动
- **稳定性指标**: Spearman相关系数、Kendall τ系数、Top-K稳定性
- **全局分析**: 网格搜索 + 随机采样

### 4.2 数据来源
- **PCA得分数据**: 基于已保存的缓存文件
- **任务覆盖**: {', '.join(ALL_TASKS)}
- **模型数量**: 约{len(perturbation_results['base_ranking'])}个

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 保存报告
    report_file = output_dir / 'SENSITIVITY_ANALYSIS_REPORT.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✓ 敏感性分析报告已保存: {report_file.name}")
# ============================================================================
# 主执行函数
# ============================================================================

def main():
    """主函数：执行完整的敏感性分析"""
    # 创建输出目录
    SENSITIVITY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("GenAI模型质效比评估 - 权重敏感性分析")
    print("=" * 80)
    print(f"输出目录: {SENSITIVITY_OUTPUT_DIR}")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 1. 加载PCA得分数据
    print("\n步骤1: 加载PCA得分数据")
    print("-" * 60)
    
    cache_file = project_root / 'analysis' / 'qe_research' / 'results' / 'mixed_task_analysis' / 'task_02' / 'balanced' / 'pca_scores_all_tasks.csv'
    
    try:
        pca_scores = load_pca_scores_from_cache(cache_file)
        quality_data = simulate_quality_data_from_pca(pca_scores)
        print(f"✓ 成功加载 {len(quality_data)} 个任务的数据")
    except Exception as e:
        print(f"✗ 数据加载失败: {e}")
        return
    
    # 2. 局部扰动分析
    print("\n步骤2: 局部扰动分析")
    print("-" * 60)
    
    perturbation_results = {}
    for config_name in ['balanced', 'objective', 'subjective']:
        print(f"\n分析配置: {config_name}")
        try:
            result = run_perturbation_analysis(
                quality_data, config_name, SENSITIVITY_OUTPUT_DIR, verbose=True
            )
            perturbation_results[config_name] = result
        except Exception as e:
            print(f"✗ 配置 {config_name} 分析失败: {e}")
            continue
    
    # 3. 全局敏感性分析
    print("\n步骤3: 全局敏感性分析")
    print("-" * 60)
    
    try:
        global_results = run_global_sensitivity_analysis(
            quality_data, SENSITIVITY_OUTPUT_DIR, verbose=True
        )
    except Exception as e:
        print(f"✗ 全局分析失败: {e}")
        global_results = {}
    
    # 4. 生成可视化
    print("\n步骤4: 生成可视化")
    print("-" * 60)
    
    for config_name, result in perturbation_results.items():
        config_output_dir = SENSITIVITY_OUTPUT_DIR / config_name
        config_output_dir.mkdir(exist_ok=True)
        
        try:
            plot_perturbation_stability(result, config_output_dir)
            plot_ranking_heatmap(result, config_output_dir)
        except Exception as e:
            print(f"✗ 配置 {config_name} 可视化失败: {e}")
    
    if global_results:
        try:
            plot_weight_sensitivity_radar(global_results, SENSITIVITY_OUTPUT_DIR)
        except Exception as e:
            print(f"✗ 全局可视化失败: {e}")
    
    # 5. 生成报告
    print("\n步骤5: 生成分析报告")
    print("-" * 60)
    
    for config_name, result in perturbation_results.items():
        config_output_dir = SENSITIVITY_OUTPUT_DIR / config_name
        try:
            generate_sensitivity_report(result, global_results, config_output_dir)
        except Exception as e:
            print(f"✗ 配置 {config_name} 报告生成失败: {e}")
    
    # 6. 总结
    print("\n" + "=" * 80)
    print("敏感性分析完成！")
    print("=" * 80)
    print(f"结果保存在: {SENSITIVITY_OUTPUT_DIR}")
    print("\n主要输出文件:")
    print("- perturbation_stability.png: 扰动稳定性图表")
    print("- ranking_heatmap.png: 排名变化热力图")
    print("- weight_sensitivity_radar.png: 权重敏感性雷达图")
    print("- SENSITIVITY_ANALYSIS_REPORT.md: 详细分析报告")
    print("=" * 80)


if __name__ == '__main__':
    main()